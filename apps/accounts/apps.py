from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'  # Full path to match INSTALLED_APPS
    verbose_name = 'User Management'
