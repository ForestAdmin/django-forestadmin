from django.db.models import Q

from django_forest.tests.models import Question
from django_forest.utils.collection import Collection


# adding smart fields on existing collection
from django_forest.utils.views.base import BaseView


class QuestionForest(Collection):
    def load(self):
        self.fields = [
            {
                'field': 'foo',
                'get': self.foo_get,
                'set': self.foo_set,
                'search': self.search_foo,
                'filter': self.filter_foo,
                'is_filterable': True
            },
            {
                'field': 'bar',
                'get': 'bar_get',
                'set': 'bar_set',
                'search': 'search_bar',
                'filter': 'filter_bar',
                'is_filterable': True
            }
        ]

        self.actions = [
            {
                'name': 'Send invoice',
                'type': 'single',
                'fields': [
                    {
                        'field': 'country',
                        'type': 'Enum',
                        'enums': ['FR', 'US']
                    },
                    {
                        'field': 'phones',
                        'type': ['Enum'],
                        'enums': [['01', '02'], ['998', '999']]
                    },
                    {
                        'field': 'city',
                        'type': 'String',
                        'hook': 'cityChange'
                    },
                    {
                        'field': 'zip code',
                        'type': 'String',
                        'hook': 'zipCodeChange'
                    },
                ],
                'hooks': {
                    'load': self.invoice_load,
                    'change': {
                        'cityChange': self.invoice_change_city,
                        'zipCodeChange': self.invoice_change_zip_code,
                    },
                },
            },
            {
                'name': 'Mark as Live'
            }, {
                'name': 'Generate invoice',
                'download': True,  # If true, the action triggers a file download in the Browser.
            },
        ]

        self.segments = [
            {
                'name': 'Best questions',
                'where': self.best_questions
            }
        ]

    def foo_get(self, obj):
        return f'{obj.question_text}+foo'

    def foo_set(self, obj, value):
        obj.question_text = f'{value}+foo'
        return obj

    def search_foo(self, search):
        return Q(question_text=search)

    def filter_foo(self, operator, value):
        from django_forest.resources.utils.queryset.filters.utils import OPERATORS
        kwargs = {f'question_text{OPERATORS[operator]}': value}
        is_negated = operator.startswith('not')
        if is_negated:
            return ~Q(**kwargs)
        return Q(**kwargs)

    def bar_get(self, obj):
        return f'{obj.question_text}+bar'

    def bar_set(self, obj, value):
        obj.question_text = f'bar+{value}'
        return obj

    def search_bar(self, search):
        return Q(question_text=search)

    def filter_bar(self, operator, value):
        from django_forest.resources.utils.queryset.filters.utils import OPERATORS
        kwargs = {f'question_text{OPERATORS[operator]}': value}
        is_negated = operator.startswith('not')
        if is_negated:
            return ~Q(**kwargs)
        return Q(**kwargs)

    def best_questions(self):
        questions = Question.objects.raw('''SELECT tests_question.id, COUNT(tests_choice.*)
            FROM tests_question
            JOIN tests_choice ON tests_choice.question_id = tests_question.id
            GROUP BY tests_question.id
            ORDER BY count DESC
            LIMIT 5;''')
        return Q(**{'id__in': [question.id for question in questions]})

    def invoice_load(self, fields, request, *args, **kwargs):
        ids = BaseView().get_ids_from_request(request, Question)

        country = next((x for x in fields if x['field'] == 'country'), None)
        country['value'] = 'IT'

        phones = next((x for x in fields if x['field'] == 'phones'), None)
        phones['value'] = ['foo', 'bar']
        return fields

    def invoice_change_city(self, fields, request, changed_field, *args, **kwargs):
        zip_code = next((x for x in fields if x['field'] == 'zip code'), None)
        zip_code['value'] = '83'
        return fields

    def invoice_change_zip_code(self, fields, request, changed_field, *args, **kwargs):
        return fields


Collection.register(QuestionForest, Question)
