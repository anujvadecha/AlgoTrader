from django.apps import AppConfig
from main import *

class AlgoappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AlgoApp'

    def ready(self):
        # main = Main()
        pass
