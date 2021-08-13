from datetime import datetime, timezone

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.timezone import make_aware


class FormatFieldMixin:
    def get_association_instance(self, association, value):
        pk = value['data']['id']
        try:
            instance = association.related_model.objects.get(pk=pk)
        except ObjectDoesNotExist:
            raise Exception(f'Instance {association.related_model._meta.db_table} with pk {pk} does not exists')
        else:
            return instance

    def handle_foreign_key(self, name, value):
        if value['data'] is not None:
            association = next((x for x in self.Model._meta.get_fields() if x.is_relation and x.name == name), None)
            return self.get_association_instance(association, value)
        return None

    def format(self, name, value, field):
        # TODO other special fields
        if isinstance(field, models.DateTimeField):
            return make_aware(datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ'), timezone.utc)
        elif isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneRel):
            return self.handle_foreign_key(name, value)

        return value

    def get_attributes(self, body, fields):
        attributes = {}
        for k, v in body.items():
            if k in fields.keys():
                attributes[k] = self.format(k, v, fields[k])
        return attributes

    def populate_attribute(self, body):
        fields = {x.name: x for x in self.Model._meta.get_fields() if not x.many_to_many}
        attributes = {}
        for key in ('attributes', 'relationships'):
            if key in body['data']:
                attributes.update(self.get_attributes(body['data'][key], fields))

        return attributes
