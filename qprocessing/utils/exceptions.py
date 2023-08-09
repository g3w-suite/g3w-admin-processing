# coding=utf-8
"""" QProcessing custom exceptions
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-06-15'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

class QProcessingException(Exception):
    pass

class QProcessingInputException(QProcessingException):
    pass

class QProcessingOutputException(QProcessingException):
    pass