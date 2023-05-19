# coding=utf-8
""" Qprocessing django urls module.
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-09'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.urls import path
from django.contrib.auth.decorators import login_required
from base.urls import G3W_SITETREE_I18N_ALIAS
from  .views import \
    QProcessingProjectsListView, \
    QProcessingProjectAddView, \
    QProcessingProjectUpdateView, \
    QProcessingProjectDeleteView

G3W_SITETREE_I18N_ALIAS.append('qprocessing')

urlpatterns = [

    # For QProcessingProject CRUD
    path('projects/', login_required(QProcessingProjectsListView.as_view()), name='qprocessing-project-list'),
    path('projects/add/', login_required(QProcessingProjectAddView.as_view()), name='qprocessing-project-add'),
    path('projects/update/<int:pk>/', login_required(QProcessingProjectUpdateView.as_view()),
         name='qprocessing-project-update'),
    path('projects/delete/<int:pk>/', login_required(QProcessingProjectDeleteView.as_view()),
         name='qprocessing-project-delete'),
]