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
from qprocessing.models import QProcessingModel
from .base import CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE
import os

class TestQprocessingAlgorithm(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.model_file = os.path.join(CURRENT_PATH, TEST_BASE_PATH, MODEL_FILE)

    def test_run(self):

        qpm = QProcessingModel(str(qpp.model.file))