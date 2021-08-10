from django_forest.tests.models import Choice, Topic
from django_forest.utils.collection import Collection


class ChoiceForest(Collection):
    def load(self):
        self.fields = [
            {
                'field': 'topic',
                'reference': 'tests_topic.id',
                'type': 'String',
                'get': self.get_topic,
            }
        ]

    def get_topic(self, obj):
        queryset = Topic.objects.filter(question__in=(obj.question_id,))
        if len(queryset):
            return queryset[0]


Collection.register(ChoiceForest, Choice)
