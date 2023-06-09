# coding=utf-8
""""
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-06-09'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from huey.contrib.djhuey import HUEY
from huey.exceptions import TaskException
from huey_monitor.models import TaskModel
from core.api.views import G3WAPIView
from core.api.authentication import CsrfExemptSessionAuthentication
from qprocessing.utils.data import QProcessingModel
from qprocessing.tasks import run_model_task, run_model, run_model_celery_task

class QProcessingRunModelView(G3WAPIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication,
    )

    def post(self, request, **kwargs):
        """
        :param qprocessingproject_pk: int, qprocessing.QProcessingProject model instance pk
        :param project_pk: int, qdjango.Project model instance pk
        """

        params = {}

        # params = {'buffer_distance': 1000,
        #           'ingresso1': p.layer_set.get(qgs_layer_id='buildings_668620c2_602a_4ada_9b4f_546eb690db1c').datasource,
        #           'layer_bufferd': result_path}

        task = run_model_task(kwargs['qprocessingproject_pk'], kwargs['project_pk'], params)

        self.results.results.update({
            'data': {
                'task_id': task.id
            }
        })

        return Response(self.results.results)




class QProcessingRunInfoTask(G3WAPIView):
    """
    QProcessing view to get progess state ok a huey/celery task.
    """
    def get(self, request, task_id):

        #TODO: add code for celery tasks.

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