from django.apps import AppConfig


class CustomLogicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "custom_logic"

    def ready(self):
        import custom_logic.signals 
