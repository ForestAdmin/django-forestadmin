from distutils.util import strtobool

from django.http import JsonResponse, HttpResponse

from django_forest.resources.associations.utils import AssociationView
from django_forest.resources.utils.json_api_serializer import JsonApiSerializerMixin
from django_forest.resources.utils.query_parameters import parse_qs
from django_forest.resources.utils.smart_field import SmartFieldMixin
from django_forest.utils import get_association_field


class ListView(SmartFieldMixin, JsonApiSerializerMixin, AssociationView):

    def get(self, request, pk, association_resource):
        try:
            association_field = get_association_field(self.Model, association_resource)
        except Exception as e:
            return self.error_response(e)
        else:
            RelatedModel = association_field.related_model

            # default
            queryset = getattr(self.Model.objects.get(pk=pk), association_resource).all()

            params = request.GET.dict()
            # enhance queryset
            queryset = self.enhance_queryset(queryset, RelatedModel, params, request)

            # handle smart fields
            self.handle_smart_fields(queryset, RelatedModel._meta.db_table, parse_qs(params), many=True)

            # json api serializer
            data = self.serialize(queryset, RelatedModel, params)

            return JsonResponse(data, safe=False)

    def post(self, request, pk, association_resource):
        try:
            association_field = get_association_field(self.Model, association_resource)
        except Exception as e:
            return self.error_response(e)
        else:
            RelatedModel = association_field.related_model
            body = self.get_body(request.body)
            ids = [x['id'] for x in body['data']]

            instance = self.Model.objects.get(pk=pk)
            objects, fields_to_update = self.get_association_utils(self.Model, RelatedModel, ids)
            self.handle_association(instance, objects, fields_to_update, 'add')
            return JsonResponse({}, safe=False)

    # Notice: BelongsTo case
    def put(self, request, pk, association_resource):
        # Notice, ForeignKeys are already handled by the put method in the resource view
        # There is no need to do anything there
        return HttpResponse(status=204)

    def _dissociate(self, RelatedModel, ids, pk):
        instance = self.Model.objects.get(pk=pk)
        objects, fields_to_update = self.get_association_utils(self.Model, RelatedModel, ids)
        self.handle_association(instance, objects, fields_to_update, 'remove')

    def delete(self, request, pk, association_resource):
        try:
            association_field = get_association_field(self.Model, association_resource)
            ids = self.get_ids_from_request(request, self.Model)
        except Exception as e:
            return self.error_response(e)
        else:
            RelatedModel = association_field.related_model
            params = request.GET.dict()

            # Notice: Delete
            if 'delete' in params and strtobool(params['delete']):
                # Notice: this does not run pre/post_delete signals
                RelatedModel.objects.filter(pk__in=ids).delete()
            # Notice: Dissociate
            else:
                self._dissociate(RelatedModel, ids, pk)

            return HttpResponse(status=204)
