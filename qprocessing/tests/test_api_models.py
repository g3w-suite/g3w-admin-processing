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
from .base import \
    TestQProcessingBase, \
    MODEL_FILE_BUFFER, \
    MODEL_FILE_POINTSPOLYGONS, \
    MODEL_FILE_INTERSECTIONS

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

        # Create QProcessingProject
        # --------------------------------------------

        # Create testing object and data
        with open(cls.model_file_buffer, 'r') as f:
            cls.qpp_buffer = QProcessingProject(model=File(f, name=MODEL_FILE_BUFFER.split('/')[1]))
            cls.qpp_buffer.save()

        cls.qpp_buffer.projects.add(cls.project.instance)

        with open(cls.model_file_ponintspolygons, 'r') as f:
            cls.qpp_pointspolygons = QProcessingProject(model=File(f, name=MODEL_FILE_POINTSPOLYGONS.split('/')[1]))
            cls.qpp_pointspolygons.save()

        cls.qpp_pointspolygons.projects.add(cls.project.instance)

        with open(cls.model_file_intersections, 'r') as f:
            cls.qpp_intesections = QProcessingProject(model=File(f, name=MODEL_FILE_INTERSECTIONS.split('/')[1]))
            cls.qpp_intesections.save()

        cls.qpp_intesections.projects.add(cls.project.instance)

        # Create API REST post data
        # --------------------------------------------

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

        cls.pointspolygons_post_data = {
            "inputs": {
                "points_layer": "qprocessing_2f527e7f_4c58_485a_a8b3_6370801c37ae",
                "polygon_layer": "poligono2_ca3f4152_353f_471b_a7dc_5fd1b1b0bffe",
                "weight_fileds": "value"
            },
            "outputs": {
                "native:countpointsinpolygon_1:Points in polygons":"geojson"
            }
        }

        cls.pointspolygons_features_post_data = {
            "inputs": {
                "points_layer": "qprocessing_2f527e7f_4c58_485a_a8b3_6370801c37ae",
                "polygon_layer": "poligono2_ca3f4152_353f_471b_a7dc_5fd1b1b0bffe:1",
                "weight_fileds": "value"
            },
            "outputs": {
                "native:countpointsinpolygon_1:Points in polygons": "geojson"
            }
        }



    def test_run_model(self):
        """
        Testing run models
        """


        url = reverse('qprocessing-run-model', args=[self.qpp_buffer.pk, self.project.instance.pk])

        # Login as admin01
        # ----------------------------------------------
        self.client.login(username=self.test_admin1.username, password=self.test_admin1.username)

        # Testing MODEL_FILE_BUFFER processing model
        #_____________________________________________
        res = self.client.post(url,data=self.buffer_post_data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        jres = json.loads(res.content)

        # Wait for processing result
        time.sleep(1)
        task_info_url = reverse('qprocessing-infotask', args=[jres['task_id']])

        res = self.client.get(task_info_url)
        self.assertEqual(res.status_code, 200)

        jres = json.loads(res.content)

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

        # Testing MODEL_FILE_POINTSPOLYGONS processing model
        #______________________________________________________
        url = reverse('qprocessing-run-model', args=[self.qpp_pointspolygons.pk, self.project.instance.pk])
        res = self.client.post(url, data=self.pointspolygons_post_data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        jres = json.loads(res.content)

        # Wait for processing result
        time.sleep(1)
        task_info_url = reverse('qprocessing-infotask', args=[jres['task_id']])

        res = self.client.get(task_info_url)
        self.assertEqual(res.status_code, 200)

        jres = json.loads(res.content)

        self.assertEqual(jres['status'], 'complete')
        self.assertEqual(jres['exception'], '')
        self.assertEqual(jres['progress'], 0)

        # Get file result file GeoJson
        res = self.client.get(jres['task_result']['native:countpointsinpolygon_1:Points in polygons'])
        self.assertTrue(res.status_code, 200)

        temp = QTemporaryDir()
        z.extractall(temp.path())
        result_file = f'{temp.path()}/result.geojson'
        with open(result_file, 'w') as f:
            f.write(res.content.decode())
        vl = QgsVectorLayer(result_file)
        self.assertTrue(vl.isValid())

        self.assertEqual(vl.featureCount(), 4)
        self.assertEqual(QgsWkbTypes.geometryDisplayString(vl.geometryType()), 'Polygon')

        res = self.client.post(url, data=self.pointspolygons_features_post_data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        jres = json.loads(res.content)

        # Wait for processing result
        time.sleep(1)
        task_info_url = reverse('qprocessing-infotask', args=[jres['task_id']])

        res = self.client.get(task_info_url)
        self.assertEqual(res.status_code, 200)

        jres = json.loads(res.content)

        self.assertEqual(jres['status'], 'complete')
        self.assertEqual(jres['exception'], '')
        self.assertEqual(jres['progress'], 0)

        # Get file result file GeoJson
        res = self.client.get(jres['task_result']['native:countpointsinpolygon_1:Points in polygons'])
        self.assertTrue(res.status_code, 200)

        temp = QTemporaryDir()
        z.extractall(temp.path())
        result_file = f'{temp.path()}/result.geojson'
        with open(result_file, 'w') as f:
            f.write(res.content.decode())
        vl = QgsVectorLayer(result_file)
        self.assertTrue(vl.isValid())

        self.assertEqual(vl.featureCount(), 1)
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
