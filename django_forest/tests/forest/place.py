from django_forest.tests.models import Place
from django_forest.utils.collection import Collection

from django_forest.resources.utils.resource import ResourceView
from django_forest.resources.views import ListView, DetailView

class PlaceForest(Collection):
    def load(self):
        self.fields = [
            {
                'field': 'restaurant',
                "reference": "tests_restaurant.id",
                'type': 'String',
                "filter": self.filter_restaurant,
                "is_filterable": True,

            }
        ]

    def filter_restaurant(self, obj):
        if obj.restaurant:
            return obj.restaurant
        return None

Collection.register(PlaceForest, Place)
