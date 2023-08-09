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
from guardian.shortcuts import get_objects_for_user
from core.signals import initconfig_plugin_start
from .models import QProcessingProject
from .utils.data import QProcessingModel
from .configs import __BASE_RUN_MODEL_URL, __BASE_TASK_INFO_URL, __BASE_ACTION_URL, __BASE_UPLOAD_URL

@receiver(initconfig_plugin_start)
def set_initconfig_value(sender, **kwargs):
    """
    Set base qprocessing data for initconfig
    """

    # Check if project has QGIS processing models linked.
    # Get QProcessingProject instances by ACL
    qpprojects = get_objects_for_user(sender.request.user, 'run_model', QProcessingProject).\
        filter(projects__pk=kwargs['project'])

    if len(qpprojects) == 0:
        return None

    toret = {
        'qprocessing': {
            'gid': f"{kwargs['projectType']}:{kwargs['project']}",
            'urls': {
                'run': f'/qprocessing{__BASE_RUN_MODEL_URL}',
                'taskinfo': f'/qprocessing{__BASE_TASK_INFO_URL}',
                'fields': f'/qprocessing{__BASE_ACTION_URL}fields/',
                'upload': f'/qprocessing{__BASE_UPLOAD_URL}',
            }
        }
    }

    models = []
    for qpp in qpprojects:
        qpm = QProcessingModel(str(qpp.model.file))
        dictmodel = qpm.render2dict()

        # Adding QProcessingProject.pk
        dictmodel.update({
            'id': qpp.pk,
            'results': []
        })
        models.append(dictmodel)

    toret['qprocessing'].update({
        'models': models
    })


    return toret
