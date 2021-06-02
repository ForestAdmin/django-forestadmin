TYPE_CHOICES = {
    'AutoField': 'String',
    'BigAutoField': 'Number',
    'BinaryField': 'String',
    'BooleanField': 'Boolean',
    'CharField': 'String',
    'DateField': 'DateOnly',
    'DateTimeField': 'Date',
    'DecimalField': 'Number',
    'DurationField': 'Number',
    'FileField': 'String',
    'FilePathField': 'String',
    'FloatField': 'Number',
    'IntegerField': 'Number',
    'BigIntegerField': 'Number',
    'IPAddressField': 'String',
    'GenericIPAddressField': 'String',
    'JSONField': 'Json',
    'NullBooleanField': 'Boolean',
    'OneToOneField': 'Number',
    'PositiveBigIntegerField': 'Number',
    'PositiveIntegerField': 'Number',
    'PositiveSmallIntegerField': 'Number',
    'SlugField': 'String',
    'SmallAutoField': 'String',
    'SmallIntegerField': 'Number',
    'TextField': 'String',
    'TimeField': 'Time',
    'UUIDField': 'String',
    'CICharField': 'String',
    'CIEmailField': 'String',
    'CITextField': 'String',
    'HStoreField': 'Json',
}

def get_type(field_type):
    # TODO handle Enum
    # handle ArrayField
    # handle 'RangeField', 'IntegerRangeField', 'BigIntegerRangeField',
    #     'DecimalRangeField', 'DateTimeRangeField', 'DateRangeField',
    # See connection.data_types (different for each DB Engine)
    return TYPE_CHOICES.get(field_type, 'default')  # TODO raise error, do not put default
