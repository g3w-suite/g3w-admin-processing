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
from .api.views import (
    QProcessingRunModelView,
    QProcessingRunInfoTaskView,
    QProcessingDownLoadOutputView,
    QProcessingProjectViewerUsersView,
    QProcessingActionFieldsView,
    QProcessingInputUploadView
)
from .configs import (
    __BASE_RUN_MODEL_URL,
    __BASE_TASK_INFO_URL,
    __BASE_OUTPUT_URL,
    __BASE_ACTION_URL,
    __BASE_UPLOAD_URL
 )

urlpatterns = [
    # G3W-CLIENT API url:
    # ------------------------------------------------------
    path(f'{__BASE_RUN_MODEL_URL[1:]}<int:qprocessingproject_pk>/<int:project_pk>/',
         QProcessingRunModelView.as_view(),
         name='qprocessing-run-model'),

    # Use for asyncronous task
    path(f'{__BASE_TASK_INFO_URL[1:]}<str:task_id>/',
         QProcessingRunInfoTaskView.as_view(),
         name='qprocessing-infotask'),

    # Outputs
    path(f'{__BASE_OUTPUT_URL[1:]}<int:qprocessingproject_pk>/<int:project_pk>/<str:encpath>/',
         QProcessingDownLoadOutputView.as_view(),
         name='qprocessing-download-output'),

    # Actions: filter_fields
    path(f'{__BASE_ACTION_URL[1:]}fields/<int:project_id>/<str:qgs_layer_id>/',
         QProcessingActionFieldsView.as_view(),
        name='qprocessing-action-fields'),

    # Actions: upload input file
    path(f'{__BASE_UPLOAD_URL[1:]}<int:qprocessingproject_pk>/<int:project_pk>/<str:input_name>/',
         QProcessingInputUploadView.as_view(),
        name='qprocessing-action-input-upload'),

    # G3W-ADMIN API url:
    # ------------------------------------------------------
    # For form users
    path('jx/project/viewer_users/',
         login_required(QProcessingProjectViewerUsersView.as_view()),
        name='qprocessing-viewer-users'),
]