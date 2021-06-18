import json
from distutils.util import strtobool

from django.http import JsonResponse, HttpResponse
from django.views import generic

from django_forest.resources.associations.utils import get_association_field_name
from django_forest.resources.utils import SmartFieldMixin, EnhanceQuerysetMixin, JsonApiSerializerMixin
from django_forest.utils.models import Models


class IndexView(SmartFieldMixin, EnhanceQuerysetMixin, JsonApiSerializerMixin, generic.View):

    def _get_association_fields(self, Model, association_resource):
        for field in Model._meta.get_fields():
            if field.is_relation and \
                    (field.name == association_resource or
                     field.related_model.__name__.lower() == association_resource.lower()):
                return field
        return None

    def get(self, request, resource, pk, association_resource):
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        association_field = self._get_association_fields(Model, association_resource)
        if association_field is None:
            return JsonResponse({'error': 'cannot find relation'}, safe=False, status=400)

        RelatedModel = association_field.related_model

        params = request.GET.dict()

        # default
        association_field_name = get_association_field_name(association_field)
        queryset = getattr(Model.objects.get(pk=pk), association_field_name).all()
        queryset = self.enhance_queryset(queryset, association_resource, RelatedModel, params)

        # handle smart fields
        self.handle_smart_fields(queryset, association_resource, RelatedModel, many=True)

        # json api serializer
        data = self.serialize(queryset, association_resource, RelatedModel, params)

        return JsonResponse(data, safe=False)

    def post(self, request, resource, pk, association_resource):
        # TODO
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        params = request.GET.dict()

        association_field = self._get_association_fields(Model, association_resource)
        if association_field is None:
            return JsonResponse({'error': 'cannot find relation'}, safe=False, status=400)

        RelatedModel = association_field.related_model

        ids = [x['id'] for x in body['data']]

        instance = Model.objects.get(pk=pk)
        objects = RelatedModel.objects.filter(pk__in=ids)
        fields_to_update = [x for x in RelatedModel._meta.get_fields() if
                            x.is_relation and x.related_model == Model]
        kwargs = {}
        for field in fields_to_update:
            if field.many_to_many:
                for obj in objects:
                    getattr(obj, field.related_name).add(instance)
            else:
                kwargs[field.name] = instance
        try:
            objects.update(**kwargs)
        except Exception:
            return JsonResponse({'errors': ['You cannot dissociate this field']}, status=400)
        else:
            return JsonResponse({}, safe=False)

    # BelongsTo case
    def put(self, request, resource, pk, association_resource):
        # TODO
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        return HttpResponse(status=204)

    def delete(self, request, resource, pk, association_resource):
        Model = Models.get(resource)
        if Model is None:
            return JsonResponse({'message': 'error no model found'}, status=400)

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        params = request.GET.dict()

        association_field = self._get_association_fields(Model, association_resource)
        if association_field is None:
            return JsonResponse({'error': 'cannot find relation'}, safe=False, status=400)

        RelatedModel = association_field.related_model

        ids = [x['id'] for x in body['data']]

        # Notice: Delete
        if 'delete' in params and strtobool(params['delete']):
            # Notice: this does not run pre/post_delete signals
            RelatedModel.objects.filter(pk__in=ids).delete()
        # Notice: Dissociate
        else:
            instance = Model.objects.get(pk=pk)
            objects = RelatedModel.objects.filter(pk__in=ids)
            fields_to_update = [x for x in RelatedModel._meta.get_fields() if
                                x.is_relation and x.related_model == Model]
            kwargs = {}
            for field in fields_to_update:
                if field.many_to_many:
                    for obj in objects:
                        getattr(obj, field.related_name).remove(instance)
                else:
                    kwargs[field.name] = None
            try:
                objects.update(**kwargs)
            except Exception:
                return JsonResponse({'errors': ['You cannot dissociate this field']}, status=400)

        return HttpResponse(status=204)
