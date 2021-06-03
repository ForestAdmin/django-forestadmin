import copy

from django_forest.utils.schema import Schema, COLLECTION

ACTION = {
    'name': '',
    'type': 'bulk',
    'baseUrl': None,
    'endpoint': '',
    'httpMethod': 'POST',
    'redirect': None,
    'download': False,
    'fields': [],
    'hooks': {
        'load': False,
        'change': []
    }
}


class Collection:
    name = None  # TODO warn if set to empty string?
    is_searchable = None
    is_read_only = None
    icon = None
    only_for_relationships = None
    pagination_type = None
    search_fields = None
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

    def get_default_action(self, obj):
        for key, value in copy.deepcopy(ACTION).items():
            obj[key] = value if key not in obj else obj[key]

        return obj

    def override_collection(self, collection):
        for key in [k for k in COLLECTION.keys() if k not in ('fields', 'actions', 'segments')]:
            if hasattr(self, key) and getattr(self, key) is not None:
                collection[key] = getattr(self, key)

    def handle_smart_fields(self, collection):
        existing_fields = [f['field'] for f in collection['fields']]
        for field in self.fields:
            # update
            if field['field'] in existing_fields:
                fi = [f for f in collection['fields'] if f['field'] == field['field']][0]
                fi.update({'is_virtual': True})
            # add
            else:
                field.update({'is_virtual': True})
                collection['fields'].append(Schema.get_default_field(field))

    def handle_action_endpoint(self, action):
        if 'endpoint' not in action:
            return f"/forest/actions/{'-'.join(action['name'].split(' ')).lower()}"
        return action['endpoint']

    def handle_action_fields(self, action):
        res = []
        if 'fields' in action:
            for i, v in enumerate(action['fields']):
                field = Schema.get_default_action_field(v)
                field['position'] = i
                res.append(field)
        return res

    def handle_action_hooks(self, action):
        res = {
            'load': False,
            'change': []
        }
        if 'hooks' in action:
            if 'load' in action['hooks']:
                res['load'] = True  # TODO add validation, has to be a function
            if 'change' in action['hooks']:
                res['change'] = list(action['hooks']['change'].keys())
        return res

    def handle_smart_actions(self, collection):
        # TODO, warn if no name?
        for action in self.actions:
            action.update({
                'endpoint': self.handle_action_endpoint(action),
                'fields': self.handle_action_fields(action),
                'hooks': self.handle_action_hooks(action)
            })
            collection['actions'].append(self.get_default_action(action))

    def handle_smart_segments(self, collection):
        for segment in self.segments:
            collection['segments'].append({'name': segment['name']})

    def __init__(self, model):
        self.load()

        # find resource in Schema
        if model is not None:
            collection = Schema.get_collection(model.__name__)
        # create smart collection
        else:
            collection = Schema.get_default_collection({
                'name': self.__class__.__name__,
                'is_virtual': True
            })
            Schema.schema['collections'].append(collection)

        if collection is not None:
            self.override_collection(collection)
            self.handle_smart_fields(collection)
            self.handle_smart_actions(collection)
            self.handle_smart_segments(collection)

        super().__init__()
