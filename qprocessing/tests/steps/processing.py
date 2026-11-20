import os
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from behave import given, then, when
from django.test import override_settings
from osgeo import gdal
from qgis.core import (
    QgsProcessingContext, QgsProcessingFeedback, QgsProcessingOutputRasterLayer,
    QgsProcessingOutputVectorLayer, QgsProcessingParameterRasterLayer,
    QgsProcessingParameters, QgsProject, QgsRasterLayer, QgsVectorLayer,
)

from qprocessing.tests.base import CURRENT_PATH, MODEL_FILE, QGS_PROJECT_FILE, TEST_BASE_PATH
from qprocessing.utils.data import QProcessingModel
from qprocessing.utils.formtypes import QProcessingFormTypeException, QProcessingFormTypeRasterLayer


@given('the buffer model')
def buffer_model(context):
    context.model = QProcessingModel(os.path.join(CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE))


@given('the buffer model and its QGIS project')
def buffer_model_and_project(context):
    buffer_model(context)
    context.project = QgsProject()
    assert context.project.read(os.path.join(CURRENT_PATH, TEST_BASE_PATH, QGS_PROJECT_FILE))
    assert context.project.mapLayer('buildings_7783caca_93e9_4c17_9770_1fd8e82f7109').isValid()
    context.add_cleanup(context.project.clear)


@when('the buffer model runs')
def run_buffer(context):
    directory = TemporaryDirectory()
    context.add_cleanup(directory.cleanup)
    context.input_path = os.path.join(CURRENT_PATH, TEST_BASE_PATH, 'project_data', 'buildings.geojson')
    context.output_path = os.path.join(directory.name, 'out.shp')
    processing_context = QgsProcessingContext()
    processing_context.setProject(context.project)
    context.result = context.model.model.processAlgorithm(
        {'buffer_distance': 1000, 'ingresso1': context.input_path, 'layer_bufferd': context.output_path},
        processing_context, QgsProcessingFeedback(),
    )


@then('QGIS returns the expected buffer result')
def check_buffer(context):
    assert context.result == {
        'CHILD_INPUTS': {'native:buffer_1': {
            'DISSOLVE': False, 'DISTANCE': 1000, 'END_CAP_STYLE': 0, 'INPUT': context.input_path,
            'JOIN_STYLE': 0, 'MITER_LIMIT': None, 'OUTPUT': context.output_path, 'SEGMENTS': None,
        }},
        'CHILD_RESULTS': {'native:buffer_1': {'OUTPUT': context.output_path}},
        'layer_bufferd': context.output_path,
    }


@when('its inputs and outputs are described')
def describe_model(context):
    context.description = context.model.render2dict()


@then('the description contains the expected inputs and output formats')
def check_description(context):
    assert context.description == {
        'name': 'test_buffer_all_inputs', 'display_name': 'test_buffer_all_inputs',
        'inputs': [
            {'name': 'buffer_distance', 'label': 'Buffer distance', 'type': 'float', 'qprocessing_type': 'distance', 'default': 1000.0, 'editable': True, 'validate': {'required': True}, 'input': {'type': 'range', 'options': {'default': 1000.0, 'values': [{'min': 10.0, 'max': 20000.0, 'step': 1}]}}},
            {'name': 'buffer_miter_limit', 'label': 'Buffer miter limit', 'type': 'integer', 'qprocessing_type': 'number', 'default': 2.0, 'editable': True, 'validate': {'required': True}, 'input': {'type': 'range', 'options': {'default': 2.0, 'values': [{'min': 0.0, 'max': 10.0, 'step': 1}]}}},
            {'name': 'buffer_segments', 'label': 'Buffer segments', 'type': 'integer', 'qprocessing_type': 'number', 'default': 2.0, 'editable': True, 'validate': {'required': True}, 'input': {'type': 'range', 'options': {'default': 2.0, 'values': [{'min': 0.0, 'max': 10.0, 'step': 1}]}}},
            {'name': 'ingresso1', 'label': 'Ingresso1', 'type': 'varchar', 'qprocessing_type': 'vector', 'default': None, 'editable': True, 'validate': {'required': True}, 'input': {'type': 'prjvectorlayer', 'options': {'datatypes': ['polygon'], 'values': []}}},
        ],
        'outputs': [
            {'name': 'layer_bufferd', 'label': 'Layer bufferd', 'qprocessing_type': 'outputVector', 'type': 'varchar', 'default': None, 'validate': {'required': True}, 'input': {'type': 'outputvectorlayer', 'options': {'values': [{'value': 'shp', 'key': 'Shapefile'}, {'value': 'geojson', 'key': 'GeoJSON'}, {'value': 'kml', 'key': 'KML'}, {'value': 'kmz', 'key': 'KMZ'}, {'value': 'csv', 'key': 'CSV'}]}}},
        ],
    }


@given('distinct raster and vector output formats')
def output_formats(context):
    context.raster_formats = [{'value': 'tiff', 'key': 'TIFF'}]
    context.vector_formats = [{'value': 'geojson', 'key': 'GeoJSON'}]


@when('raster and vector model outputs are described')
def describe_outputs(context):
    model = QProcessingModel.__new__(QProcessingModel)
    model.model = SimpleNamespace(outputDefinitions=lambda: [
        QgsProcessingOutputRasterLayer('raster'), QgsProcessingOutputVectorLayer('vector'),
    ])
    with override_settings(QPROCESSING_OUTPUT_RASTER_FORMATS=context.raster_formats,
                           QPROCESSING_OUTPUT_VECTOR_FORMATS=context.vector_formats):
        model._get_outputs()
    context.outputs = model.outputs


@then('each output offers its configured formats')
def check_outputs(context):
    assert context.outputs['raster']['input'] == {
        'type': 'outputrasterlayer', 'options': {'values': context.raster_formats},
    }
    assert context.outputs['vector']['input']['options']['values'] == context.vector_formats


@given('a valid raster layer in a QGIS project')
def raster_project(context):
    directory = TemporaryDirectory()
    context.add_cleanup(directory.cleanup)
    path = os.path.join(directory.name, 'input.tif')
    dataset = gdal.GetDriverByName('GTiff').Create(path, 2, 2, 1, gdal.GDT_Byte)
    dataset.SetGeoTransform((0, 1, 0, 0, 0, -1))
    dataset = None
    context.layer = QgsRasterLayer(path, 'raster', 'gdal')
    assert context.layer.isValid()
    context.project = QgsProject()
    context.add_cleanup(context.project.clear)
    context.project.addMapLayer(context.layer)


@when('the raster layer is selected for processing')
def select_raster(context):
    context.parameter = QProcessingFormTypeRasterLayer.update_model_params(context.project, context.layer.id())


@then('QGIS resolves the selected raster layer')
def check_raster(context):
    processing_context = QgsProcessingContext()
    processing_context.setProject(context.project)
    resolved = QgsProcessingParameters.parameterAsRasterLayer(
        QgsProcessingParameterRasterLayer('input'), {'input': context.parameter}, processing_context,
    )
    assert resolved == context.layer


@when('a {layer} layer is selected for raster processing')
def select_invalid_raster(context, layer):
    if layer == 'vector':
        vector = QgsVectorLayer('Point', 'vector', 'memory')
        context.project.addMapLayer(vector)
        layer_id = vector.id()
    else:
        layer_id = 'missing'
    try:
        QProcessingFormTypeRasterLayer.update_model_params(context.project, layer_id)
    except QProcessingFormTypeException as error:
        context.raster_error = error


@then('the raster input is rejected')
def check_raster_error(context):
    assert hasattr(context, 'raster_error')
