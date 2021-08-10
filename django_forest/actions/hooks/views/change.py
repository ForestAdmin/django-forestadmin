from django_forest.actions.hooks.views.utils import HookView


class ChangeView(HookView):
    def handle_action(self, action, action_name, request):
        body = self.get_body(request.body)
        if self.hook_exists(action, action_name, 'change'):
            changed_field = next((x for x in action['fields'] if x['field'] == body['changedField']), None)
            if changed_field is not None:
                return action['hooks']['change'][changed_field['hook']](body['fields'], request, changed_field)
