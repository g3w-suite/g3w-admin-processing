from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import QProcessingProject

@admin.register(QProcessingProject)
class QProcessingProjectAdmin(GuardedModelAdmin):
    list_display = (
        'pk',
        'model',
    )
