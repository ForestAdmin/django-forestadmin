from django_forest.actions.hooks.views.utils import HookView


class LoadView(HookView):
    def handle_action(self, action, action_name, request):
        if self.hook_exists(action, action_name, 'load'):
            return action['hooks']['load'](action['fields'], request)
