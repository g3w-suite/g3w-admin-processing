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


# Customizable settings
# -------------------------------

# Qprocessing path directory for model output files
QPROCESSING_OUTPUT_PATH = '/tmp/'
QPROCESSING_OUTPUT_VECTOR_FORMAT_DEFAULT = 'geojson'

# For download of ouputs
QPROCESSING_CRYPTO_KEY = b'aAf72grwGaZYH9R7ZaGHgSSbtQVXPplXB4wpiMsKtJM='


