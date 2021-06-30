from distutils.util import strtobool

from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.associations.utils import AssociationMixin
from django_forest.resources.utils import SmartFieldMixin, QuerysetMixin, JsonApiSerializerMixin, ResourceMixin


class ListView(QuerysetMixin, SmartFieldMixin, ResourceMixin, AssociationMixin, JsonApiSerializerMixin, generic.View):

    def get(self, request, resource, pk, association_resource):
        try:
            Model = self.get_model(resource)
        except Exception as e:
            return self.no_model_error(e)
        else:
            association_field, association_field_name = self.get_association_field(Model, association_resource)

            RelatedModel = association_field.related_model
            params = request.GET.dict()

            # default
            queryset = getattr(Model.objects.get(pk=pk), association_field_name).all()
            queryset = self.enhance_queryset(queryset, RelatedModel, params)

            # handle smart fields
            self.handle_smart_fields(queryset, RelatedModel, many=True)

            # json api serializer
            data = self.serialize(queryset, RelatedModel, params)

            return JsonResponse(data, safe=False)

    def post(self, request, resource, pk, association_resource):
        try:
            Model = self.get_model(resource)
        except Exception as e:
            return self.no_model_error(e)
        else:
            association_field, _ = self.get_association_field(Model, association_resource)

            RelatedModel = association_field.related_model
            body = self.get_body(request.body)
            ids = [x['id'] for x in body['data']]

            instance = Model.objects.get(pk=pk)
            objects, fields_to_update = self.get_association_utils(Model, RelatedModel, ids)
            try:
                self.handle_association(instance, objects, fields_to_update, 'add')
            except Exception as e:
                return JsonResponse({'errors': [str(e)]}, status=400)
            else:
                return JsonResponse({}, safe=False)

    # BelongsTo case
    def put(self, request, resource, pk, association_resource):
        # Notice, ForeignKeys are already handled by the put method in the resource view
        # There is no need to do anything there
        try:
            self.get_model(resource)
        except Exception as e:
            return self.no_model_error(e)
        else:
            return HttpResponse(status=204)

    def dissociate(self, Model, RelatedModel, ids, pk):
        instance = Model.objects.get(pk=pk)
        objects, fields_to_update = self.get_association_utils(Model, RelatedModel, ids)
        try:
            self.handle_association(instance, objects, fields_to_update, 'remove')
        except Exception as e:
            return JsonResponse({'errors': [str(e)]}, status=400)

    def delete(self, request, resource, pk, association_resource):
        try:
            Model = self.get_model(resource)
        except Exception as e:
            return self.no_model_error(e)
        else:
            association_field, _ = self.get_association_field(Model, association_resource)

            RelatedModel = association_field.related_model
            body = self.get_body(request.body)
            ids = [x['id'] for x in body['data']]
            params = request.GET.dict()

            # Notice: Delete
            if 'delete' in params and strtobool(params['delete']):
                # Notice: this does not run pre/post_delete signals
                RelatedModel.objects.filter(pk__in=ids).delete()
            # Notice: Dissociate
            else:
                self.dissociate(Model, RelatedModel, ids, pk)

            return HttpResponse(status=204)
