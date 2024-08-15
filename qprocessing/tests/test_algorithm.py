# coding=utf-8
"""" testign module for QGIS Processign API
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-23'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from django.test import TestCase
from qprocessing.utils.data import QProcessingModel
from .base import CURRENT_PATH, TEST_BASE_PATH, TestQProcessingBase

from qgis.core import QgsProcessingContext, QgsProcessingFeedback, QgsProject
import os

class TestQprocessingAlgorithm(TestQProcessingBase):

    def test_run(self):
        """
        Test running QGIS processing running
        """
        qpm = QProcessingModel(str(self.model_file))
        prj = QgsProject()
        loaded = prj.read(self.qgis_file)

        self.assertTrue(loaded)
        self.assertTrue(prj.mapLayer('buildings_7783caca_93e9_4c17_9770_1fd8e82f7109').isValid())

        #ingresso1 = './buildings.geojson'
        ingresso1 = os.path.join(CURRENT_PATH, TEST_BASE_PATH, 'project_data/buildings.geojson')
        result_path = os.path.join(CURRENT_PATH, TEST_BASE_PATH, 'processing_result', 'out.shp')

        params = {
            'buffer_distance': 1000,
            'ingresso1': ingresso1,
            'layer_bufferd': result_path
        }

        ctx = QgsProcessingContext()
        ctf = QgsProcessingFeedback()
        ctx.setProject(prj)

        res = qpm.model.processAlgorithm(params, ctx, ctf)

        aspected_res = {'CHILD_INPUTS': {'native:buffer_1': {'DISSOLVE': False, 'DISTANCE': 1000, 'END_CAP_STYLE': 0, 'INPUT': '/home/walter/PycharmProjects/g3w_suite_qgis_api/plugins/g3w-admin-processing/qprocessing/tests/data/project_data/buildings.geojson', 'JOIN_STYLE': 0, 'MITER_LIMIT': None, 'OUTPUT': '/home/walter/PycharmProjects/g3w_suite_qgis_api/plugins/g3w-admin-processing/qprocessing/tests/data/processing_result/out.shp', 'SEGMENTS': None}}, 'CHILD_RESULTS': {'native:buffer_1': {'OUTPUT': '/home/walter/PycharmProjects/g3w_suite_qgis_api/plugins/g3w-admin-processing/qprocessing/tests/data/processing_result/out.shp'}}, 'layer_bufferd': '/home/walter/PycharmProjects/g3w_suite_qgis_api/plugins/g3w-admin-processing/qprocessing/tests/data/processing_result/out.shp'}

        self.assertEqual(res, aspected_res)