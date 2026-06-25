from __future__ import annotations

import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.manajemen.models import ApiDocumentation


def _parse_api_endpoints_markdown() -> list[dict]:
    md_path = Path(getattr(settings, 'BASE_DIR', Path.cwd())) / 'docs' / 'API-ENDPOINTS.md'
    if not md_path.exists():
        return []

    text = md_path.read_text(encoding='utf-8', errors='ignore')
    lines = text.splitlines()

    docs: list[dict] = []

    current_title: str | None = None
    current_url: str | None = None
    current_method: str | None = None
    current_parameters: list[dict] = []
    current_description: str | None = None

    def _flush():
        nonlocal current_title, current_url, current_method, current_parameters, current_description
        if not current_url:
            current_title = None
            current_url = None
            current_method = None
            current_parameters = []
            current_description = None
            return

        params_val = None
        if current_parameters:
            params_val = current_parameters

        docs.append(
            {
                'method_type': (current_method or '').strip() or 'GET',
                'url': current_url.strip(),
                'parameters': params_val,
                'description': (current_description or current_title or '').strip(),
            }
        )

        current_title = None
        current_url = None
        current_method = None
        current_parameters = []
        current_description = None

    in_params = False
    for raw in lines:
        line = raw.strip()

        m = re.match(r'^####\s+\d+\.\s+(.*)$', line)
        if m:
            _flush()
            current_title = m.group(1).strip()
            in_params = False
            continue

        m = re.match(r'^\*\*URL:\*\*\s+`([^`]+)`\s*$', line)
        if m:
            current_url = m.group(1).strip()
            in_params = False
            continue

        m = re.match(r'^\*\*Method:\*\*\s+(.+?)\s*$', line)
        if m:
            method_raw = m.group(1).strip().replace('`', '')
            current_method = method_raw
            in_params = False
            continue

        if line.startswith('**Parameters:**'):
            in_params = True
            continue

        if in_params:
            if not line:
                in_params = False
                continue
            if line.startswith('- '):
                item = line[2:].strip()
                name = item
                desc = ''
                if ' - ' in item:
                    parts = item.split(' - ', 1)
                    name = parts[0].strip()
                    desc = parts[1].strip()
                current_parameters.append({'name': name, 'description': desc})
                continue
            in_params = False

        if current_title and not current_description:
            if line and not line.startswith('**') and not line.startswith('```') and not line.startswith('---'):
                current_description = line

    _flush()

    return docs


class Command(BaseCommand):
    help = 'Seed/sync API Documentation entries from docs/API-ENDPOINTS.md into database (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--deactivate-missing',
            action='store_true',
            help='Set is_active=False for DB entries not present in markdown.',
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('🌱 Seeding API Documentation (from docs/API-ENDPOINTS.md)'))
        self.stdout.write('=' * 70)

        docs = _parse_api_endpoints_markdown()
        if not docs:
            self.stdout.write(self.style.WARNING('No endpoints found. Ensure docs/API-ENDPOINTS.md exists and uses the expected format.'))
            return

        seen_keys: set[tuple[str, str]] = set()
        created = 0
        updated = 0

        for d in docs:
            method_type = (d.get('method_type') or '').strip() or 'GET'
            url = (d.get('url') or '').strip()
            if not url:
                continue

            key = (method_type, url)
            seen_keys.add(key)

            defaults = {
                'parameters': d.get('parameters'),
                'description': d.get('description') or '',
                'is_active': True,
            }

            obj, was_created = ApiDocumentation.objects.get_or_create(
                method_type=method_type,
                url=url,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                changed = False
                for field, val in defaults.items():
                    if getattr(obj, field) != val:
                        setattr(obj, field, val)
                        changed = True
                if not obj.is_active:
                    obj.is_active = True
                    changed = True
                if changed:
                    obj.save(update_fields=['parameters', 'description', 'is_active', 'updated_at'])
                    updated += 1

        deactivated = 0
        if options.get('deactivate_missing'):
            for obj in ApiDocumentation.objects.filter(is_active=True).iterator(chunk_size=200):
                key = (obj.method_type, obj.url)
                if key not in seen_keys:
                    obj.is_active = False
                    obj.save(update_fields=['is_active', 'updated_at'])
                    deactivated += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Done. Created: {created}, Updated: {updated}, Deactivated: {deactivated}'))
