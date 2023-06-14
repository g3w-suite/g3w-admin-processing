# coding=utf-8
""" Qprocessing django urls module.
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-09'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from django.db import models
from django.utils.translation import gettext_lazy as _
from qdjango.models import Project
from .utils.data import QProcessingModel
class QProcessingProject(models.Model):
    """
    Model to stor relation between QGIS processing model (.model3) and Qdjango Projects objects
    """

    #TODO: add new permission type, `can_run_model`

    model = models.FileField(_('QGIS processing model file (.model3)'), upload_to='qprocessing')
    projects = models.ManyToManyField(Project, help_text=_('Select one of more projects to link to this QGIS processing model'))
    note = models.TextField(_('Note'), null=True, blank=True)

    def get_qprocessingmodel(self):
        """
        Return an instance of QProcessingModel utility object by self instance
        """

        if not self.model:
            return None

        return QProcessingModel(str(self.model.file))

    def get_qdjango_project(self, project_pk:int):
        """
        Give a Qdjango project pk return qdjango.Project model instance
        """

        return self.projects.get(pk=project_pk)



