from django.apps import AppConfig


class ManajemenAplikasiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Use flattened module path
    name = 'apps.manajemen'
    # Preserve historical app label used by migrations
    label = 'manajemen_aplikasi'
    verbose_name = 'Manajemen Aplikasi'

    def ready(self):
        # Import signal handlers
        from . import signals  # noqa: F401
