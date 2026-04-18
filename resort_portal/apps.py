from django.apps import AppConfig


import os
class ResortPortalConfig(AppConfig):
    name = 'resort_portal'
    path = os.path.dirname(os.path.abspath(__file__))
