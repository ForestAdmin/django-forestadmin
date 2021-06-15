from datetime import datetime

from django.db import models

from django_forest.utils.models import Models


class FormatFieldMixin:
    def format(self, value, field):
        # TODO other special fields
        if isinstance(field, models.DateTimeField):
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
        elif isinstance(field, models.ForeignKey):
            model = Models.get(value['data']['type'])
            if model:
                return model.objects.get(pk=value['data']['id'])
            return None

        return value
