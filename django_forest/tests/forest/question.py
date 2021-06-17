from django_forest.tests.models import Question
from django_forest.utils.collection import Collection


# adding smart fields on existing collection
class QuestionForest(Collection):
    def load(self):
        self.fields = [
            {
                'field': 'foo',
                'get': self.foo_get,
                'set': self.foo_set
            },
            {
                'field': 'bar',
                'get': 'bar_get',
                'set': 'bar_set'
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
                        'field': 'city',
                        'type': 'String'
                    },
                    {
                        'field': 'zip code',
                        'type': 'String'
                    },
                ],
                'hooks': {
                    'load': self.invoice_load,
                    'change': {
                        'city': self.invoice_change_city,
                        'zip code': self.invoice_change_zip_code,
                    },
                },
            }
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

    def bar_get(self, obj):
        return f'{obj.question_text}+bar'

    def bar_set(self, obj, value):
        obj.question_text = f'{value}+bar'
        return obj

    def best_questions(self, obj):
        questions = Question.objects.raw('''SELECT question.id, COUNT(choices.*)
            FROM tests_question
            JOIN tests_choices ON tests_choices.question_id = question.id
            GROUP BY question.id
            ORDER BY count DESC
            LIMIT 5;''')
        return {'id__in': [question.id for question in questions]}

    def invoice_load(self, fields, records, *args, **kwargs):
        pass

    def invoice_change_city(self, fields, record, *args, **kwargs):
        pass

    def invoice_change_zip_code(self, fields, record, *args, **kwargs):
        pass


Collection.register(QuestionForest, Question)
