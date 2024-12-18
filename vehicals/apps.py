from django.apps import AppConfig


class VehicalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vehicals'

    def ready(self):        
        import transport_system.signals