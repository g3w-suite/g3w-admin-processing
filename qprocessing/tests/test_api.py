# coding=utf-8
"""" Test API (REST and non-REST) of qprocessing g3w-suite plugins.

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-10'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.test import TestCase
from qprocessing.utils.data import QProcessingModel
from .base import CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE


import os



class TestQprocessingUtils(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.model_file = os.path.join(CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE)

    def test_data(self):
        """
        Test qprocessing.utils.data module classes and functions
        """

        # Testing QProcessingModel
        # -------------------------------------------------

        qpm = QProcessingModel(self.model_file)

        self.assertEqual(qpm.render2json(),
                {
                   "name":"MODEL PROCESSING TEST",
                   "display_name":"MODEL PROCESSING TEST",
                   "inputs":[
                      {
                         "name":"rivers",
                         "type":"vector"
                      }
                   ],
                   "outputs":[
                      {
                         "name":"native:buffer_1:Buffered river",
                         "description":"Buffered river",
                         "type":"outputVector"
                      },
                      {
                         "name":"native:rasterize_1:Rasterized map",
                         "description":"Rasterized map",
                         "type":"outputRaster"
                      }
                   ]
                }
        )


