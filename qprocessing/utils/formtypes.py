# coding=utf-8
"""" Module to build config options for Qprocessing client form building.
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-06-07'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from django.conf import settings
from core.utils.structure import \
    FORM_FIELD_TYPE_CHECK, \
    FORM_FIELD_TYPE_SELECT

from qdjango.utils.edittype import \
    FORM_FIELD_TYPE_QGIS_RANGE

# Processing input types
# ---------------------------------------
from qgis.core import \
    (QgsProcessingParameterDistance, \
    QgsProcessingParameterVectorLayer, \
    QgsProcessingParameterField, \
    QgsProcessingParameterFeatureSource, \
    QgsProcessingParameterBand, \
    QgsProcessingParameterBoolean, \
    QgsProcessingParameterAggregate, \
    QgsProcessingParameterColor, \
    QgsProcessingParameterEnum, \
    QgsProcessingParameterExpression, \
    QgsProcessingParameterExtent, \
    QgsProcessingParameterDuration, \
    QgsProcessingParameterField, \
    QgsProcessingParameterFile, \
    QgsProcessingParameterGeometry, \
    QgsProcessingParameterNumber, \
    QgsProcessingParameterPoint, \
    QgsProcessingParameterRange, \
    QgsProcessingParameterScale, \
    QgsProcessingParameterAnnotationLayer, \
    QgsProcessingParameterCrs, \
    QgsProcessingParameterString, \
    QgsProcessingParameterDateTime, \
    QgsProcessingParameterCoordinateOperation, \
    QgsProcessingParameterRasterLayer, \
    QgsProcessingOutputVectorLayer, \
    QgsProcessingOutputRasterLayer, \
    QgsProcessingOutputFile, \
    QgsProcessingOutputHtml, \
    QgsWkbTypes,
    QgsProcessingFeatureSourceDefinition)

# Processing ouput types
# ---------------------------------------
from qgis.core import \
    QgsProcessingOutputVectorLayer
from core.utils import structure
from core.utils.qgisapi import get_layer_fids_from_server_fids

# Mapping qprocessing parameters type
MAPPING_PROCESSING_PARAMS_FORM_TYPE = {
    # Inputs
    QgsProcessingParameterDistance('').type(): structure.FIELD_TYPE_FLOAT,
    QgsProcessingParameterDateTime('').type(): structure.FIELD_TYPE_DATETIME,
    QgsProcessingParameterBoolean('').type(): structure.FIELD_TYPE_BOOLEAN,
    QgsProcessingParameterRasterLayer('').type(): structure.FIELD_TYPE_VARCHAR,
    QgsProcessingParameterVectorLayer('').type(): structure.FIELD_TYPE_VARCHAR,
    QgsProcessingParameterRange('').type(): structure.FIELD_TYPE_INTEGER,
    QgsProcessingParameterNumber('').type(): structure.FIELD_TYPE_INTEGER,
    QgsProcessingParameterExtent('').type(): structure.FIELD_TYPE_VARCHAR,
    QgsProcessingParameterFeatureSource('').type(): structure.FIELD_TYPE_VARCHAR,
    QgsProcessingParameterField('').type(): structure.FIELD_TYPE_VARCHAR,
    #TODO: add other QgsProcessingParamenter* type
    # Outputs
    QgsProcessingOutputVectorLayer('').type(): structure.FIELD_TYPE_VARCHAR,
    QgsProcessingOutputRasterLayer('').type(): structure.FIELD_TYPE_VARCHAR,
    QgsProcessingOutputFile('').type(): structure.FIELD_TYPE_VARCHAR,
    QgsProcessingOutputHtml('').type(): structure.FIELD_TYPE_VARCHAR,
    #TODO: add other QgsProcessingOutput* type
}

# Specific Form Field Types for QProcessing client forms
# ------------------------------------------------------
FORM_FIELD_TYPE_VECTORLAYER = 'vectorlayer' # A vector data layer which can be uploaded
FORM_FIELD_TYPE_PRJVECTORLAYER = 'prjvectorlayer' # A vector layer belonging to the project
FORM_FIELD_TYPE_RASTERLAYER = 'rasterlayer' # A raster data layer which can be uploaded
FORM_FIELD_TYPE_PRJRASTERLAYER = 'prjrasterlayer' # A raster layer belonging to the project
FORM_FIELD_TYPE_EXTENT = 'extent' # Type to get extent values form layer, map, bookmarks or by hand
FORM_FIELD_TYPE_FEATURESOURCE = 'prjvectorlayerfeature' # A vector layer belonging to the project or feature selected
FORM_FIELD_TYPE_FIELDCHOOSER = 'fieldchooser' # A select with multiple choosen or not belonging from other vectorlayer or prjvectorlayer field

# For outputs
FORM_FIELD_TYPE_OUTPUT_VECTORLAYER = 'outputvectorlayer' # Type to get outputvector type
FORM_FIELD_TYPE_OUTPUT_RASTERLAYER = 'outputrasterlayer' # Type to get outputraster type
FORM_FIELD_TYPE_OUTPUT_FILE = 'outputfile' # Type to get outputfile type
FORM_FIELD_TYPE_OUTPUT_HTML = 'outputhtml' # Type to get outputfile type


class QProcessingFormType(object):
    """
    Base class to render form config structure for g3w-client
    """

    def __init__(self, **qprocessingparams):
        """
        :param qprocessingparams: QgsProcessingParameterDefinition.toVariantMap results
        """

        for key, value in list(qprocessingparams.items()):
            setattr(self, key, value)

    @property
    def input_form(self):
        return dict()

    @staticmethod
    def create_model_params(qgs_project, parameter):
        '''
        Method to make parameters for running model.
        :params qgs_project: qdjango.model.Project instance.
        :params parameter: POST data coming from g3w-client.
        :return: Str, Object, ... for model running.
        '''

        return parameter


class QProcessingFormTypeDistance(QProcessingFormType):
    """
    FormType QProcessing class for type `distance` (QgsProcessingParameterDistance)
    """

    field_type = structure.FORM_FIELD_TYPE_FLOAT

    @property
    def input_form(self):
        return {
            'input': {
                'type': FORM_FIELD_TYPE_QGIS_RANGE,
                'options': {
                    'default': self.default,
                    'values': [
                        {
                            'min': self.min,
                            'max': self.max,
                            'step': 1
                        }

                    ]
                }
            }
        }

class QProcessingFormTypeNumber(QProcessingFormType):
    """
    FormType QProcessing class for type `number` (QgsProcessingParameterNUmber)
    """

    @property
    def input_form(self):
        return {
            'input': {
                'type': FORM_FIELD_TYPE_QGIS_RANGE,
                'options': {
                    'default': self.default,
                    'values': [
                        {
                            'min': self.min,
                            'max': self.max,
                            'step': 1
                        }

                    ]
                }
            }
        }

class QProcessingFormTypeVectorLayer(QProcessingFormType):
    """
    FormType QProcessing class for type `vector` (QgsProcessingParameterVectorLayer)
    """

    field_type = FORM_FIELD_TYPE_PRJVECTORLAYER
    TYPES = {
        5: 'nogeometry',
        0: 'point',
        1: 'line',
        2: 'polygon',
        -1: 'anygeometry'
    }

    @staticmethod
    def create_model_params(qgs_project, parameter):
        return qgs_project.mapLayer(parameter).source()

    @property
    def input_form(self):
        return {
            'input': {
                'type': self.field_type,
                'options': {
                    'datatypes': [self.TYPES[t] for t in self.data_types]
                }
            }
        }

class QProcessingFormTypeRasterLayer(QProcessingFormType):
    """
    FormType QProcessing class for type `raster` (QgsProcessingParameterRasterLayer)
    """

    field_type = FORM_FIELD_TYPE_PRJRASTERLAYER

    @staticmethod
    def create_model_params(qgs_project, parameter):
        return qgs_project.mapLayer(parameter).source()

    @property
    def input_form(self):
        return {
            'input': {
                'type': self.field_type,
                'options': {}
            }
        }

class QProcessingFormTypeExtent(QProcessingFormType):
    """
    FormType QProcessing class for type `extent` (QgsProcessingParameterExtent)
    """

    field_type = FORM_FIELD_TYPE_EXTENT

    @property
    def input_form(self):
        return {
            'input': {
                'type': self.field_type,
                'options': {
                    'default': self.default
                }
            }
        }


class QProcessingFormTypeBoolean(QProcessingFormType):
    """
     FormType QProcessing class for type `boolean` (QgsProcessingParameterBoolean)
    """

    field_type = FORM_FIELD_TYPE_CHECK

    @staticmethod
    def create_model_params(qgs_project, parameter):
        return True if parameter.lower() == 'true' else False

    @property
    def input_form(self):
        return {
            'input': {
                'type': self.field_type,
                'options': {
                    'default': self.default,
                    'values': [
                        {'value': 'True', 'checked': True},
                        {'value': 'False', 'checked': False},
                    ]
                }
            }
        }


class QProcessingFormTypeField(QProcessingFormType):
    """
     FormType QProcessing class for type `field` (QgsProcessingParameterField)
    """

    field_type = FORM_FIELD_TYPE_FIELDCHOOSER
    TYPES = {
        QgsProcessingParameterField.String: 'string',
        QgsProcessingParameterField.Numeric: 'numeric',
        QgsProcessingParameterField.DateTime: 'datetime',
        QgsProcessingParameterField.Any: 'any'
    }

    @staticmethod
    def create_model_params(qgs_project, parameter):
        return parameter.split(',')

    @property
    def input_form(self):
        return {
            'input': {
                'type': self.field_type,
                'options': {
                    'default': self.default,
                    'multiple': self.allow_multiple,
                    'parent_field': self.parent_layer,
                    'datatype': self.TYPES[self.data_type],
                    'default_to_all_fields': self.default_to_all_fields,
                    'values': []
                }
            }
        }

class QProcessingFormTypeFeatureSource(QProcessingFormTypeVectorLayer):
    """
    FormType QProcessing class for type `vector` (QgsProcessingParameterVectorLayer)
    """

    field_type = FORM_FIELD_TYPE_FEATURESOURCE

    @staticmethod
    def create_model_params(qgs_project, parameter):
        # Split by `:`
        subparams = parameter.split(':')
        qgs_layer = qgs_project.mapLayer(subparams[0])
        if len(subparams) == 1:
            return QgsProcessingFeatureSourceDefinition(qgs_layer.source())
        else:
            qgs_layer.selectByIds(get_layer_fids_from_server_fids(subparams[1].split(','), qgs_layer))
            return QgsProcessingFeatureSourceDefinition(qgs_layer.source(), selectedFeaturesOnly=True)

# OUTPUT PROCESSING
# -------------------------------------------------------------
class QProcessingFormTypeOutputRaster(QProcessingFormType):
    """
    FormType QProcessing class for type `outputraster` (QgsProcessingOutputRasterLayer)
    """

    field_type = FORM_FIELD_TYPE_OUTPUT_RASTERLAYER

    @property
    def input_form(self):
        return {
            'input': {
                'type': self.field_type,
                'options': {
                    'values': settings.QPROCESSING_OUTPUT_RASTER_FORMATS
                }
            }
        }

class QProcessingFormTypeOutputFile(QProcessingFormType):
    """
    FormType QProcessing class for type `outputfile` (QgsProcessingOutputFile)
    """

    field_type = FORM_FIELD_TYPE_OUTPUT_FILE

    @property
    def input_form(self):
        return {
            'input': {
                'type': self.field_type,
                'options': {
                    'values': settings.QPROCESSING_OUTPUT_FILE_FORMATS
                }
            }
        }

class QProcessingFormTypeOutputHtml(QProcessingFormType):
    """
    FormType QProcessing class for type `outputhtml` (QgsProcessingOutputhtml)
    """

    field_type = FORM_FIELD_TYPE_OUTPUT_HTML

    @property
    def input_form(self):
        return {
            'input': {
                'type': self.field_type,
                'options': {
                    'values': settings.QPROCESSING_OUTPUT_HTML_FORMATS
                }
            }
        }

class QProcessingFormTypeOutputVector(QProcessingFormType):
    """
    FormType QProcessing class for type `outputvector` (QgsProcessingOutputVectorLayer)
    """

    field_type = FORM_FIELD_TYPE_OUTPUT_VECTORLAYER

    @property
    def input_form(self):
        return {
            'input': {
                'type': self.field_type,
                'options': {
                    'values': settings.QPROCESSING_OUTPUT_VECTOR_FORMATS
                }
            }
        }


MAPPING_QPROCESSINGTYPE_FORMTYPE = {
    # Inputs
    QgsProcessingParameterDistance('').type(): QProcessingFormTypeDistance,
    QgsProcessingParameterNumber('').type(): QProcessingFormTypeNumber,
    QgsProcessingParameterVectorLayer('').type(): QProcessingFormTypeVectorLayer,
    QgsProcessingParameterRasterLayer('').type(): QProcessingFormTypeRasterLayer,
    QgsProcessingParameterExtent('').type(): QProcessingFormTypeExtent,
    QgsProcessingParameterFeatureSource('').type(): QProcessingFormTypeFeatureSource,
    QgsProcessingParameterBoolean('').type(): QProcessingFormTypeBoolean,
    QgsProcessingParameterField('').type(): QProcessingFormTypeField,
    # Outputs
    QgsProcessingOutputVectorLayer('').type(): QProcessingFormTypeOutputVector,
    QgsProcessingOutputRasterLayer('').type(): QProcessingFormTypeOutputRaster,
    QgsProcessingOutputFile('').type(): QProcessingFormTypeOutputFile,
    QgsProcessingOutputHtml('').type(): QProcessingFormTypeOutputHtml,
}