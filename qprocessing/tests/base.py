# coding=utf-8
"""" Base qprocessing test module

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-10'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

import os

CURRENT_PATH = os.path.dirname(__file__)
TEST_BASE_PATH = 'data/'
DATASOURCE_PATH = '{}/{}project_data'.format(CURRENT_PATH, TEST_BASE_PATH)
MODEL_FILE = 'models/test_buffer_all_inputs.model3'
MODEL_FILE_BUFFER = 'models/qbuffer.model3'
MODEL_FILE_POINTSPOLYGONS = 'models/qpointspolygons.model3'

QGS_PROJECT_FILE = 'test_qgis_328.qgs'
QGS_PROJECT_QPROCESSING_FILE = 'qprocessing_qprocessing.qgs'

# Upload file
UPLOAD_FILE_POINT = 'upload/point_to_upload.geojson'
UPLOAD_FILE_POLYGON = 'upload/polygon_to_upload.geojson'
UPLOAD_FILE_LINESTRING = 'upload/linestring_to_upload.geojson'
UPLOAD_FILE_SHP_POLYGON_ZIP = 'upload/shp_to_upload.zip'
UPLOAD_FILE_SHP_POLYGON_ZIP_FAIL = 'upload/fail_shp_to_upload.zip'
