from django_forest.utils.schema.json_api_schema import JsonApiSchema


class JsonApiSerializerMixin:
    def get_pk_name(self, Model):
        if Model._meta.pk.name != 'id':
            return 'pk'
        return 'id'

    def get_deep_only(self, params, Model):
        only = params[f'fields[{Model.__name__}]'].split(',')
        sub_only = [x for x in only if f'fields[{x}]' in params]
        for x in sub_only:
            only += [f'{x}.{y}' for y in params[f'fields[{x}]'].split(',')]
            pk_name = self.get_pk_name(Model._meta.get_field(x).related_model)
            only.append(f'{x}.{pk_name}')
            only.remove(x)
        return only

    def get_only(self, params, Model):
        only = []
        lookup = f'fields[{Model.__name__}]'
        if lookup in params:
            only = self.get_deep_only(params, Model)
        if 'context[field]' in params:
            only = [x.name for x in Model._meta.get_fields() if not x.is_relation or (x.many_to_one or x.one_to_one)]

        if 'id' not in only:
            pk_name = self.get_pk_name(Model)
            only.append(pk_name)

        return only

    def get_include_data(self, Model):
        return [x.name for x in Model._meta.get_fields() if x.is_relation and (x.many_to_one or x.one_to_one)]

    def serialize(self, queryset, Model, params):
        Schema = JsonApiSchema._registry[f'{Model.__name__}Schema']

        only = self.get_only(params, Model)
        include_data = self.get_include_data(Model)

        if not queryset:
            data = {'data': []}
        else:
            data = Schema(include_data=include_data, only=only).dump(queryset, many=True)

        return data
