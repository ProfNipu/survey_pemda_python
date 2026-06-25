from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def auto_seed_after_migrate(sender, **kwargs):
    """Run auto_seed after migrations if database looks empty.
    Safe to run multiple times (idempotent).
    """
    try:
        call_command('auto_seed')
    except Exception:
        # Silently ignore to avoid blocking migrations in CI/prod
        pass
