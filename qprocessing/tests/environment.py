from django.test import override_settings

from qprocessing.tests.base import DATASOURCE_PATH


def before_scenario(context, scenario):
    settings_override = override_settings(
        CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'some'}},
        DATASOURCE_PATH=DATASOURCE_PATH,
        LANGUAGE_CODE='en',
        LANGUAGES=(('en', 'English'),),
        PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    )
    settings_override.enable()
    context.add_cleanup(settings_override.disable)
