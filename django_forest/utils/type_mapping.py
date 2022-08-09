TYPE_CHOICES = {
    'AutoField': 'String',
    'BigAutoField': 'Integer',
    'BinaryField': 'String',
    'BooleanField': 'Boolean',
    'CharField': 'String',
    'DateField': 'Dateonly',
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

def handle_one_to_one_field(field):
    if field.target_field.get_internal_type() == 'OneToOneField':
        return TYPE_CHOICES.get(field.target_field.target_field.get_internal_type())
    return TYPE_CHOICES.get(field.target_field.get_internal_type())

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

    field_type = None
    try:
        field_type = field.get_internal_type()
    except AttributeError:
        # Some field as GenericForeignKey hasn't one internal type
        field_type = field.__class__.__name__
    finally:
        # Special case for one to one field which can redirect to an Integer or String
        if field_type == 'OneToOneField':
            return handle_one_to_one_field(field)
        elif field_type == 'ArrayField':
            return [TYPE_CHOICES.get(field.base_field.get_internal_type(), 'unknown')]
        return TYPE_CHOICES.get(field_type, 'unknown')
