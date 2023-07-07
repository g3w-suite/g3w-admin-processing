# coding=utf-8
""""
    QProcessing actions API views: filter fields etc..
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-07-05'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'


from rest_framework.response import Response
from rest_framework.exceptions import APIException, ValidationError
from core.api.views import G3WAPIView
from core.utils.qgisapi import get_qgis_layer
from qdjango.models import Layer
from qprocessing.utils.formtypes import QProcessingFormTypeField


from qgis.core import \
    QgsFieldModel, \
    QgsFieldProxyModel, \
    QgsProcessingParameterField


class QProcessingActionFieldsView(G3WAPIView):

    def get(self, request, **kwargs):

        # Get Layer
        try:
            layer = get_qgis_layer(
                Layer.objects.get(project__pk=kwargs['project_id'], qgs_layer_id=kwargs['qgs_layer_id'])
            )
        except Exception as e:
            raise APIException(e)

        # Get fields
        if 'datatype' in request.GET:

            # get Type
            types = {}
            for s, t in QProcessingFormTypeField.TYPES.items():
                types[t] = s

            try:

                qpm = QgsFieldProxyModel()
                qpm.sourceModel().setLayer(layer)
                t = request.GET['datatype']
                err_msg = f'the admissible values are: {", ".join([t for t in types.keys()])}'
                if not t:
                    raise ValidationError(f'For datatype {err_msg}')

                if types[t] == QgsProcessingParameterField.Numeric:
                    qpm.setFilters(QgsFieldProxyModel.Numeric)
                elif types[t] == QgsProcessingParameterField.String:
                    qpm.setFilters(QgsFieldProxyModel.String)
                elif types[t] == QgsProcessingParameterField.DateTime:
                    qpm.setFilters(QgsFieldProxyModel.Date | QgsFieldProxyModel.Time)

            except KeyError:
                raise ValidationError(f'\'{t}\' is not a valid datatype, {err_msg}')
            except ValidationError as e:
                raise e
            except Exception as e:
                    raise APIException(e)

            fields = []
            for r in range(0, qpm.rowCount()):
                d = qpm.itemData(qpm.index(r,0))
                fields.append({'key': d[0], 'value':d[2]})

        else:
            fields = [{'key': f.displayName(), 'value':f.name()} for f in layer.fields()]

        self.results.results.update({
            'fields': fields
        })

        return Response(self.results.results)
