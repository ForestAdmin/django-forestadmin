from django_forest.tests.models import Question
from django_forest.utils.collection import Collection


class QuestionForest(Collection):
    def load(self):
        self.fields = []


Collection.register(QuestionForest, Question)
