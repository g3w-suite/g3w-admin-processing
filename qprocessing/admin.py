from django.contrib import admin
from .models import QProcessingProject

@admin.register(QProcessingProject)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'model',
    )
