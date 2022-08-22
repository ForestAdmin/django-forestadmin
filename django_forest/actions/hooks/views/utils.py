from functools import reduce
from itertools import chain

from django.http import JsonResponse, HttpResponse

from django_forest.utils import get_token
from django_forest.utils.collection import Collection
from django_forest.utils.views.base import BaseView


class HookView(BaseView):

    def action_name_from_endpoint(self, action):
        return str(action['endpoint'].split('/')[-1])

    def hook_exists(self, action, action_name, hook):
        return self.action_name_from_endpoint(action) == action_name and 'hooks' in action and hook in action['hooks']

    def value_in_enums(self, field):
        return next((value for value in field['value'] if value in field['enums']), None)

    def handle_enums(self, field):
        if isinstance(field['type'], list):
            if isinstance(field['value'], list) and self.value_in_enums(field) is None:
                field['value'] = None
        elif field['value'] not in field['enums']:
            field['value'] = None

    def format_enums(self, data):
        for field in data:
            if 'enums' in field and isinstance(field['enums'], list):
                self.handle_enums(field)

    def get_hook_result(self, action_name, request):

        def flatten_actions(all_items):
            return list(chain.from_iterable([items.actions for collection, items in all_items]))

        def get_action(action_registry, requested_action):
            """
            From a flat registry collection, return the
            hook that belongs to this action, or None.
            """
            return reduce(
                lambda all_actions, next_action:
                all_actions | {self.action_name_from_endpoint(next_action): {**next_action}}, action_registry, {}
            ).get(requested_action)

        # Flatten all actions into a single list
        flat_actions = flatten_actions(Collection._registry.items())

        # Get the action whose name matches that which was requested
        action = get_action(flat_actions, action_name)
        if action is None:
            raise Exception('action not found')
        else:
            # TODO smart action field validator
            data = self.handle_action(action, action_name, request)
            self.format_enums(data)
            return data

    def post(self, request, action_name, *args, **kwargs):
        try:
            get_token(request)
        except Exception:
            return HttpResponse(status=403)
        else:
            try:
                data = self.get_hook_result(action_name, request)
            except Exception as e:
                return self.error_response(e)
            else:
                return JsonResponse({'fields': data}, safe=False)
