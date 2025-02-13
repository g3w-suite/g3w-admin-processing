# coding=utf-8
"""" QProcessing receiver signals.
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-06-07'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.core.files.storage import FileSystemStorage
from guardian.shortcuts import get_objects_for_user
from core.signals import initconfig_plugin_start
from .models import QProcessingProject, QProcessingInputUpload
from .utils.data import QProcessingModel
from .configs import __BASE_RUN_MODEL_URL, __BASE_TASK_INFO_URL, __BASE_ACTION_URL, __BASE_UPLOAD_URL
from importlib.metadata import version as get_version

import os

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

    return {
        'qprocessing': {
            'version': get_version('qprocessing'),
            'gid': f"{kwargs['projectType']}:{kwargs['project']}",
            'async': settings.QPROCESSING_ASYNC_RUN,
            'urls': {
                'run': f'/qprocessing{__BASE_RUN_MODEL_URL}',
                'taskinfo': f'/qprocessing{__BASE_TASK_INFO_URL}',
                'fields': f'/qprocessing{__BASE_ACTION_URL}fields/',
                'upload': f'/qprocessing{__BASE_UPLOAD_URL}',
            },
            'models': [{
                **QProcessingModel(str(qpp.model.file)).render2dict(),
                'id': qpp.pk,
                'results': [],
                # TODO: move the following into render2dict? (converts [admin] model inputs into [client] form inputs)
                'inputs': [{
                    **input,
                    'visible': True,
                    'validate': {
                        'empty': True,
                        'message': None,
                        'required': True,
                        'unique': False,
                        'valid': False,
                        '_valid': False,
                        **input['validate'],
                    },
                    'get_default_value': True,
                } for input in QProcessingModel(str(qpp.model.file)).inputs.values()],
            } for qpp in qpprojects],
            'sidebar': {
                'id': 'qprocessing',
                'title': 'plugins.qprocessing.title',
                'collapsible': True,
                'open': False,
                'isolate': False,
                'iconColor': 'green',
                'icon': 'tools',
                'mobile': True,
                'sidebarOptions': {
                    'position': "spatialbookmarks" # can be a number or a string
                }
            }
        }
    }

@receiver(post_delete, sender=QProcessingInputUpload)
def delete_input_upload_file(sender, **kwargs):

    base_url = f"{kwargs['instance'].user.pk}/" if kwargs['instance'].user else f"nouser/"
    base_url += "uploads/"
    storage = FileSystemStorage(location=settings.QPROCESSING_INPUT_UPLOAD_PATH)
    if os.path.splitext(kwargs['instance'].name)[-1][1:].lower() == 'shp':

        # Delete every shapefile files
        for ext in settings.QPROCESSING_INPUT_SHP_EXTS + ['qix', 'cpg']:
            fname = f"{os.path.splitext(kwargs['instance'].name)[0]}.{ext}"
            storage.delete(f"{base_url}{fname}")
    else:
        storage.delete(f"{base_url}{kwargs['instance'].name}")
