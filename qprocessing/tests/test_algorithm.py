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
from .base import CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE_1, QGS_PROJECT_FILE
from qgis.core import QgsProcessingContext, QgsProcessingFeedback, QgsProject
import os

class TestQprocessingAlgorithm(TestCase):

    databases = {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.model_file = os.path.join(CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE_1)
        cls.qgis_file = os.path.join(CURRENT_PATH, TEST_BASE_PATH, QGS_PROJECT_FILE)

    def test_run(self):

        qpm = QProcessingModel(str(self.model_file))
        prj = QgsProject()
        loaded = prj.read(self.qgis_file)

        self.assertTrue(loaded)
        self.assertTrue(prj.mapLayer('buildings_7783caca_93e9_4c17_9770_1fd8e82f7109').isValid())

        #ingresso1 = './buildings.geojson'
        ingresso1 = os.path.join(CURRENT_PATH, TEST_BASE_PATH, 'buildings.geojson')
        result_path = os.path.join(CURRENT_PATH, TEST_BASE_PATH, 'processing_result', 'out.shp')

        params = {'buffer_distance': 1000,
                  'ingresso1': ingresso1,
                  'layer_bufferd': result_path}

        print(params)

        ctx = QgsProcessingContext()
        ctf = QgsProcessingFeedback()

        print(prj)
        ctx.setProject(prj)

        res = qpm.model.processAlgorithm(params, ctx, ctf)

        print(res)
        print(ctf.textLog())