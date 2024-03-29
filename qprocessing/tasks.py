# coding=utf-8
"""" Module for async scripting
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-23'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from functools import wraps

from django.db import close_old_connections
from django.contrib.auth.models import User
from django.conf import settings
from huey.contrib.djhuey import HUEY
from huey_monitor.tqdm import ProcessInfo
from celery import shared_task, current_task
from celery.utils.log import get_task_logger
from .models import QProcessingProject
from .utils.data import QProcessingModel
from qgis.core import QgsProcessingContext, QgsProcessingFeedback, QgsProject, Qgis


import logging

logger = logging.getLogger('qprocessing')

task = HUEY.task

celery_logger = get_task_logger(__name__)

def run_model_test(qprocessing_project_pk, project_pk, params):


    print(qprocessing_project_pk)
    qpp = QProcessingProject.objects.get(pk=qprocessing_project_pk)
    prj = qpp.projects.get(pk=project_pk)
    print(prj)
    print(prj.qgis_project)


    return True

def run_model(url_params, form_data, **kwargs):
    """
    Run processing model
    """

    qpp = QProcessingProject.objects.get(pk=url_params['qprocessingproject_pk'])
    qpm = QProcessingModel(str(qpp.model.file))

    prj_instance = qpp.projects.get(pk=url_params['project_pk'])
    # prj = prj_instance.qgis_project
    # prj = QgsProject()
    # flags = Qgis.ProjectReadFlags()
    # flags |= Qgis.ProjectReadFlag.DontLoadLayouts
    # # flags |= Qgis.ProjectReadFlag.DontResolveLayers
    # prj.read(str(prj_instance.qgis_file.path), flags)

    prj, params = qpm.make_model_params(form_data=form_data, qproject=prj_instance, **kwargs)

    qpm = QProcessingModel(str(qpp.model.file))

    ctx = QgsProcessingContext()
    if settings.DEBUG and Qgis.QGIS_VERSION_INT >= 33400:
        ctx.setLogLevel(QgsProcessingContext.LogLevel.ModelDebug)
    ctf = QgsProcessingFeedback()

    ctx.setProject(prj)
    res = qpm.process_algorithm(params, ctx, ctf)

    # Replace outputs
    res = qpm.make_outputs(res, url_params['qprocessingproject_pk'], url_params['project_pk'])

    return res

def close_db(fn):
    """Decorator called by db_task() to be used with tasks that may operate
    on the database.

    This implementation is a copy of djhuey implementation but it falls
    back to noop when HUEY.testing is True.

    Set HUEY.testing to True to skip DB connection close.

    """

    @wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        finally:
            if not HUEY.immediate and not getattr(HUEY, 'testing', False):
                close_old_connections()
    return inner


def db_task(*args, **kwargs):
    """Decorator to be used with tasks that may operate on the database.

    This implementation is a copy of djhuey implementation but it falls
    back to noop when HUEY.testing is True.

    Set HUEY.testing to True to skip DB connection close.

    """

    def decorator(fn):
        ret = task(*args, **kwargs)(close_db(fn))
        ret.call_local = fn
        return ret
    return decorator

@db_task(context=True)
def run_model_task(url_params, form_data, task, **kwargs):
    """
    Run processing model
    """

    process_info = ProcessInfo(
        task,
        desc='Run Processing Model'
    )

    #return run_model(qpp.pk, url_params['project_pk'], params)
    return run_model(url_params, form_data, **kwargs)

@shared_task(name='run_model_celery', bind=True)
def run_model_celery_task(self, url_params, form_data, **kwargs):


    model =  run_model(url_params, form_data, **{'user': User.objects.get(pk=kwargs['user_pk'])})
    return {}