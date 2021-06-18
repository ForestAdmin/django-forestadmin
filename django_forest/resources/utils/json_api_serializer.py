from django_forest.utils.json_api_serializer import JsonApiSchema

class JsonApiSerializerMixin:
    def get_only(self, params, Model):
        only = []
        lookup = f'fields[{Model.__name__}]'
        if lookup in params:
            only = params[f'fields[{Model.__name__}]'].split(',')
            sub_only = [x for x in only if f'fields[{x}]' in params]
            for x in sub_only:
                only += [f'{x}.{y}' for y in params[f'fields[{x}]'].split(',')]
                only.append(f'{x}.id')  # marshmallow need an id
                only.remove(x)
        elif 'context[field]' in params:
            only = [x.name for x in Model._meta.get_fields()]

        if 'id' not in only:
            only.append('id')

        return only

    def serialize(self, queryset, resource, Model, params):
        Schema = JsonApiSchema._registry[f'{resource}Schema']

        only = self.get_only(params, Model)
        include_data = [x.name for x in Model._meta.get_fields() if x.is_relation and x.many_to_one]

        if not queryset:
            data = {'data': []}
        else:
            data = Schema(include_data=include_data, only=only).dump(queryset, many=True)

        return data
