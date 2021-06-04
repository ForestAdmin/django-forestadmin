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

Collection.register(QuestionForest, Question)
