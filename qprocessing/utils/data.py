# coding=utf-8
"""" Data qprocessing module
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-09'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from qgis.core import \
    QgsProcessingModelAlgorithm, QgsProject, Qgis
from qdjango.models import Project as QdjangoProject
from core.utils.qgisapi import get_layer_fids_from_server_fids
from .formtypes import \
    (MAPPING_PROCESSING_PARAMS_FORM_TYPE,
    MAPPING_QPROCESSINGTYPE_FORMTYPE,
    QgsProcessingOutputVectorLayer,
     QgsProcessingOutputRasterLayer,
     QgsProcessingOutputHtml,
     QgsProcessingOutputFile)
from .exceptions import (
    QProcessingInputException,
    QProcessingOutputException)

import os
from cryptography.fernet import Fernet
import datetime

class QProcessingModel(object):
    """
    A class to read a .model3 XMl file and retrieve information about inputs outputs end other.
    """

    def __init__(self, model_file):
        self.model_file = model_file

        # Instance QgsProcessingModelAlgorithm
        self.model = QgsProcessingModelAlgorithm()
        load = self.model.fromFile(self.model_file)
        if not load:
            raise Exception(f"The model file could not be loaded, check that the path is correct: {self.model_file}")

        # Analyze .model3 file
        # -------------------------------------------
        # Get general metadata properties
        self._get_generals()

        #Get inputs and outputs properties
        self._get_inputs()

        # Get outputs
        self._get_outputs()

    def _get_generals(self):
        """
        From a QgsProcessingModelAlgorithm instance get information general metadata information, i.e Model name etc.

        :return: None
        """

        self.name = self.model.name()
        self.display_name = self.model.displayName()

    def _get_inputs(self):
        """
        From a QgsProcessingModelAlgorithm instance get information about
        inputs

        :return: None
        """

        # Get inputs of first algorithm
        self.inputs = {}
        for op in self.model.orderedParameters():
            dop = self.model.parameterDefinition(op.parameterName())
            vmap = dop.toVariantMap()
            qtype = vmap['parameter_type']
            flags = self._read_flags(vmap['flags'])

            # Checking the type of processing if it is managed
            if qtype not in MAPPING_PROCESSING_PARAMS_FORM_TYPE:
                raise QProcessingInputException(_(f'Processing input type`{qtype}` is not managed.'))

            dt = {
                    'name': vmap['name'],
                    'label': vmap['description'],
                    'type': MAPPING_PROCESSING_PARAMS_FORM_TYPE[qtype],
                    'qprocessing_type': qtype,
                    'default': dop.defaultValue(),
                    'editable': True, # Editable by default: only for g3w-client complaint
                    'validate': {
                        "required": dop.FlagOptional not in flags
                    },
                    'input': {
                        'type': 'text',
                        'options': {}
                    }
                }

            # Update `input` section by qtype
            if qtype in MAPPING_QPROCESSINGTYPE_FORMTYPE:
                dt.update(MAPPING_QPROCESSINGTYPE_FORMTYPE[qtype](**vmap).input_form)


            self.inputs.update({
                vmap['name']: dt
            })

    def _get_outputs(self):
        """
        From a QgsProcessingModelAlgorithm instance get information about
        outputs

        :return: None
        """
        self.outputs = {}
        for od in self.model.outputDefinitions():
            qtype = od.type()

            # Checking the type of processing if it is managed
            if qtype not in MAPPING_PROCESSING_PARAMS_FORM_TYPE:
                raise QProcessingOutputException(_(f'Processing output type`{qtype}` is not managed.'))

            ot = {
                'name': od.name(),
                'label': od.description(),
                'qprocessing_type': qtype,
                'type': MAPPING_PROCESSING_PARAMS_FORM_TYPE[qtype],
                'default': None,
                'validate': {
                    "required": True
                },
                'input': {
                    'type': 'text',
                    'options': {}
                }
            }

            # Update `output` section by qtype
            if qtype in MAPPING_QPROCESSINGTYPE_FORMTYPE:
                ot.update(MAPPING_QPROCESSINGTYPE_FORMTYPE[qtype](**{}).input_form)

            self.outputs.update({
                od.name(): ot
            })

    ##
    def _read_flags(self, flags:int ):

        def fit_bits(n:int):
            """
            fn_bits: Calculate binary (base2) numbers from integer (base10)
            """
            while n:
                b = n & (~n + 1)
                yield b
                n ^= b

        return [flag for flag in fit_bits(flags)]

    def get_qgsprocessingparameter(self, name):
        """
        Return the QgsProcessingModelParameter by name
        """

        return self.model.parameterComponent(name)

    def render2dict(self):
        """
        Render properties to json

        :return: dict
        """

        return {
            'name': self.name,
            'display_name': self.display_name,
            'inputs': list(self.inputs.values()),
            'outputs': list(self.outputs.values())
        }

    def make_model_params(self, form_data:dict, qproject: QdjangoProject, **kwargs):
        """
        Build and return a dict params for algorithm processing
        :param form_data: dict data from g3w-client processing model form (usually request.data in a View).
        :param qgs_project: An instace of QgsProject.
        :return: tuple of QGSProject instance and  dict params for algorithm processing

        Change the values of form_data input by model inputs/outputs type
        """


        qgs_project = QgsProject()
        flags = Qgis.ProjectReadFlags()
        #flags |= Qgis.ProjectReadFlag.DontLoadLayouts
        #flags |= Qgis.ProjectReadFlag.DontResolveLayers
        qgs_project.read(str(qproject.qgis_file.path), flags)

        #qgs_project = qproject.qgis_project

        params = {}
        params.update(form_data['inputs'])
        params.update(form_data['outputs'])

        # Input cases
        # --------------------------------------
        for k, v in form_data['inputs'].items():

            formtype = MAPPING_QPROCESSINGTYPE_FORMTYPE[self.inputs[k]['qprocessing_type']]
            params[k] = formtype.update_model_params(qgs_project, params[k])


        # Outputs cases
        # --------------------------------------

        # Make directory by user Id
        if 'user' in kwargs:
            save_path = f"{settings.QPROCESSING_OUTPUT_PATH}{kwargs['user'].pk}/"
        else:
            save_path = f"{settings.QPROCESSING_OUTPUT_PATH}nouser/"

        if not os.path.exists(save_path):
            os.mkdir(save_path)

        for k, o in form_data['outputs'].items():

            formtype = MAPPING_QPROCESSINGTYPE_FORMTYPE[self.outputs[k]['qprocessing_type']]
            params[self.outputs[k]['name']] = formtype.update_model_params(qgs_project, o, self.outputs[k],
                                                                           save_path=save_path)

        return qgs_project, params

    def make_outputs(self, pres, qprocessingproject_pk, project_pk):
        """
        Refine processing running model output for g3w-client.
        :param pres: Processing running model output dict.
        :param qprocessingproject_pk: QProcessingProject model instance pk.
        :param project_pk: Qdjango Project model instance pk.
        :return: Return a dict with url to new geo data download.
        """

        out = {}
        for k, o in self.outputs.items():
            if k in pres and o['qprocessing_type'] in [
                QgsProcessingOutputVectorLayer('').type(),
                QgsProcessingOutputRasterLayer('').type(),
                QgsProcessingOutputHtml('').type(),
                QgsProcessingOutputFile('').type(),
            ]:
                f = Fernet(settings.QPROCESSING_CRYPTO_KEY)
                out[k] = reverse('qprocessing-download-output', args=(qprocessingproject_pk, project_pk,
                                                                      f.encrypt(pres[k].encode()).decode(),))
        return out




    def validate(self):
        """
        Proxy interface to QgsProcessingModelAlgorithm.validate method.
        """

        return self.model.validate()

    def process_algorithm(self, params, context, feedback):
        """
        Proxy interface to QgsProcessingModelAlgorithm.processAlgorithm method.
        """
        return self.model.processAlgorithm(params, context, feedback)







