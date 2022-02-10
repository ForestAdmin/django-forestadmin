class LimitFieldsMixin:
    def handle_fields(self, params, lookup, Model, queryset):
        args = []
        fields_name = [x.name for x in Model._meta.get_fields()]
        for param in params[lookup].split(','):
            if param in fields_name:
                args.append(param)

        return queryset.only(*args)

    def handle_context(self, Model, queryset):
        args = []
        for field in Model._meta.get_fields():
            if not field.is_relation or (field.many_to_one or field.one_to_one):
                args.append(field.name)

        return queryset.only(*args)

    def handle_limit_fields(self, params, Model, queryset):

        lookup = f'fields[{Model._meta.db_table}]'
        if lookup in params:
            queryset = self.handle_fields(params, lookup, Model, queryset)
        return queryset
