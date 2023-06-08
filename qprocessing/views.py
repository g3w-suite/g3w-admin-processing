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
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from guardian.decorators import permission_required
from huey.contrib.djhuey import HUEY
from huey.exceptions import TaskException
from huey_monitor.models import TaskModel
from core.mixins.views import G3WRequestViewMixin, G3WAjaxDeleteViewMixin
from core.utils.qgisapi import get_qgs_project
from .models import QProcessingProject
from .forms import QProcessingProjectForm
from .utils.data import QProcessingModel
from .tasks import run_model_task, run_model, run_model_celery_task

from qgis.core import QgsProcessingFeedback, QgsProcessingContext

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

class QProcessingProjectDeleteView(G3WAjaxDeleteViewMixin, SingleObjectMixin, View):
    """
    Delete SISPIWorkSiteProject model Ajax view
    """
    model = QProcessingProject
    @method_decorator(
        permission_required('qprocessing.delete_qprocessingproject', (QProcessingProject, 'pk', 'pk'), return_403=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ConsoleFeedBack(QgsProcessingFeedback):

    _error = ''

    def reportError(self, error, fatalError=False):
        self._error = error

from qgis.core import QgsProject, QgsProcessingContext, QgsProcessingFeedback
import os
CURRENT_PATH = os.path.dirname(__file__)
class QProcessingRunTest(View):

    # def get(self, request):
    #
    #     qpm = QProcessingModel(os.path.join(CURRENT_PATH, 'tests/data/test_buffer_layer1.model3'))
    #     prj = QgsProject()
    #     loaded = prj.read(os.path.join(CURRENT_PATH, 'tests/data/test_qgis_328.qgs'))
    #
    #     assert loaded
    #     assert prj.mapLayer('buildings_7783caca_93e9_4c17_9770_1fd8e82f7109').isValid()
    #
    #     # ingresso1 = './buildings.geojson'
    #     ingresso1 = os.path.join(CURRENT_PATH, 'tests/data/buildings.geojson')
    #     result_path = os.path.join(CURRENT_PATH, 'tests/data/processing_result', 'out.shp')
    #
    #     params = {'buffer_distance': 1000,
    #               'ingresso1': ingresso1,
    #               'layer_bufferd': result_path}
    #
    #     ctx = QgsProcessingContext()
    #     ctf = QgsProcessingFeedback()
    #
    #     print(prj)
    #     ctx.setProject(prj)
    #
    #     res = qpm.model.processAlgorithm(params, ctx, ctf)
    #
    #     print(res)
    #     print(ctf.textLog())
    #
    #     return HttpResponse(f'processing result: {json.dumps(res)}')

    def get(self, request):


        qpp = QProcessingProject.objects.all()[1]
        p = qpp.projects.get(pk=339)
        p.qgis_project
        result_path = os.path.join(CURRENT_PATH, 'tests/data/processing_result', 'out.shp')

        params = {'buffer_distance': 1000,
                  'ingresso1': p.layer_set.get(qgs_layer_id='buildings_668620c2_602a_4ada_9b4f_546eb690db1c').datasource,
                  'layer_bufferd': result_path}

        task = run_model_task(qpp.pk, p.pk, params)
        #task = run_model(qpp.pk, p.pk, params)

        #task_id = run_model_celery_task.delay(qpp.pk, p.pk, params)

        return HttpResponse(f'Rrocessing running: {task.id}')


class QProcessingRunInfoTask(View):

    def get(self, request, task_id):

        try:

            # Try to retrieve the task result, may throw an exception
            try:
                result = HUEY.result(task_id)
                ret_status = 200
            except TaskException:
                result = None
                ret_status = 500

            task_model = TaskModel.objects.get(task_id=task_id)
            progress_info = task_model.progress_info

            try:
                progress_percentage = int(
                    100 * progress_info[0] / task_model.total)
            except:
                progress_percentage = 0

            try:
                return JsonResponse({
                    'status': task_model.state.signal_name,
                    'exception': task_model.state.exception_line,
                    'progress': progress_percentage,
                    'task_result': result
                }, status=ret_status)
            except:
                return JsonResponse({
                    'status': 'error',
                    'exception': 'Error retrieving task informations',
                    'progress': 0,
                    'task_result': result,
                }, status=500)

        except TaskModel.DoesNotExist:

            # Handle pending
            pending_task_ids = [task.id for task in HUEY.pending()]

            if task_id in pending_task_ids:
                return JsonResponse({'result': True, 'status': 'pending'})

            return JsonResponse({'result': False, 'error': _('Task not found!')}, status=404)


