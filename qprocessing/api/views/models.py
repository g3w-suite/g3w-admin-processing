# coding=utf-8
""""
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-06-09'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from huey.contrib.djhuey import HUEY
from huey.exceptions import TaskException
from huey_monitor.models import TaskModel
from core.api.views import G3WAPIView
from core.api.authentication import CsrfExemptSessionAuthentication
from usersmanage.utils import get_viewers_for_object, get_users_for_object, get_user_groups_for_object
from usersmanage.configs import G3W_VIEWER2, G3W_VIEWER1
from usersmanage.forms import label_users
from qdjango.models import Project
from qprocessing.utils.data import QProcessingModel
from qprocessing.tasks import run_model_task, run_model, run_model_celery_task
from qprocessing.models import QProcessingProject
from qprocessing.api.permissions import RunModelPermission

from cryptography.fernet import Fernet

import zipfile
import os
import io


class QProcessingRunModelView(G3WAPIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication,
    )

    permission_classes = (
        RunModelPermission,
    )

    def post(self, request, **kwargs):
        """
        :param qprocessingproject_pk: int, qprocessing.QProcessingProject model instance pk
        :param project_pk: int, qdjango.Project model instance pk
        """

        # Asynchronous run
        if settings.QPROCESSING_ASYNC_RUN:

            task = run_model_task(kwargs, request.data, **{'user': request.user})

            # Test celery
            # class tsk:
            #     pass
            # task = tsk()
            # task.id = run_model_celery_task.delay(kwargs, request.data, **{'user_pk': request.user.pk})

            self.results.results.update({
                    'task_id': task.id
            })

        # Synchronous run
        else:

            try:

                res = run_model(kwargs, request.data, **{'user': request.user})
                self.results.results.update({
                    'data': res
                })
            except Exception as e:
                raise APIException(e)

        return Response(self.results.results)



class QProcessingRunInfoTaskView(G3WAPIView):
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

class QProcessingDownLoadOutputView(G3WAPIView):

    permission_classes = (
        RunModelPermission,
    )

    # Extensions for create zip file
    shp_extentions = ('.shp', '.shx', '.dbf', '.prj')

    def _create_zip_file(self, down_path, filename):
        """
        Make a zip file with shape files and send by django reponse.
        """

        # Case shp file
        # Create a zip file
        # ---------------------------------------------------

        path = os.path.dirname(down_path)
        filename_noext = filename.split('.')[0]
        filenames = ["{}{}".format(filename_noext, ftype)
                     for ftype in self.shp_extentions]

        zip_filename = "{}.zip".format(filename_noext)

        # Open BytesIO to grab in-memory ZIP contents
        s = io.BytesIO()

        # The zip compressor
        zf = zipfile.ZipFile(s, "w")

        for fpath in filenames:

            # Add file, at correct path
            ftoadd = os.path.join(path, fpath)
            if os.path.exists(ftoadd):
                zf.write(ftoadd, fpath)

        # Must close zip for all contents to be written
        zf.close()

        # Grab ZIP file from in-memory, make response with correct MIME-type
        response = HttpResponse(
            s.getvalue(), content_type="application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        response.set_cookie('fileDownload', 'true')

        return response

    def get(self, request, qprocessingproject_pk, project_pk, encpath):
        """
        Get encrypted path, download and return file if exists
        """

        # Get path
        f = Fernet(settings.QPROCESSING_CRYPTO_KEY)
        down_path = f.decrypt(encpath.encode()).decode()
        filename = down_path.split('/')[-1]
        ext = filename.split('.')[-1].lower()

        # Get content type by extension
        if ext == 'shp':

            # Custom response for shp
            return self._create_zip_file(down_path, filename)
        elif ext == 'geojson':
            content_type = 'application/json'
        elif ext == 'gpkg':
            content_type = 'application/geopackage+sqlite3'
        elif ext == 'sqlite':
            content_type = 'application / vnd.sqlite3'
        else:
            content_type = 'application/octet-stream'


        response = HttpResponse(open(down_path, 'rb'), content_type=f'{content_type}')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

