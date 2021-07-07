from django.core.management.commands.runserver import Command as BaseRunserverCommand

from django_forest.utils.cors import set_cors
from django_forest.utils.middlewares import set_middlewares
from django_forest.utils.schema import Schema


class Command(BaseRunserverCommand):

    def inner_run(self, *args, **options):
        set_cors()
        set_middlewares()

        # schema
        Schema.build_schema()
        Schema.add_smart_features()
        Schema.handle_json_api_schema()
        Schema.handle_schema_file()
        Schema.send_apimap()
        super(Command, self).inner_run(*args, **options)
