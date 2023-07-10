# coding=utf-8
"""" Tests for API REST models
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-07-07'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from django.urls import reverse
from django.core.files import File
from qprocessing.models QProcessingProject
from .base import TestQProcessingBase
import json


class TestQProcessingModelsAPIREST(TestQProcessingBase):
    """
    Test for QProcessing API REST for running models
    """

    def test_run_model(self):
        """
        Testing run models
        """

        # Create QProcessingProject
        # --------------------------------------------
        qpp_buffer = QProcessingProject(model=File(self.model_file_buffer, 'r'))
        qpp_buffer.save()

        qpp_buffer.projects.add(File(self.qgis_qprocessing_file, 'r'))


