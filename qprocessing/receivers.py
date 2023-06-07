# coding=utf-8
"""" QProcessing receiver signals.
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-06-07'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.dispatch import receiver
from core.signals import initconfig_plugin_start
from .models import QProcessingProject
from .utils.data import QProcessingModel

@receiver(initconfig_plugin_start)
def set_initconfig_value(sender, **kwargs):
    """
    Set base qprocessing data for initconfig
    """

    # Check if project has QGIS processing models linked.
    qpprojects = QProcessingProject.objects.filter(projects__pk=kwargs['project'])

    if len(qpprojects) == 0:
        return None

    toret = {
        'qprocessing': {
            'gid': f"{kwargs['projectType']}:{kwargs['project']}",
        }
    }

    models = []
    for qpp in qpprojects:
        qpm = QProcessingModel(str(qpp.model.file))
        models.append(qpm.render2json())

    toret['qprocessing'].update({
        'models': models
    })

    return toret
