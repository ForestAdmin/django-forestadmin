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

    def get_attributes(self, body, fields, fields_name):
        attributes = {}
        for k, v in body.items():
            if k in fields_name:
                attributes[k] = self.format(v, fields[k])
        return attributes

    def populate_attribute(self, body, Model):
        fields = {x.name: x for x in Model._meta.get_fields()}
        fields_name = fields.keys()
        attributes = {}
        attributes.update(self.get_attributes(body['data']['attributes'], fields, fields_name))
        if 'relationships' in body['data']:
            attributes.update(self.get_attributes(body['data']['relationships'], fields, fields_name))

        return attributes
