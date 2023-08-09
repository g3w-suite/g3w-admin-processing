# coding=utf-8
"""" API REST for upload processing input file
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = "lorenzetti@gis3w.it"
__date__ = "2023-08-09"
__copyright__ = "Copyright 2015 - 2023, Gis3w"
__license__ = "MPL 2.0"

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponseServerError
from django.core.files import File
from django.core.files.storage import default_storage, FileSystemStorage
from rest_framework.response import Response
from core.api.views import G3WAPIView
from core.api.authentication import CsrfExemptSessionAuthentication
from qprocessing.api.permissions import RunModelPermission
from qprocessing.models import QProcessingInputUpload

import os


class QProcessingInputUploadView(G3WAPIView):
    """
    Upload View
    """

    authentication_classes = (
        CsrfExemptSessionAuthentication,
    )
    
    permission_classes = (
        RunModelPermission,
    )


    def post(self, request, *args, **kwargs):

        response_status = 200
        try:
            if not request.FILES:
                return Exception('No FILES are uploaded!')

            to_ret = {}

            # get files
            for file_field, file in request.FILES.items():
                to_ret[file_field] = self.handle_file(file, **kwargs)

            self.results.update({
                'data': to_ret
            })

        except Exception as e:
            self.results.result = False
            self.results.update({"error": str(e)})
            response_status = 500


        return Response(self.results.results, status=response_status)

    def handle_file(self, f, **kwargs):


        # Validate by ext
        # -------------------------------------------------
        ext = os.path.splitext(f.name)[-1][1:].lower()
        formats = [frm['value'] for frm in settings.QPROCESSING_INPUT_UPLOAD_VECTOR_FORMATS]
        if ext not in formats:
            raise Exception(
                f"File type not allowed: {ext}. "
                f'Allowed formats are: {", ".join(formats)}'
            )

        # Save file
        # -------------------------------------------------
        save_path = f"{self.request.user.pk}/" if hasattr(self.request, 'user') else f"nouser/"
        save_path += "uploads/"

        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        File(f)
        storage  = FileSystemStorage(location=settings.QPROCESSING_INPUT_UPLOAD_PATH, base_url=save_path)
        path = storage.save('{}/{}'.format(save_path, f.name), f)


        # Save data into db
        # -------------------------------------------------
        qpia = QProcessingInputUpload.objects.create(user=self.request.user,
                                      name=path.split('/')[-1],
                                      qpp_id=kwargs['qprocessingproject_pk'],
                                      input_name=kwargs['input_name'])

        return qpia.uuid



