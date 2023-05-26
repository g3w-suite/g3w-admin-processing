# coding=utf-8
"""" Module for async scripting
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-23'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from huey.contrib.djhuey import HUEY, db_task
from huey_monitor.tqdm import ProcessInfo
from .models import QProcessingProject
from qgis.core import QgsProcessingContext, QgsProcessingFeedback


task = HUEY.task

def run_model(qprocessing_project_pk, project_pk, params):
    """
    Run processing model
    """

    qpm = QProcessingProject.objects.get(pk=qprocessing_project_pk)
    prj = qpm.projects.get(pk=project_pk).qgis_project

    ctx = QgsProcessingContext()
    ctf = QgsProcessingFeedback()

    ctx.setProject(prj)

    print(prj)
    print(qpm)
    print(params)

    res = qpm.process_algorithm(params, ctx, ctf)

    return res

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
