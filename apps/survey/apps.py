from django.apps import AppConfig


class SurveyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.survey'
    verbose_name = 'Survey'
    
    def ready(self):
        """Import signals when app is ready"""
        import apps.survey.signals  # noqa
