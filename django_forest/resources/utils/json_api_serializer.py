class JsonApiSerializerMixin:
    def get_only(self, params, Model):
        only = params[f'fields[{Model.__name__}]'].split(',')
        sub_only = [x for x in only if f'fields[{x}]' in params]
        for x in sub_only:
            only += [f'{x}.{y}' for y in params[f'fields[{x}]'].split(',')]
            only.append(f'{x}.id')  # marshmallow need an id
            only.remove(x)
        return only
