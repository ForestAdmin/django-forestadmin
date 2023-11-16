from .live_query_segment import LiveQuerySegmentMixin
from django_forest.utils.collection import Collection


class SegmentMixin(LiveQuerySegmentMixin):
    def handle_segment(self, params, Model, queryset):
        if 'segment' in params:
            collection = Collection._registry[Model._meta.db_table]
            segment = next((x for x in collection.segments if x['name'] == params['segment']), None)
            if segment is not None and 'where' in segment:
                queryset = queryset.filter(segment['where']())

        # live query segment
        if "segmentQuery" in params:
            queryset = self.handle_live_query_segment(params['segmentQuery'], Model, queryset)

        return queryset
