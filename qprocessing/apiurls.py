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

urlpatterns = [
    path('api/run/<int:qgprocessingproject_pk>/<int:project_pk>', QProcessingRunModelView.as_view(),
         name='qprocessing-run-model'),
    path('api/infotask/<str:task_id>', QProcessingRunInfoTask.as_view(), name='qprocessing-infotask')
]