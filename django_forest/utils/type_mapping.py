TYPE_CHOICES = {
    'AutoField': 'String',
    'BigAutoField': 'Integer',
    'BinaryField': 'String',
    'BooleanField': 'Boolean',
    'CharField': 'String',
    'DateField': 'DateOnly',
    'DateTimeField': 'Date',
    'DecimalField': 'Float',
    'DurationField': 'Number',
    'FileField': 'String',
    'FilePathField': 'String',
    'FloatField': 'Float',
    'IntegerField': 'Integer',
    'BigIntegerField': 'Integer',
    'IPAddressField': 'String',
    'GenericIPAddressField': 'String',
    'JSONField': 'Json',
    'NullBooleanField': 'Boolean',
    'OneToOneField': 'Integer',
    'PositiveBigIntegerField': 'Integer',
    'PositiveIntegerField': 'Integer',
    'PositiveSmallIntegerField': 'Integer',
    'SlugField': 'String',
    'SmallAutoField': 'String',
    'SmallIntegerField': 'Integer',
    'TextField': 'String',
    'TimeField': 'Time',
    'UUIDField': 'String',
    'CICharField': 'String',
    'CIEmailField': 'String',
    'CITextField': 'String',
    'HStoreField': 'Json',
}


def get_type(field):
    # See connection.data_types (different for each DB Engine)
    # ForestAdmin does not handle range fields: https://www.postgresql.org/docs/9.3/rangetypes.html
    # 'RangeField'
    # 'IntegerRangeField'
    # 'BigIntegerRangeField'
    # 'DecimalRangeField'
    # 'DateTimeRangeField'
    # 'DateRangeField'
    if hasattr(field, 'choices') and field.choices is not None:
        return 'Enum'
    field_type = field.get_internal_type()
    if field_type == 'ArrayField':
        return [TYPE_CHOICES.get(field.base_field.get_internal_type(), 'unknown')]
    return TYPE_CHOICES.get(field_type, 'unknown')
