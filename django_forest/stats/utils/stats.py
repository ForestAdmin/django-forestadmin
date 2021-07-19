import uuid
from datetime import datetime

from django.http import JsonResponse


class StatsMixin:
    def serialize(self, value):
        if isinstance(value, datetime):
            return value.strftime('%d/%m/%Y')
        return value

    def handle_values(self, _type):
        values = None
        if _type in ('Value', 'Objective'):
            values = self.get_value()
        elif _type == 'Pie':
            values = self.get_pie()
        elif _type == 'Line':
            values = self.get_line()
        elif _type == 'Leaderboard':
            values = self.get_leaderboard()

        return values

    def handle_chart(self):
        res = {
            'data': {
                'attributes': {},
                'type': 'stats',
                'id': uuid.uuid4()
            }}

        if 'type' in self.body:
            res['data']['attributes'] = {
                'value': self.handle_values(self.body['type'])
            }
        return res

    def chart(self):
        try:
            res = self.handle_chart()
        except Exception as e:
            return self.error_response(e)
        else:
            return JsonResponse(res, safe=False)
