from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import QProcessingProject, QProcessingInputUpload

@admin.register(QProcessingProject)
class QProcessingProjectAdmin(GuardedModelAdmin):
    list_display = (
        'pk',
        'model',
    )

@admin.register(QProcessingInputUpload)
class QProcessingInputUploadAdmin(GuardedModelAdmin):
    list_display = (
        'uuid',
        'name',
        'user'
    )
