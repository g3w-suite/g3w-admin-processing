# coding=utf-8
"""" Tests for API REST models
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-07-07'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.core.files import File
from django.urls import reverse
from guardian.shortcuts import assign_perm
from qprocessing.models import QProcessingProject
from .base import TestQProcessingBase

from qgis.core import QgsVectorLayer, QgsWkbTypes
from qgis.PyQt.QtCore import QTemporaryDir

import json
import zipfile
import time
from io import BytesIO


class TestQProcessingModelsAPIREST(TestQProcessingBase):
    """
    Test for QProcessing API REST for running models
    """

    @classmethod
    def setUp(cls):

        super().setUp()

        # Create testing object and data
        with open(cls.model_file_buffer, 'r') as f:
            cls.qpp_buffer = QProcessingProject(model=File(f, name='qbuffer.model3'))
            cls.qpp_buffer.save()

        cls.qpp_buffer.projects.add(cls.project.instance)

        cls.buffer_post_data = {
            "inputs": {
                "buffer_layer2": "qprocessing_2f527e7f_4c58_485a_a8b3_6370801c37ae",
                "dissolve": "False",
                "distance": "100000"
            },
            "outputs": {
                "native:buffer_1:Buffer results": "shp"
            }
        }

    def test_run_model(self):
        """
        Testing run models
        """

        # Create QProcessingProject
        # --------------------------------------------


        url = reverse('qprocessing-run-model', args=[self.qpp_buffer.pk, self.project.instance.pk])

        # Login as admin01
        # ----------------------------------------------
        self.client.login(username=self.test_admin1.username, password=self.test_admin1.username)

        res = self.client.post(url,data=self.buffer_post_data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        jres = json.loads(res.content)

        # Wait for processing result
        time.sleep(1)
        task_info_url = reverse('qprocessing-infotask', args=[jres['task_id']])

        res = self.client.get(task_info_url)
        self.assertEqual(res.status_code, 200)

        jres = json.loads(res.content)

        print(jres)

        self.assertEqual(jres['status'], 'complete')
        self.assertEqual(jres['exception'], '')
        self.assertEqual(jres['progress'], 0)
        #self.assertEqual(jres['task_result'], {'native:buffer_1:Buffer results': '/qprocessing/api/download/gAAAAABkq-KAS1ExRItPOBL1Bi8CTBcl0INK6VL9ipYiQjy-48Fmo4r-2ERNDMa0paQcG_2vzFVFY11Lgmcl_qCN1qsykovFOQFf67CtJhK3OLvPU7HjqygYSX0rdJrwv0NE_xADuBdZ02orxcH_IxU24-bib8YMsw==/'})


        # Get file result file ZIP
        res = self.client.get(jres['task_result']['native:buffer_1:Buffer results'])

        self.assertTrue(res.status_code, 200)

        # For return shp:
        z = zipfile.ZipFile(BytesIO(res.content))
        temp = QTemporaryDir()
        z.extractall(temp.path())
        vl = QgsVectorLayer(temp.path())
        self.assertTrue(vl.isValid())

        fields = [f for f in vl.fields()]

        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0].name(), 'fid')
        self.assertEqual(fields[1].name(), 'name')
        self.assertEqual(fields[2].name(), 'value')

        self.assertEqual(QgsWkbTypes.geometryDisplayString(vl.geometryType()), 'Polygon')

        self.client.logout()

    def test_permissions(self):
        """
        Test permissions
        """

        url = reverse('qprocessing-run-model', args=[self.qpp_buffer.pk, self.project.instance.pk])

        # Login as admin01
        # ----------------------------------------------
        self.client.login(username=self.test_admin1.username, password=self.test_admin1.username)

        res = self.client.post(url, data=self.buffer_post_data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        jres = json.loads(res.content)

        self.client.logout()

        # Login as Viewer1
        # ----------------------------------------------
        self.client.login(username=self.test_viewer1.username, password=self.test_viewer1.username)

        res = self.client.post(url, data=self.buffer_post_data, content_type='application/json')
        self.assertEqual(res.status_code, 403)

        # Assign permission
        # Give permission to Viewer1
        assign_perm('view_project', self.test_viewer1, self.project.instance)
        assign_perm('run_model', self.test_viewer1, self.qpp_buffer)

        res = self.client.post(url, data=self.buffer_post_data, content_type='application/json')
        self.assertEqual(res.status_code, 200)

        self.client.logout()
