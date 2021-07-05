import json

from django.views import generic

from django.http import JsonResponse

from .queryset import QuerysetMixin
from django_forest.utils import get_accessor_name
from django_forest.utils.models import Models


class ResourceView(QuerysetMixin, generic.View):
    def error_response(self, e):
        return JsonResponse({'errors': [{'detail': str(e)}]}, status=400)

    def dispatch(self, request, resource, *args, **kwargs):
        try:
            self.Model = self.get_model(resource)
        except Exception as e:
            return self.error_response(e)
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_model(self, resource):
        Model = Models.get(resource)
        if Model is None:
            raise Exception(f'no model found for resource {resource}')
        return Model

    def get_body(self, body):
        body_unicode = body.decode('utf-8')
        return json.loads(body_unicode)

    def get_association_field(self, Model, association_resource):
        association_field = next((x for x in Model._meta.get_fields()
                                  if x.is_relation and get_accessor_name(x) == association_resource), None)
        if association_field is None:
            message = f'cannot find association resource {association_resource} for Model {Model.__name__}'
            raise Exception(message)

        return association_field

    def handle_all_records(self, attributes):
        all_records_ids_excluded = attributes.get('all_records_ids_excluded', [])
        all_records_subset_query = attributes.get('all_records_subset_query', [])
        parent_collection_id = attributes.get('parent_collection_id', None)
        parent_collection_name = attributes.get('parent_collection_name', '')
        parent_association_name = attributes.get('parent_association_name', '')
        if parent_collection_id and parent_collection_name and parent_association_name:
            parent_model = Models.get(parent_collection_name)
            association_field = self.get_association_field(parent_model, parent_association_name)
            RelatedModel = association_field.related_model
            queryset = getattr(parent_model.objects.get(pk=parent_collection_id), parent_association_name).all()
            queryset = self.filter_queryset(queryset, RelatedModel, all_records_subset_query)
        else:
            queryset = self.Model.objects.all()
            queryset = self.filter_queryset(queryset, self.Model, all_records_subset_query)

        return [x for x in queryset.values_list('id', flat=True) if str(x) not in all_records_ids_excluded]

    def get_ids_from_request(self, request):
        body = self.get_body(request.body)

        data = body['data']
        if 'attributes' not in data:
            return [x['id'] for x in body['data']]

        attributes = body['data']['attributes']

        if not attributes.get('all_records', False):
            return attributes.get('ids', [])
        else:
            return self.handle_all_records(attributes)
