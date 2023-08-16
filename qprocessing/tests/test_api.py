# coding=utf-8
"""" Test API (REST and non-REST) of qprocessing g3w-suite plugins.

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-10'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.urls import reverse
from core.utils.qgisapi import get_qgs_project
from qprocessing.utils.data import QProcessingModel
from .base import TestQProcessingBase
import json



class TestQProcessingUtils(TestQProcessingBase):


    def test_data(self):
        """
        Test qprocessing.utils.data module classes and functions
        """

        # Testing QProcessingModel
        # =========================================================

        # Testing render2dict
        # ------------------------------------------------

        qpm = QProcessingModel(self.model_file)

        # Testing render2dict
        aspected_dict = {'name': 'test_buffer_all_inputs', 'display_name': 'test_buffer_all_inputs', 'inputs': [{'name': 'buffer_distance', 'label': 'Buffer distance', 'type': 'float', 'qprocessing_type': 'distance', 'default': 1000.0, 'editable': True, 'validate': {'required': True}, 'input': {'type': 'range', 'options': {'default': 1000.0, 'values': [{'min': 10.0, 'max': 20000.0, 'step': 1}]}}}, {'name': 'buffer_miter_limit', 'label': 'Buffer miter limit', 'type': 'integer', 'qprocessing_type': 'number', 'default': 2.0, 'editable': True, 'validate': {'required': True}, 'input': {'type': 'range', 'options': {'default': 2.0, 'values': [{'min': 0.0, 'max': 10.0, 'step': 1}]}}}, {'name': 'buffer_segments', 'label': 'Buffer segments', 'type': 'integer', 'qprocessing_type': 'number', 'default': 2.0, 'editable': True, 'validate': {'required': True}, 'input': {'type': 'range', 'options': {'default': 2.0, 'values': [{'min': 0.0, 'max': 10.0, 'step': 1}]}}}, {'name': 'ingresso1', 'label': 'Ingresso1', 'type': 'varchar', 'qprocessing_type': 'vector', 'default': None, 'editable': True, 'validate': {'required': True}, 'input': {'type': 'prjvectorlayer', 'options': {'datatypes': ['polygon'], 'values': []}}}], 'outputs': [{'name': 'layer_bufferd', 'label': 'Layer bufferd', 'qprocessing_type': 'outputVector', 'type': 'varchar', 'default': None, 'validate': {'required': True}, 'input': {'type': 'outputvectorlayer', 'options': {'values': [{'value': 'shp', 'key': 'Shapefile'}, {'value': 'geojson', 'key': 'GeoJSON'}, {'value': 'kml', 'key': 'KML'}, {'value': 'kmz', 'key': 'KMZ'}]}}}]}
        self.assertEqual(qpm.render2dict(), aspected_dict)

        # Testing make_model_params
        # -------------------------------------------------
        form_data = {

        }



class TestQProcessingActionAPIREST(TestQProcessingBase):
    """
    Test for API REST general Actions
    """

    def test_action_fields(self):
        """
        Testing of `actions/fields`, `qprocessing-action-fields`
        """

        self.client.login(username=self.test_admin1.username, password=self.test_admin1.username)

        qgs_alyer_id = 'points_aae45d3d_4911_445f_a6de_0e4ab724cd1b'

        # Testing exception
        # -----------------------------
        # No layer id
        url = reverse('qprocessing-action-fields', args=[self.project.instance.pk, 'no_layer_id'])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 500)

        jres = json.loads(res.content)
        self.assertFalse(jres['result'])
        self.assertEqual(jres['error'], {"code":"servererror","message":"A error server is occured!",
                                         "data":"Layer matching query does not exist."})

        # datatype empty
        url = reverse('qprocessing-action-fields', args=[self.project.instance.pk, qgs_alyer_id])
        res = self.client.get(f'{url}?datatype=')
        self.assertEqual(res.status_code, 400)

        jres = json.loads(res.content)
        self.assertFalse(jres['result'])
        self.assertEqual(jres['error'], {"code": "validation", "message": "Data are not correct or insufficent!",
                                         "data": ["For datatype the admissible values are: string, numeric, datetime, "
                                                  "any"]})

        # wrong datatype
        url = reverse('qprocessing-action-fields', args=[self.project.instance.pk, qgs_alyer_id])
        res = self.client.get(f'{url}?datatype=wrong')
        self.assertEqual(res.status_code, 400)

        jres = json.loads(res.content)
        self.assertFalse(jres['result'])
        self.assertEqual(jres['error'], {"code": "validation", "message": "Data are not correct or insufficent!",
                                         "data": ["'wrong' is not a valid datatype, the admissible values are: string, "
                                                  "numeric, datetime, any"]})

        # Testing filtering results
        # -----------------------------------
        # All fields: without `datatype` get parameter

        url = reverse('qprocessing-action-fields', args=[self.project.instance.pk, qgs_alyer_id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        qprj = get_qgs_project(self.project.instance.qgis_file.path)
        qlayer = qprj.mapLayer(qgs_alyer_id)


        aspected_all = {
            'result': True,
            'fields': [{'key': f.displayName(), 'value':f.name()} for f in qlayer.fields()]
        }

        jres = json.loads(res.content)
        self.assertEqual(jres, aspected_all)

        # `datatype': string
        url = reverse('qprocessing-action-fields', args=[self.project.instance.pk, qgs_alyer_id])
        res = self.client.get(f'{url}?datatype=string')
        self.assertEqual(res.status_code, 200)

        aspected = {
            'result': True,
            'fields': [{'key': 'name', 'value': 'name'}]
        }

        jres = json.loads(res.content)
        self.assertEqual(jres, aspected)

        # `datatype': numeric
        url = reverse('qprocessing-action-fields', args=[self.project.instance.pk, qgs_alyer_id])
        res = self.client.get(f'{url}?datatype=numeric')
        self.assertEqual(res.status_code, 200)

        aspected = {
            'result': True,
            'fields': [
                {'key': 'fid', 'value': 'fid'},
                {'key': 'value', 'value': 'value'}
            ]
        }

        jres = json.loads(res.content)
        self.assertEqual(jres, aspected)

        # `datatype': datetime
        url = reverse('qprocessing-action-fields', args=[self.project.instance.pk, qgs_alyer_id])
        res = self.client.get(f'{url}?datatype=datetime')
        self.assertEqual(res.status_code, 200)

        aspected = {
            'result': True,
            'fields': []
        }

        jres = json.loads(res.content)
        self.assertEqual(jres, aspected)

        # `datatype': any
        url = reverse('qprocessing-action-fields', args=[self.project.instance.pk, qgs_alyer_id])
        res = self.client.get(f'{url}?datatype=any')
        self.assertEqual(res.status_code, 200)

        jres = json.loads(res.content)
        self.assertEqual(jres, aspected_all)

        self.client.logout()





