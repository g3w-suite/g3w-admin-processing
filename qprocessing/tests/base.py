# coding=utf-8
"""" Base qprocessing test module

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-10'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.test import TestCase, override_settings
from django.core.files import File
from core.models import G3WSpatialRefSys, Group as CoreGroup
from usersmanage.tests.utils import setup_testing_user
from qdjango.utils.data import QgisProject
import os

CURRENT_PATH = os.path.dirname(__file__)
TEST_BASE_PATH = 'data/'
DATASOURCE_PATH = '{}/{}project_data'.format(CURRENT_PATH, TEST_BASE_PATH)
MODEL_FILE = 'models/test_buffer_all_inputs.model3'
MODEL_FILE_ONLY_BUFFER = 'models/test_buffer_layer1.model3'

MODEL_FILE_BUFFER = 'models/qbuffer.model3'
MODEL_FILE_INTERSECTIONS = 'models/qintersection.model3'
MODEL_FILE_POINTSPOLYGONS = 'models/qpointspolygons.model3'

QGS_PROJECT_FILE = 'test_qgis_328.qgs'
QGS_PROJECT_QPROCESSING_FILE = 'qprocessing_qprocessing.qgs'

# Upload file
UPLOAD_FILE_POINT = 'upload/point_to_upload.geojson'
UPLOAD_FILE_POLYGON = 'upload/polygon_to_upload.geojson'
UPLOAD_FILE_LINESTRING = 'upload/linestring_to_upload.geojson'
UPLOAD_FILE_SHP_POLYGON_ZIP = 'upload/shp_to_upload.zip'
UPLOAD_FILE_SHP_POLYGON_ZIP_FAIL = 'upload/fail_shp_to_upload.zip'


@override_settings(
    CACHES={
        'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'some',
        }
    },
    DATASOURCE_PATH=DATASOURCE_PATH,
    LANGUAGE_CODE='en',
    LANGUAGES = (
        ('en', 'English'),
    ),
    HUEY={
        # Huey implementation to use.
        'huey_class': 'huey.RedisExpireHuey',
        'name': 'g3w-suite',
        'url': 'redis://localhost:6379/?db=0',
        'immediate': True,
        'consumer': {
            'workers': 1,
            'worker_type': 'process',
        }
    }
)
class TestQProcessingBase(TestCase):
    """
    Base class for QProcessing tests
    """

    fixtures = ['BaseLayer.json',
                'G3WMapControls.json',
                'G3WSpatialRefSys.json',
                'G3WGeneralDataSuite.json'
                ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        setup_testing_user(cls)

        cls.model_file = os.path.join(CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE)
        cls.qgis_file = os.path.join(CURRENT_PATH, TEST_BASE_PATH, QGS_PROJECT_FILE)

        cls.qgis_qprocessing_file = os.path.join(CURRENT_PATH, TEST_BASE_PATH, QGS_PROJECT_QPROCESSING_FILE)
        cls.model_file_buffer = os.path.join(CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE_BUFFER)
        cls.model_file_intersections = os.path.join(CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE_INTERSECTIONS)
        cls.model_file_ponintspolygons = os.path.join(CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE_POINTSPOLYGONS)

    @classmethod
    def setUp(cls):

        # main project group
        cls.project_group = CoreGroup(name='QProcessing', title='QProcessing', header_logo_img='',
                                      srid=G3WSpatialRefSys.objects.get(auth_srid=3857))
        cls.project_group.save()

        # Add projects to DB
        qgis_project_file = File(open(cls.qgis_qprocessing_file, 'r'))
        cls.project = QgisProject(qgis_project_file)
        cls.project.title = 'QProcessing Test Project'
        cls.project.group = cls.project_group
        cls.project.save()
