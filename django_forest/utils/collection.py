from django_forest.utils.schema import Schema


class Collection:
    actions = []
    fields = []
    segments = []

    _registry = {}

    @classmethod
    def register(cls, model, model_forest):
        cls._registry[model.__name__] = model_forest(model)

    def load(self):
        pass

    def handle_smart_fields(self, collection):
        # TODO, this is a dumb implementation
        existing_fields = [f['field'] for f in collection['fields']]
        for field in self.fields:
            if field['field'] in existing_fields:  # update
                collection['fields'] = Schema.get_default_field(field)
            else:  # add
                field.update({'is_virtual': True})
                collection['fields'].append(Schema.get_default_field(field))

    def handle_smart_actions(self, collection):
        pass

    def handle_smart_segments(self, collection):
        pass

    def __init__(self, model):
        self.model = model
        self.load()

        # find resource in Schema
        collection = Schema.get_collection(self.model.__name__)
        self.handle_smart_fields(collection)
        self.handle_smart_actions(collection)
        self.handle_smart_segments(collection)
        # TODO handle smart collection

        super().__init__()
