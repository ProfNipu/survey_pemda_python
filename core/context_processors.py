"""
Context Processors
Auto-inject variables to all templates
"""
from django.conf import settings


def app_branding(request):
    """
    App branding context processor
    Makes app_name, app_long_name, app_instansi available in ALL templates
    
    Usage in settings.py:
        TEMPLATES = [{
            'OPTIONS': {
                'context_processors': [
                    ...
                    'core.context_processors.app_branding',
                ],
            },
        }]
    
    Then use in templates:
        {{ app_name }}
        {{ app_long_name }}
        {{ app_instansi }}
    """
    return {
        'app_name': getattr(settings, 'APP_NAME', 'aplikasi-test'),
        'app_long_name': getattr(settings, 'APP_LONG_NAME', 'Aplikasi Test'),
        'app_instansi': getattr(settings, 'APP_INSTANSI', 'Instansi'),
        'app_description': getattr(settings, 'APP_DESCRIPTION', 'Aplikasi internal'),
    }
