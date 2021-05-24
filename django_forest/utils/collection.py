from django_forest.utils.schema import Schema


class Collection:
    name = None
    actions = []
    fields = []
    segments = []

    _registry = {}

    @classmethod
    def register(cls, model_forest, model=None):
        instance = model_forest(model)
        key = instance.__class__.__name__
        if model is not None:
            key = model.__name__
        elif instance.name is not None:
            key = instance.name
        cls._registry[key] = instance

    def load(self):
        pass

    def handle_smart_fields(self, collection):
        # TODO, this is a dumb implementation
        existing_fields = [f['field'] for f in collection['fields']]
        for field in self.fields:
            if field['field'] in existing_fields:  # update
                # TODO review
                fi = [f for f in collection['fields'] if f['field'] == field['field']][0]
                fi = Schema.get_default_field(fi)
            else:  # add
                field.update({'is_virtual': True})
                collection['fields'].append(Schema.get_default_field(field))

    def handle_smart_actions(self, collection):
        pass

    def handle_smart_segments(self, collection):
        pass

    def __init__(self, model):
        self.load()

        # find resource in Schema
        if model is not None:
            collection = Schema.get_collection(model.__name__)
        else:  # create smart collection
            name = self.__class__.__name__
            if self.name is not None:
                name = self.name
            collection = Schema.get_default_collection({'name': name, 'is_virtual': True})
            Schema.schema['collections'].append(collection)
        self.handle_smart_fields(collection)
        self.handle_smart_actions(collection)
        self.handle_smart_segments(collection)
        # TODO handle smart collection

        super().__init__()
