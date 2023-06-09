# coding=utf-8
""""
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-06-09'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.urls import path
from django.contrib.auth.decorators import login_required
from .api.views import \
    QProcessingRunModelView, \
    QProcessingRunInfoTask
from .configs import __BASE_RUN_MODEL_URL, __BASE_TASK_INFO_URL


#f'{__BASE_RUN_MODEL_URL[1:]}<int:qprocessingproject_pk>/<int:project_pk>/'

urlpatterns = [
    path('api/run/<int:qprocessingproject_pk>/<int:project_pk>/', QProcessingRunModelView.as_view(),
         name='qprocessing-run-model'),
    path(f'{__BASE_TASK_INFO_URL[1:]}/<str:task_id>/', QProcessingRunInfoTask.as_view(), name='qprocessing-infotask')
]