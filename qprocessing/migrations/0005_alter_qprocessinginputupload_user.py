# Generated by Django 3.2.20 on 2023-08-09 14:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qprocessing', '0004_auto_20230809_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qprocessinginputupload',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
