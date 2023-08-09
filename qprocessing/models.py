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
from model_utils.models import TimeStampedModel
from model_utils.fields import UUIDField
from usersmanage.utils import get_users_for_object, get_groups_for_object, setPermissionUserObject
from usersmanage.configs import G3W_VIEWER1, G3W_VIEWER2, G3W_EDITOR2, G3W_EDITOR1
from usersmanage.models import User, Group as AuthGroup
from .utils.data import QProcessingModel


class QProcessingProject(models.Model):
    """
    Model to stor relation between QGIS processing model (.model3) and Qdjango Projects objects
    """

    class Meta:
        permissions = (
            ('run_model', 'Can run a QGIS processing model'),
        )


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

    # ACL
    # ---------------------------------------------
    def setPermissionToEditor(self):
        """ Check and give or remove permission to editor level 1 and editor level 2"""

        currentEditor = set()
        for project in self.projects.all():
            ce = get_users_for_object(project, 'change_project', [G3W_EDITOR1, G3W_EDITOR2],
                                                 with_anonymous=False)
            currentEditor = currentEditor.union(set(ce))

        currentEditorPermission = get_users_for_object(self, 'run_model', [G3W_EDITOR1, G3W_EDITOR2],
                                                       with_anonymous=False)
        permissionEditorToRemove = list(set(currentEditorPermission) - currentEditor)

        if len(currentEditor) > 0 :
            for ce in currentEditor:
                setPermissionUserObject(ce, self, ['run_model'])
        if len(permissionEditorToRemove):
            for per in permissionEditorToRemove:
                setPermissionUserObject(per, self, ['run_model'], mode='remove')

    def set_permissions_to_editor_user_groups(self):
        """ Check and giv or remove permission to editor groups """

        # current editor user groups with change permission on project
        currentEditorGroup = set()
        for project in self.projects.all():
            ceg = get_groups_for_object(project, 'change_project', grouprole='editor')

            currentEditorGroup = currentEditorGroup.union(ceg)

        currentEditorGroupPermission = get_groups_for_object(self, 'run_model', grouprole='editor')
        permissionEditorGroupToRemove = list(set(currentEditorGroupPermission) - currentEditorGroup)

        if len(currentEditorGroup) > 0 :
            for ceg in currentEditorGroup:
                setPermissionUserObject(ceg, self, ['run_model'])
        if len(permissionEditorGroupToRemove):
            for pegr in permissionEditorGroupToRemove:
                setPermissionUserObject(pegr, self, permissions=['run_model'],
                                        mode='remove')

    def addPermissionsToViewers(self, users_id):

        for user_id in users_id:
            setPermissionUserObject(User.objects.get(pk=user_id), self,
                                    permissions='qprocessing.run_model')

    def removePermissionsToViewers(self, users_id=None):

        for user_id in users_id:
            setPermissionUserObject(User.objects.get(pk=user_id), self,
                            permissions='run_model', mode='remove')

    def add_permissions_to_viewer_user_groups(self, groups_id):
            self._permissions_to_user_groups_viewer(groups_id=groups_id)

    def remove_permissions_to_viewer_user_groups(self, groups_id):
            self._permissions_to_user_groups_viewer(groups_id=groups_id, mode='remove')

    def _permissions_to_user_groups_viewer(self, groups_id, mode='add'):

        for group_id in groups_id:
            auth_group = AuthGroup.objects.get(pk=group_id)
            setPermissionUserObject(auth_group, self, permissions=['run_model'],
                                    mode=mode)




class QProcessingInputUpload(TimeStampedModel):
    """
    Model to save information about files uploaded for processing inputs.
    """

    name = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    uuid = UUIDField(editable=True)
    input_name = models.CharField(max_length=400)
    qpp = models.ForeignKey(QProcessingProject, on_delete=models.CASCADE)




