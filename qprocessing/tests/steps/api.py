import os
import time
import zipfile
from io import BytesIO
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from behave import given, then, when
from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse
from guardian.shortcuts import assign_perm
from qgis.core import QgsVectorLayer, QgsWkbTypes

from core.models import G3WSpatialRefSys, Group as CoreGroup
from core.utils.qgisapi import get_qgs_project
from qdjango.utils.data import QgisProject
from qprocessing.models import QProcessingInputUpload, QProcessingProject
from qprocessing.tests.base import (
    CURRENT_PATH, MODEL_FILE_BUFFER, MODEL_FILE_POINTSPOLYGONS, QGS_PROJECT_QPROCESSING_FILE,
    TEST_BASE_PATH, UPLOAD_FILE_LINESTRING, UPLOAD_FILE_POINT, UPLOAD_FILE_POLYGON,
    UPLOAD_FILE_SHP_POLYGON_ZIP, UPLOAD_FILE_SHP_POLYGON_ZIP_FAIL,
)
from usersmanage.tests.utils import setup_testing_user


POINT_LAYER = 'qprocessing_2f527e7f_4c58_485a_a8b3_6370801c37ae'
POLYGON_LAYER = 'poligono2_ca3f4152_353f_471b_a7dc_5fd1b1b0bffe'
FIELDS_LAYER = 'points_aae45d3d_4911_445f_a6de_0e4ab724cd1b'


@given('a processing project and an authenticated administrator')
def processing_project(context):
    call_command('loaddata', 'BaseLayer.json', 'G3WMapControls.json',
                 'G3WSpatialRefSys.json', 'G3WGeneralDataSuite.json', verbosity=0)
    setup_testing_user(context.test)
    group = CoreGroup.objects.create(
        name='QProcessing', title='QProcessing', header_logo_img='',
        srid=G3WSpatialRefSys.objects.get(auth_srid=3857),
    )
    with open(os.path.join(CURRENT_PATH, TEST_BASE_PATH, QGS_PROJECT_QPROCESSING_FILE), 'r') as project_file:
        project = QgisProject(File(project_file))
        project.title = 'QProcessing Test Project'
        project.group = group
        project.save()
    context.project = project.instance
    context.models = {}
    for name, model_file in [('buffer', MODEL_FILE_BUFFER), ('points', MODEL_FILE_POINTSPOLYGONS)]:
        with open(os.path.join(CURRENT_PATH, TEST_BASE_PATH, model_file), 'r') as source:
            model = QProcessingProject(model=File(source, name=os.path.basename(model_file)))
            model.save()
        model.projects.add(context.project)
        context.models[name] = model
    assert context.test.client.login(
        username=context.test.test_admin1.username, password=context.test.test_admin1.username,
    )


@when('fields are requested for datatype "{datatype}"')
def request_fields(context, datatype):
    url = reverse('qprocessing-action-fields', args=[context.project.pk, FIELDS_LAYER])
    if datatype != 'omitted':
        url += f'?datatype={datatype}'
    context.response = context.test.client.get(url)


@then('the response contains the {fields} fields')
def check_fields(context, fields):
    project = get_qgs_project(context.project.qgis_file.path)
    layer = project.mapLayer(FIELDS_LAYER)
    expected = {
        'all': [{'key': f.displayName(), 'value': f.name()} for f in layer.fields()],
        'string': [{'key': 'name', 'value': 'name'}],
        'numeric': [{'key': 'fid', 'value': 'fid'}, {'key': 'value', 'value': 'value'}],
        'datetime': [],
    }
    assert context.response.status_code == 200
    assert context.response.json() == {'result': True, 'fields': expected[fields]}


@when('fields are requested for {request}')
def request_invalid_fields(context, request):
    layer_id = 'no_layer_id' if request == 'a missing layer' else FIELDS_LAYER
    url = reverse('qprocessing-action-fields', args=[context.project.pk, layer_id])
    if request == 'an empty datatype':
        url += '?datatype='
    elif request == 'an unknown datatype':
        url += '?datatype=wrong'
    context.request_kind = request
    context.response = context.test.client.get(url)


@then('the response has status {status:d} and the expected error')
def check_fields_error(context, status):
    errors = {
        'a missing layer': {'code': 'servererror', 'message': 'A error server is occured!',
                            'data': 'Layer matching query does not exist.'},
        'an empty datatype': {'code': 'validation', 'message': 'Data are not correct or insufficent!',
                              'data': ['For datatype the admissible values are: string, numeric, datetime, any']},
        'an unknown datatype': {'code': 'validation', 'message': 'Data are not correct or insufficent!',
                                'data': ["'wrong' is not a valid datatype, the admissible values are: string, numeric, datetime, any"]},
    }
    assert context.response.status_code == status
    assert context.response.json() == {'result': False, 'error': errors[context.request_kind]}


@given('model execution is {mode}')
def execution_mode(context, mode):
    context.async_run = mode == 'asynchronous'
    override = override_settings(QPROCESSING_ASYNC_RUN=context.async_run)
    override.enable()
    context.add_cleanup(override.disable)


def run_and_download(context, model, inputs, output):
    url = reverse('qprocessing-run-model', args=[context.models[model].pk, context.project.pk])
    response = context.test.client.post(
        url, data={'inputs': inputs, 'outputs': {output[0]: output[1]}}, content_type='application/json',
    )
    assert response.status_code == 200
    result = response.json()
    if context.async_run:
        time.sleep(1)
        response = context.test.client.get(reverse('qprocessing-infotask', args=[result['task_id']]))
        assert response.status_code == 200
        result = response.json()
        assert result['status'] == 'complete'
        assert result['exception'] == ''
        assert result['progress'] == 100
        download_url = result['task_result'][output[0]]
    else:
        assert result['result']
        download_url = result['data'][output[0]]
    response = context.test.client.get(download_url)
    assert response.status_code == 200
    if not context.async_run:
        assert response.headers['Content-Type'] == output[2]
        assert output[3] in response.headers['Content-Disposition']
    return response.content


@when('the buffer, point-in-polygon and selected-feature models run')
def run_models(context):
    context.buffer_result = run_and_download(
        context, 'buffer', {'buffer_layer2': POINT_LAYER, 'dissolve': 'False', 'distance': '100000'},
        ('native:buffer_1:Buffer results', 'shp', 'application/x-zip-compressed', 'buffer-results'),
    )
    context.point_results = []
    for polygon in (POLYGON_LAYER, f'{POLYGON_LAYER}:1'):
        context.point_results.append(run_and_download(
            context, 'points', {'points_layer': POINT_LAYER, 'polygon_layer': polygon, 'weight_fileds': 'value'},
            ('native:countpointsinpolygon_1:Points in polygons', 'geojson', 'application/json', 'points-in-polygons'),
        ))


@then('their downloaded results have the expected geometries and attributes')
def check_model_results(context):
    with TemporaryDirectory() as directory:
        with zipfile.ZipFile(BytesIO(context.buffer_result)) as archive:
            archive.extractall(directory)
        layer = QgsVectorLayer(directory)
        assert layer.isValid()
        assert [field.name() for field in layer.fields()] == ['fid', 'name', 'value']
        assert QgsWkbTypes.geometryDisplayString(layer.geometryType()) == 'Polygon'
        for content, count in zip(context.point_results, (4, 1)):
            path = os.path.join(directory, f'result-{count}.geojson')
            with open(path, 'wb') as output:
                output.write(content)
            layer = QgsVectorLayer(path)
            assert layer.isValid()
            assert layer.featureCount() == count
            assert QgsWkbTypes.geometryDisplayString(layer.geometryType()) == 'Polygon'


@when('a viewer tries to run the buffer model')
def viewer_runs(context):
    context.run_url = reverse('qprocessing-run-model', args=[context.models['buffer'].pk, context.project.pk])
    context.buffer_data = {
        'inputs': {'buffer_layer2': POINT_LAYER, 'dissolve': 'False', 'distance': '100000'},
        'outputs': {'native:buffer_1:Buffer results': 'shp'},
    }
    response = context.test.client.post(context.run_url, data=context.buffer_data, content_type='application/json')
    assert response.status_code == 200
    context.test.client.logout()
    viewer = context.test.test_viewer1
    assert context.test.client.login(username=viewer.username, password=viewer.username)
    context.response = context.test.client.post(
        context.run_url, data=context.buffer_data, content_type='application/json',
    )


@then('the request is forbidden')
def forbidden(context):
    assert context.response.status_code == 403


@when('the viewer receives project and model permissions')
def grant_permissions(context):
    viewer = context.test.test_viewer1
    assign_perm('view_project', viewer, context.project)
    assign_perm('run_model', viewer, context.models['buffer'])
    context.response = context.test.client.post(
        context.run_url, data=context.buffer_data, content_type='application/json',
    )


@then('the viewer can run the buffer model')
def allowed(context):
    assert context.response.status_code == 200


@given('task progress is represented by {representation}')
def task_progress(context, representation):
    state = SimpleNamespace(signal_name='executing', exception_line='')
    values = {
        'count': {'total': 100, 'progress_count': 25},
        'tuple': {'total': 100, 'progress_info': (25, None)},
        'missing': {'total': 0, 'progress_count': None},
    }
    context.task = SimpleNamespace(state=state, **values[representation])


@when('task progress is requested')
def request_progress(context):
    url = reverse('qprocessing-infotask', args=['00000000-0000-0000-0000-000000000001'])
    with patch('qprocessing.api.views.models.HUEY.result', return_value=None), \
            patch('qprocessing.api.views.models.TaskModel.objects.get', return_value=context.task):
        context.response = context.test.client.get(url)


@then('the reported progress is {progress:d}')
def check_progress(context, progress):
    assert context.response.status_code == 200
    assert context.response.json()['progress'] == progress


@when('a {geometry} input is uploaded')
def upload_input(context, geometry):
    files = {
        'point': UPLOAD_FILE_POINT,
        'polygon': UPLOAD_FILE_POLYGON,
        'line': UPLOAD_FILE_LINESTRING,
        'shapefile': UPLOAD_FILE_SHP_POLYGON_ZIP,
        'incomplete shapefile': UPLOAD_FILE_SHP_POLYGON_ZIP_FAIL,
    }
    context.geometry = geometry
    context.upload_name = os.path.basename(files[geometry])
    with open(os.path.join(CURRENT_PATH, TEST_BASE_PATH, files[geometry]), 'rb') as source:
        upload = SimpleUploadedFile(context.upload_name, source.read(), content_type='application/json')
    url = reverse('qprocessing-action-input-upload', args=[context.models['buffer'].pk, context.project.pk, 'buffer_layer2'])
    context.response = context.test.client.post(url, data={'file': [upload]})


@then('the input is stored successfully')
def check_upload(context):
    assert context.response.status_code == 200
    result = context.response.json()
    assert result['result']
    upload = QProcessingInputUpload.objects.get(uuid=result['data']['file'])
    upload_dir = os.path.join(settings.QPROCESSING_OUTPUT_PATH, str(context.test.test_admin1.pk), 'uploads')
    if context.geometry == 'shapefile':
        assert upload.name == f'{os.path.splitext(context.upload_name)[0]}.shp'
        for ext in settings.QPROCESSING_INPUT_SHP_EXTS:
            assert os.path.exists(os.path.join(upload_dir, f'{os.path.splitext(upload.name)[0]}.{ext}'))
    else:
        stem, extension = os.path.splitext(upload.name)
        unsuffixed = f'{"_".join(stem.split("_")[:-1])}{extension}'
        assert upload.name == context.upload_name or unsuffixed == context.upload_name
        assert os.path.exists(os.path.join(upload_dir, upload.name))


@then('the upload is rejected with the expected error')
def check_upload_error(context):
    assert context.response.status_code == 400
    result = context.response.json()
    assert not result['result']
    if context.geometry == 'line':
        assert 'must have a geometry type of: point,polygon' in result['error']
    else:
        assert result['error'] == 'Zip file for shape files is not correct. Missing the following files type: prj, shx'
