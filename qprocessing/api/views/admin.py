# coding=utf-8
""""
    API vies for G3W-ADMIN
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-07-05'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from rest_framework.response import Response
from usersmanage.utils import get_viewers_for_object, get_users_for_object, get_user_groups_for_object
from usersmanage.configs import G3W_VIEWER2, G3W_VIEWER1
from usersmanage.forms import label_users
from core.api.views import G3WAPIView
from qdjango.models import Project
from qprocessing.models import QProcessingProject


class QProcessingProjectViewerUsersView(G3WAPIView):
    """Return viewer_users for project"""

    viewer_permission = 'view_project'

    def get(self, *args, **kwargs):
        # get viewer users
        projects = Project.objects.filter(pk__in=self.request.GET['project_id'].split(','))
        try:
            qpp = QProcessingProject.objects.get(pk=self.request.GET['qpp_id'])
        except:
            qpp = None

        viewers = set()
        viewers_run_model = set()
        group_viewers = set()
        group_viewers_run_model = set()
        for project in projects:
            vs = get_users_for_object(project, self.viewer_permission, [G3W_VIEWER1, G3W_VIEWER2], with_anonymous=True)
            viewers = viewers.union(set(vs))

            viewers_run_model = set()
            if qpp:
                vl = get_users_for_object(qpp, 'run_model', [G3W_VIEWER1, G3W_VIEWER2], with_anonymous=True)
                viewers_run_model = viewers_run_model.union(set(vl))


            gs = get_user_groups_for_object(project, self.request.user, 'view_project', 'viewer')
            group_viewers = group_viewers.union(gs)

            group_viewers_run_model = set()
            if qpp:
                gm = get_user_groups_for_object(qpp, self.request.user, 'run_model', 'viewer')
                group_viewers_run_model = group_viewers_run_model.union(gm)


        self.results.results.update({
            'viewer_users': [
                {
                    'id': viewer.pk,
                    'text': label_users(viewer),
                    'selected': viewer in viewers_run_model
                } for viewer in viewers
            ],
            'group_viewers': [
                {
                    'id': gviewer.pk,
                    'text': gviewer.name,
                    'selected': gviewer in group_viewers_run_model
                } for gviewer in group_viewers
            ]
        })

        return Response(self.results.results)
