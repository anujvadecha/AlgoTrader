from django.apps import AppConfig


class AlgoappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AlgoApp'

    def ready(self):
        # main = Main()
        pass
