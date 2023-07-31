# coding=utf-8
"""" QProcessing forms
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-05-18'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from django.forms.models import ModelForm, ValidationError
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field
from django_bleach.forms import BleachField
from django_file_form.forms import FileFormMixin, UploadedFileField
from usersmanage.forms import G3WACLForm
from usersmanage.utils import crispyBoxACL
#from usersmanage.configs import G3W_EDITOR1
from core.mixins.forms import G3WRequestFormMixin, G3WFormMixin
from .models import QProcessingProject
from .utils.data import QProcessingModel
from .utils.exceptions import (
    QProcessingInputException,
    QProcessingOutputException)
import os



class QProcessingProjectForm(FileFormMixin, G3WFormMixin, G3WACLForm, G3WRequestFormMixin, ModelForm):
    """
    Form for QprocessingPro model.
    """

    # TODO: add ACL

    note = BleachField(required=False)

    class Meta:
        model = QProcessingProject
        fields = '__all__'
        field_classes = dict(
            model=UploadedFileField
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
                                Div(
                                    Div(
                                        Div(
                                            Div(
                                                HTML("<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                    _('Project'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                Field('projects', css_class='select2'),
                                                'model',
                                                'model-uploads',
                                                'form_id',
                                                'upload_url',
                                                Field('note', css_class='wys5'),
                                                css_class='box-body',
                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-8'
                                    ),
                                    crispyBoxACL(self,
                                                 editor_field_required=False,
                                                 editor2_field_required=False,
                                                 editor_groups_field_required=False,
                                                 boxCssClass='col-md-4'),
                                    css_class='row'
                                ),
                            )

    def clean_model(self):
        """
        Validate .model3 uploaded
        """

        model = self.cleaned_data['model']

        # Validate file extension
        file_extension = os.path.splitext(model.name)[1]
        if file_extension.lower() not in ('.model3', ):
            raise ValidationError(_("File must have '.model3' extension"))

        if hasattr(self.cleaned_data['model'], 'path'):
            model_file = model.path

        # Case UploadedFileWithId
        elif hasattr(model, 'file'):
            if hasattr(model.file, 'path'):
                model_file = model.file.path
            else:
                model_file = model.file.name

        # Validate the model
        try:
            is_valid, errors = QProcessingModel(model_file).validate()
        except QProcessingInputException as e:
            raise ValidationError(e)
        except QProcessingOutputException as e:
            raise ValidationError(e)

        if not is_valid:
            raise ValidationError(_(f'[Model Validation Errors] - {"; ".join(errors)}'))

        return model

    def save(self, commit=True):
        instance = super().save(commit=commit)

        # set permissions to editor1 and editor2
        self.instance.setPermissionToEditor()

        # set permissions to editor user groups
        self.instance.set_permissions_to_editor_user_groups()

        self._ACLPolicy()

        return instance


