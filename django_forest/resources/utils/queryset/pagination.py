class PaginationMixin:
    def get_pagination(self, params, queryset):
        if 'page[number]' in params and 'page[size]' in params:
            page_number = int(params['page[number]'])
            page_size = int(params['page[size]'])

            _from = (page_number - 1) * page_size
            _to = page_number * page_size

            return queryset[_from:_to]

        return queryset
