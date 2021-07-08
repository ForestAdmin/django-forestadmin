import copy
import json


class ScopeValidator:
    def __init__(self, scope_filters, users_variable_values):
        self.scope_filters = scope_filters
        self.users_variable_values = users_variable_values

    def is_scope_in_request(self, scope_request):
        if scope_request['filters'] is None:
            return None

        try:
            filters = json.loads(scope_request['filters'])
        except Exception:
            raise Exception('Invalid filters JSON format')
        else:
            # NOTICE: Perform a travel in the request condition filters tree to find the scope
            tagged_scope_filters = self.search_scope_aggregation(filters, scope_request)

            # NOTICE: Permission system always send an aggregator even if there is only one condition
            #         In that case, if the condition is valid, then request was not edited
            if len(self.scope_filters['conditions']) == 1:
                return tagged_scope_filters is not None

            # NOTICE: If there is more than one condition, do a final validation on the condition filters
            return tagged_scope_filters is not None and \
                tagged_scope_filters['aggregator'] == self.scope_filters['aggregator'] and \
                'conditions' in tagged_scope_filters and \
                len(tagged_scope_filters['conditions']) == len(self.scope_filters['conditions'])

    def compute_condition_filters_from_scope(self, user_id):
        computed_condition_filters = copy.deepcopy(self.scope_filters)
        for condition in computed_condition_filters['conditions']:
            if 'value' in condition and \
                    condition['value'] is not None and \
                    isinstance(condition['value'], str) and \
                    condition['value'].startswith('$') and \
                    user_id in self.users_variable_values:
                condition['value'] = self.users_variable_values[user_id][condition['value']]
        return computed_condition_filters

    def search_scope_aggregation(self, filters, scope_request):
        self.ensure_valid_aggregation(filters)

        if 'aggregator' not in filters or not filters['aggregator']:
            return self.is_scope_condition(filters, scope_request)

        # NOTICE: Remove conditions that are not from the scope
        filtered_conditions = [self.search_scope_aggregation(condition, scope_request) for condition in
                               filters['conditions']]

        # NOTICE: If there is only one condition filter left and its current aggregator is
        #         an "and", this condition filter is the searched scope
        if len(filtered_conditions) == 1 and \
                isinstance(filtered_conditions[0], dict) and \
                'aggregator' in filtered_conditions[0] and \
                filters['aggregator'] == 'and':
            return filtered_conditions[0]

        # NOTICE: Otherwise, validate if the current node is the scope and return nil
        #         if it's not
        if len(filtered_conditions) == len(self.scope_filters['conditions']) and \
                filters['aggregator'] == self.scope_filters['aggregator']:
            return {
                'aggregator': filters['aggregator'],
                'conditions': filtered_conditions,
            }

    def ensure_valid_aggregation(self, filters):
        if not isinstance(filters, dict) or not filters:
            raise Exception('Filters cannot be a raw value')

    def is_scope_condition(self, filters, scope_request):
        self.ensure_valid_condition(filters)
        computed_scope = self.compute_condition_filters_from_scope(scope_request['user_id'])
        return filters in computed_scope['conditions']

    def ensure_valid_condition(self, filters):
        if not isinstance(filters, dict) or not filters:
            raise Exception('Condition cannot be a raw value')

        if not isinstance(filters['field'], str) or not isinstance(filters['operator'], str):
            raise Exception('Invalid condition format')
