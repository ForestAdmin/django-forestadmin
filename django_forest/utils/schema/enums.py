def handle_enums(field, f):
    # TODO handle array of enums?
    if f['type'] == 'Enum':
        choices = field.get_choices() if field.blank else field.choices
        f['enums'] = [x[1] for x in choices]
    return f
