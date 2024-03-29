# coding=utf-8
"""" base configs QProcessing module
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-06-07'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

# Module internal settings
# -------------------------------
__BASE_RUN_MODEL_URL = '/api/run/'
__BASE_TASK_INFO_URL = '/api/infotask/'
__BASE_OUTPUT_URL = '/api/download/'
__BASE_ACTION_URL = '/api/action/'
__BASE_UPLOAD_URL = '/api/upload/'


# Customizable settings
# -------------------------------

# Qprocessing asyncronous run model, by default False set to True
# for run asyncronous model
QPROCESSING_ASYNC_RUN = False

# Qprocessing path directory for model output files
QPROCESSING_OUTPUT_PATH = '/tmp/'
QPROCESSING_INPUT_UPLOAD_PATH = QPROCESSING_OUTPUT_PATH
QPROCESSING_OUTPUT_VECTOR_FORMAT_DEFAULT = 'geojson'
QPROCESSING_OUTPUT_RASTER_FORMAT_DEFAULT = 'tiff'
QPROCESSING_OUTPUT_FILE_FORMAT_DEFAULT = 'pdf'
QPROCESSING_OUTPUT_HTML_FORMAT_DEFAULT = 'html'

QPROCESSING_INPUT_SHP_EXTS = ['shp', 'shx', 'prj', 'dbf', 'shx']

# Formats available for input upload
QPROCESSING_INPUT_UPLOAD_VECTOR_FORMATS = [
    {
        'value': 'zip',
        'key': 'Shapefile'
    },
    {
        'value': 'geojson',
        'key': 'GeoJSON'
    },
    {
        'value': 'kml',
        'key': 'KML'
    },
    {
        'value': 'gpkg',
        'key': 'GeoPackage'
    },
    {
        'value': 'sqlite',
        'key': 'Sqlite/Spatialite'
    }

]


# For Processing form type: input/output
QPROCESSING_OUTPUT_VECTOR_FORMATS = [
    {
        'value': 'shp',
        'key': 'Shapefile'
    },
    {
        'value': 'geojson',
        'key': 'GeoJSON'
    },
    {
        'value': 'kml',
        'key': 'KML'
    },
    {
        'value': 'kmz',
        'key': 'KMZ'
    },
    {
        'value': 'csv',
        'key': 'CSV'
    }
    #'gpkg': 'GeoPackage', # g3w-client cannot read this format
    #'sqlite': 'SpatiaLite' # g3w-client cannot read this format
]

QPROCESSING_OUTPUT_FILE_FORMATS = [
    {
        'value': 'pdf',
        'key': 'PDF'
    },
]

QPROCESSING_OUTPUT_HTML_FORMATS = [
    {
        'value': 'html',
        'key': 'HTML'
    },
]

QPROCESSING_OUTPUT_RASTER_FORMATS = [
    {
        'value': 'vrt',
        'key': 'VRT'
    },
    {
        'value': 'tiff',
        'key': 'TIFF'
    },
    {
        'value': 'png',
        'key': 'PNG'
    },
    {
        'value': 'jpeg',
        'key': 'JPEG'
    },
    {
        'value': 'jpg',
        'key': 'JPG'
    },
]

# For download of ouputs
QPROCESSING_CRYPTO_KEY = b'aAf72grwGaZYH9R7ZaGHgSSbtQVXPplXB4wpiMsKtJM='


