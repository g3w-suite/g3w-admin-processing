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
from django.core.files.storage import FileSystemStorage
from rest_framework.response import Response
from core.api.views import G3WAPIView
from core.api.authentication import CsrfExemptSessionAuthentication
from qprocessing.api.permissions import RunModelPermission
from qprocessing.models import QProcessingInputUpload, QProcessingProject
from qprocessing.utils.formtypes import MAPPING_QPROCESSINGTYPE_FORMTYPE, QProcessingFormTypeException

from zipfile import ZipFile
import os
import tempfile

#Try to fix
try:
    os.path.sep = os.sep
except:
    pass

# Create custom exception

class QProcessingInputUploadValidationException(Exception):
    pass

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

            # Get QProcessingProject and input name
            try:
                self.qpp = QProcessingProject.objects.get(pk=kwargs['qprocessingproject_pk'])
            except:
                raise Exception('QProcessingProject instance not found!')

            try:
                self.qpm = self.qpp.get_qprocessingmodel()
                self.qpi = self.qpm.get_qgsprocessingparameter(kwargs['input_name'])
            except:
                raise Exception(f"{kwargs['input_name']} input not found into the model!")

            # get files
            for file_field, file in request.FILES.items():
                to_ret[file_field] = self.handle_file(file, **kwargs)

            self.results.update({
                'data': to_ret
            })

        except QProcessingInputUploadValidationException as e:
            self.results.result = False
            self.results.update({"error": str(e)})
            response_status = 400

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
            raise QProcessingInputUploadValidationException(
                f"File type not allowed: {ext}. "
                f'Allowed formats are: {", ".join(formats)}'
            )

        # Save file
        # -------------------------------------------------
        save_path = (
            f"{self.request.user.pk}/"
            if hasattr(self.request, "user") and not self.request.user.is_anonymous
            else f"nouser/"
        )
        save_path += "uploads/"
        absolute_save_path = f"{settings.QPROCESSING_INPUT_UPLOAD_PATH}{save_path}"

        if not os.path.isdir(absolute_save_path):
            os.makedirs(absolute_save_path)

        # Zip case for shp files
        # --------------------------------------------------
        if ext == 'zip':
            zipf = ZipFile(f, mode='r')

            # Check for shape files list
            zip_filelist = [os.path.splitext(zf.filename)[-1][1:].lower() for zf in zipf.infolist()]
            diff = list(set(settings.QPROCESSING_INPUT_SHP_EXTS) - set(zip_filelist))
            diff.sort()
            if len(diff):
                raise QProcessingInputUploadValidationException(
                    f"Zip file for shape files is not correct. " 
                    f'Missing the following files type: {", ".join(diff)}'
                )

            # Unzip
            for zf in zipf.infolist():

                # Get path for QProcessingInputUpload
                if os.path.splitext(zf.filename)[-1][1:].lower() == 'shp':
                    path = f"{save_path}{zf.filename}"

            zipf.extractall(path=absolute_save_path)
            zipf.close()

        else:
            File(f)
            storage  = FileSystemStorage(location=settings.QPROCESSING_INPUT_UPLOAD_PATH, base_url=save_path)
            path = storage.save('{}/{}'.format(save_path, f.name), f)


        # Check input data by type
        # --------------------------------------------------------------
        try:
            dop = self.qpm.model.parameterDefinition(self.qpi.parameterName())
            vmap = dop.toVariantMap()
            ftype = MAPPING_QPROCESSINGTYPE_FORMTYPE[vmap['parameter_type']](**vmap)
            ftype.validate_type(f"{settings.QPROCESSING_INPUT_UPLOAD_PATH}{path}")
        except QProcessingFormTypeException as e:
            raise QProcessingInputUploadValidationException(e)


        # Save data into db
        # -------------------------------------------------
        qpia = QProcessingInputUpload.objects.create(
            user=self.request.user if not self.request.user.is_anonymous else None,
            name=path.split('/')[-1],
            qpp_id=kwargs['qprocessingproject_pk'],
            input_name=kwargs['input_name']
        )

        return qpia.uuid



