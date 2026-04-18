from django.apps import AppConfig


import os
class VendorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vendors'
    if os.name == 'nt':
        path = os.path.dirname(os.path.abspath(__file__))

    def ready(self):
        import vendors.signals
