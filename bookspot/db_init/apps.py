from django.apps import AppConfig

class DbInitConfig(AppConfig):
    name = 'db_init'
    verbose_name = "Database Initialization"

    def ready(self):
        from . import signals