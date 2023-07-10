# coding=utf-8
"""" Permissions classe for QProcessing API REST
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-07-10'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from rest_framework.permissions import BasePermission
from usersmanage.configs import *
from usersmanage.utils import get_users_for_object
from qprocessing.models import QProcessingProject

import logging

logger = logging.getLogger('qprocessing')


class RunModelPermission(BasePermission):
    """
    Allows access only to users have permission run_model
    """

    def has_permission(self, request, view):

        # get
        try:
            qpp = QProcessingProject.objects.get(pk=view.kwargs['qprocessingproject_pk'])

            # Check permission on QProcessingProject and on Porject

            return request.user.has_perm('qprocessing.run_model', qpp) and \
                request.user.has_perm('qdjango.view_project', qpp.get_qdjango_project(view.kwargs['project_pk']))
        except Exception as e:
            logger.debug(f'[QPROCESSING] - RunModelPermission: {e}')
            return False