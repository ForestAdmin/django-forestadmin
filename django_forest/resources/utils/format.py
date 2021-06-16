from datetime import datetime

from django.db import models

from django_forest.utils.models import Models


class FormatFieldMixin:
    def format(self, value, field):
        # TODO other special fields
        if isinstance(field, models.DateTimeField):
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
        elif isinstance(field, models.ForeignKey):
            Model = Models.get(value['data']['type'])
            if Model is not None:
                return Model.objects.get(pk=value['data']['id'])
            return None

        return value
