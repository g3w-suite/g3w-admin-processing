# coding=utf-8
"""" Main views module
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-18'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from django.views.generic import ListView, CreateView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from guardian.decorators import permission_required
from usersmanage.utils import get_viewers_for_object, get_users_for_object, get_user_groups_for_object
from core.mixins.views import G3WRequestViewMixin, G3WAjaxDeleteViewMixin
from .models import QProcessingProject
from .forms import QProcessingProjectForm



import json


class QProcessingProjectsListView(ListView):
    """List simple qprocessing projects view."""

    template_name = 'qprocessing/projects_list.html'
    model = QProcessingProject

    @method_decorator(permission_required('qprocessing.add_qprocessingproject', return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)



class QProcessingProjectAddView(G3WRequestViewMixin, CreateView):
    """
    Create view for QProcessingProject model
    """
    form_class = QProcessingProjectForm
    template_name = 'qprocessing/project_form.html'
    success_url = reverse_lazy('qprocessing-project-list')

    @method_decorator(permission_required('qprocessing.add_qprocessingproject', return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class QProcessingProjectUpdateView(G3WRequestViewMixin, UpdateView):
    """
    Update view for QProcessingProject model instance
    """
    model = QProcessingProject
    form_class = QProcessingProjectForm
    template_name = 'qprocessing/project_form.html'
    success_url = reverse_lazy('qprocessing-project-list')

    @method_decorator(
        permission_required('qprocessing.change_qprocessingproject', (QProcessingProject, 'pk', 'pk'), return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        self.get_object()
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.object})

        # give initial viewer users and viewer user groups
        viewers = get_viewers_for_object(self.object, self.request.user, 'run_model')
        kwargs['initial']['viewer_users'] = [o.id for o in viewers]
        viewer_groups = get_user_groups_for_object(self.object, self.request.user, 'run_model', 'viewer')
        kwargs['initial']['viewer_user_groups'] = [o.id for o in viewer_groups]

        return kwargs

class QProcessingProjectDeleteView(G3WAjaxDeleteViewMixin, SingleObjectMixin, View):
    """
    Delete SISPIWorkSiteProject model Ajax view
    """
    model = QProcessingProject
    @method_decorator(
        permission_required('qprocessing.delete_qprocessingproject', (QProcessingProject, 'pk', 'pk'), return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)




