from django.apps import AppConfig


class QprocessingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qprocessing'

    def ready(self):

        # Initialize processing
        from qdjango.apps import QGS_APPLICATION
        import os
        import sys
        from qgis.analysis import QgsNativeAlgorithms

        sys.path.append(os.path.join(QGS_APPLICATION.prefixPath(),
                                     'share', 'qgis', 'python', 'plugins'))

        import processing
        from processing.core.Processing import Processing
        Processing.initialize()
        from processing.algs.gdal.GdalAlgorithmProvider import GdalAlgorithmProvider
        QGS_APPLICATION.processingRegistry().addProvider(
            QgsNativeAlgorithms(QGS_APPLICATION.processingRegistry()))
        QGS_APPLICATION.processingRegistry().addProvider(
            GdalAlgorithmProvider())

