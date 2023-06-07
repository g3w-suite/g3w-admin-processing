# coding=utf-8
"""" base configs QProcessing module
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-06-07'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from qgis.core import \
    QgsProcessingParameterDistance, \
    QgsProcessingParameterVectorLayer, \
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
    QgsProcessingParameterRasterLayer

from core.utils.structure import \
    FIELD_TYPE_FLOAT, \
    FIELD_TYPE_INTEGER, \
    FIELD_TYPE_BIGINTEGER, \
    FIELD_TYPE_SMALLINTEGER, \
    FIELD_TYPE_FLOAT, \
    FIELD_TYPE_STRING, \
    FIELD_TYPE_TEXT, \
    FIELD_TYPE_BOOLEAN, \
    FIELD_TYPE_DATE, \
    FIELD_TYPE_TIME, \
    FIELD_TYPE_DATETIME, \
    FIELD_TYPE_IMAGE, \
    FIELD_TYPE_FILE, \
    FIELD_TYPE_VARCHAR, \
    FIELD_TYPE_CHAR



# Mapping qprocessing parameters type
MAPPING_PROCESSING_PARAMS_FORM_TYPE = {
    QgsProcessingParameterDistance: FIELD_TYPE_FLOAT,
    QgsProcessingParameterDateTime: FIELD_TYPE_DATETIME,
    QgsProcessingParameterBoolean: FIELD_TYPE_BOOLEAN,
    QgsProcessingParameterRasterLayer: FIELD_TYPE_VARCHAR,
    QgsProcessingParameterVectorLayer: FIELD_TYPE_VARCHAR,
    QgsProcessingParameterRange: FIELD_TYPE_INTEGER
    #TODO: add other QgsParamenters type
}
