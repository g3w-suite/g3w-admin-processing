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
from huey.contrib.djhuey import HUEY
from huey_monitor.tqdm import ProcessInfo
from celery import shared_task, current_task
from celery.utils.log import get_task_logger
from .models import QProcessingProject
from .utils.data import QProcessingModel
from qgis.core import QgsProcessingContext, QgsProcessingFeedback


task = HUEY.task

celery_logger = get_task_logger(__name__)

def run_model_test(qprocessing_project_pk, project_pk, params):


    print(qprocessing_project_pk)
    qpp = QProcessingProject.objects.get(pk=qprocessing_project_pk)
    prj = qpp.projects.get(pk=project_pk)
    print(prj)
    print(prj.qgis_project)


    return True

def run_model(qprocessing_project_pk, project_pk, params):
    """
    Run processing model
    """

    qpp = QProcessingProject.objects.get(pk=qprocessing_project_pk)
    prj = qpp.projects.get(pk=project_pk).qgis_project

    qpm = QProcessingModel(str(qpp.model.file))

    ctx = QgsProcessingContext()
    ctf = QgsProcessingFeedback()

    ctx.setProject(prj)

    res = qpm.process_algorithm(params, ctx, ctf)

    # Replace outputs
    res = qpm.make_outputs(res)

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
def run_model_task(qprocessing_project_pk, project_pk, params, task):
    """
    Run processing model
    """

    process_info = ProcessInfo(
        task,
        desc='Run Processing Model'
    )

    return run_model(qprocessing_project_pk, project_pk, params)

@shared_task(name='run_model', bind=True)
def run_model_celery_task(self, qprocessing_project_pk, project_pk, params):

    return run_model(qprocessing_project_pk, project_pk, params)