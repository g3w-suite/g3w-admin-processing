# coding=utf-8
"""" Data qprocessing module
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-09'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from qgis.core import QgsProcessingModelAlgorithm
from .formtypes import \
    MAPPING_PROCESSING_PARAMS_FORM_TYPE, \
    MAPPING_QPROCESSINGTYPE_FORMTYPE

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
        self.inputs = []
        for op in self.model.orderedParameters():
            dop = self.model.parameterDefinition(op.parameterName())
            vmap = dop.toVariantMap()
            qtype = vmap['parameter_type']
            flags = self._read_flags(vmap['flags'])

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


            # For QgsProcessingParameterLimitedDataTypes:
            try:
                dt.update({
                    'data_types': dop.dataTypes()
                })
            except:
                pass

            self.inputs.append(dt)

    def _get_outputs(self):
        """
        From a QgsProcessingModelAlgorithm instance get information about
        outputs

        :return: None
        """
        self.outputs = []
        for od in self.model.outputDefinitions():
            self.outputs.append(
                {
                    'name': od.name(),
                    'description': od.description(),
                    'type': od.type()

                }
            )

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

    def render2dict(self):
        """
        Render properties to json

        :return: dict
        """

        return {
            'name': self.name,
            'display_name': self.display_name,
            'inputs': self.inputs,
            'outputs': self.outputs
        }



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







