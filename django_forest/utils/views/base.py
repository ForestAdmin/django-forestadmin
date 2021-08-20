import json

from django.http import JsonResponse
from django.views import generic

from django_forest.resources.utils.queryset import QuerysetMixin
from django_forest.utils import get_association_field, get_token
from django_forest.utils.models import Models


class BaseView(QuerysetMixin, generic.View):
    def is_authenticated(self, request):
        try:
            token = get_token(request)
        except Exception:
            return False
        else:
            return token

    def get_body(self, body):
        body_unicode = body.decode('utf-8')
        return json.loads(body_unicode)

    def error_response(self, e):
        return JsonResponse({'errors': [{'detail': str(e)}]}, status=400)

    def get_model(self, resource):
        Model = Models.get(resource)
        if Model is None:
            raise Exception(f'no model found for resource {resource}')
        return Model

    def handle_all_records(self, attributes, Model, request):
        all_records_ids_excluded = attributes.get('all_records_ids_excluded', [])
        all_records_subset_query = attributes.get('all_records_subset_query', [])
        parent_collection_id = attributes.get('parent_collection_id', None)
        parent_collection_name = attributes.get('parent_collection_name', '')
        parent_association_name = attributes.get('parent_association_name', '')
        if parent_collection_id and parent_collection_name and parent_association_name:
            parent_model = Models.get(parent_collection_name)
            association_field = get_association_field(parent_model, parent_association_name)
            RelatedModel = association_field.related_model
            queryset = getattr(parent_model.objects.get(pk=parent_collection_id), parent_association_name).all()
            queryset = self.filter_queryset(queryset, RelatedModel, all_records_subset_query, request)
        else:
            queryset = Model.objects.all()
            queryset = self.filter_queryset(queryset, Model, all_records_subset_query, request)

        return [x for x in queryset.values_list('id', flat=True) if str(x) not in all_records_ids_excluded]

    def get_ids_from_request(self, request, Model):
        body = self.get_body(request.body)

        if 'data' in body:
            data = body['data']
            if 'attributes' not in data:
                return [x['id'] for x in body['data']]
            else:
                attributes = data['attributes']

                if not attributes.get('all_records', False):
                    return attributes.get('ids', [])
                else:
                    return self.handle_all_records(attributes, Model, request)
        elif 'recordIds' in body:
            return body['recordIds']
