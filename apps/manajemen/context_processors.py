"""
Context processor for building sidebar menus from database-driven MenuItem
with permission-based visibility, inspired by Laravel sidebar.
"""
from typing import Dict, List, Tuple
from django.urls import reverse, NoReverseMatch

from .models import MenuItem, PermissionRule, RoleRule, MenuCategory
from .helpers import has_any_permission, check_permission, is_superadmin


def _parse_permission_key(permission_key: str) -> Tuple[str, str, str]:
    """Parse permission_key into (module, control, function). Missing parts become None."""
    if not permission_key:
        return None, None, None
    parts = [p.strip() for p in permission_key.split('.') if p.strip()]
    module = parts[0] if len(parts) > 0 else None
    control = parts[1] if len(parts) > 1 else None
    function = parts[2] if len(parts) > 2 else None
    return module, control, function


def _user_has_permission_for_key(user, permission_key: str) -> bool:
    """Evaluate permission string against current user.
    Supports forms: 'module', 'module.control', 'module.control.function'.
    """
    if not user.is_authenticated:
        return False
    if is_superadmin(user):
        return True

    module, control, function = _parse_permission_key(permission_key)
    # No key means no direct permission; parent may still be visible via children
    if not module:
        return False

    # module only
    if module and not control and not function:
        return has_any_permission(user, module)

    # module + control
    if module and control and not function:
        user_roles = user.groups.all()
        return RoleRule.objects.filter(
            role__in=user_roles,
            rule__module__nama_module=module,
            rule__control__nama_kontrol=control,
            rule__is_active=True,
            rule__module__is_active=True,
        ).exists()

    # module + control + function
    if module and control and function:
        return check_permission(user, module, control, function)

    return False


def _build_url(item: MenuItem):
    if item.url_name:
        # Primary attempt
        try:
            return reverse(item.url_name)
        except NoReverseMatch:
            # Compatibility fallback: migrate old namespace 'permissions:' → 'manajemen_aplikasi:'
            try:
                if isinstance(item.url_name, str) and item.url_name.startswith('permissions:'):
                    compat_name = item.url_name.replace('permissions:', 'manajemen_aplikasi:', 1)
                    return reverse(compat_name)
            except NoReverseMatch:
                return '#'
            except Exception:
                return '#'
            return '#'
    if item.external_url:
        return item.external_url
    return '#'


def _serialize(item: MenuItem, request, visible_children: List[Dict]):
    """Serialize MenuItem to dict for template consumption."""
    url = _build_url(item)
    active = False
    if getattr(request, 'resolver_match', None):
        try:
            view_name = getattr(request.resolver_match, 'view_name', None)
            if item.url_name:
                # Exact namespaced match only - no prefix matching to avoid confusion
                active = (view_name == item.url_name)
            # URL path exact match only
            if not active and url and url != '#':
                req_path = getattr(request, 'path', '') or ''
                if isinstance(req_path, str) and req_path == url:
                    active = True
        except Exception:
            active = False

    # If any child is active, keep parent active too (important for collapsed sidebar highlight)
    if not active and visible_children:
        try:
            if any(bool(ch.get('active')) for ch in visible_children):
                active = True
        except Exception:
            pass
    return {
        'id': item.id,
        'name': item.name,
        'icon': item.icon or 'fas fa-folder',
        'type': item.type,
        'category': item.category or 0,
        'url': url,
        'active': active,
        'children': visible_children,
    }


def sidebar_menu(request):
    """
    Provide sidebar_groups for dynamic sidebar rendering.
    sidebar_groups = [
      ("SUPER ADMIN", [items...]),
      ("Data Pegawai", [items...]),
      ("Laporan Data", [items...]),
      ("Manajemen Integrasi", [items...]),
      ("Menu Lainnya", [items...]),
    ]
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}

    # Load all active items and build adjacency
    items = list(MenuItem.objects.filter(is_active=True).order_by('category', 'parent_id', 'order', 'name'))
    by_id: Dict[int, MenuItem] = {i.id: i for i in items}
    children_map: Dict[int, List[MenuItem]] = {}
    roots: List[MenuItem] = []

    for i in items:
        if i.parent_id:
            children_map.setdefault(i.parent_id, []).append(i)
        else:
            roots.append(i)

    def build_visible(node: MenuItem):
        # Build visible children first
        child_nodes = []
        for ch in children_map.get(node.id, []):
            built = build_visible(ch)
            if built is not None:
                child_nodes.append(built)

        # Check own permission
        # Rule: if no permission_key and this is a leaf (type != 'menuItem'),
        #       show to any authenticated user (useful for Logout/Profile)
        if node.permission_key:
            has_perm = _user_has_permission_for_key(user, node.permission_key)
        else:
            has_perm = node.type != 'menuItem'
        # Parent-only items (type menuItem) become visible if any child visible
        if node.type == 'menuItem':
            visible = len(child_nodes) > 0 or has_perm
        else:
            visible = has_perm or len(child_nodes) > 0

        if not visible:
            return None

        return _serialize(node, request, child_nodes)

    # Build trees and group by category (dynamic categories)
    cats = {0: []}  # Default bucket for 'Menu Lainnya' and unknown codes

    for r in roots:
        built = build_visible(r)
        if built is None:
            continue
        cats.setdefault(built['category'] or 0, []).append(built)

    # Load dynamic categories; fallback to defaults when table empty
    default_categories = [
        (6, "Beranda"),
        (1, "Pengaturan Sistem"),
        (5, "Master Data"),
        (2, "Data Pegawai"),
        (3, "Laporan Data"),
        (4, "Manajemen Integrasi"),
        (0, "Menu Lainnya"),
    ]

    try:
        db_cats = list(MenuCategory.objects.filter(is_active=True).order_by('order', 'name').values_list('code', 'name'))
    except Exception:
        db_cats = []

    ordered_categories = db_cats if db_cats else default_categories

    # Gather unknown category codes into 'Menu Lainnya'
    known_codes = set(code for code, _ in ordered_categories)
    unknown_items = []
    for code, items_list in list(cats.items()):
        if code != 0 and code not in known_codes:
            unknown_items.extend(items_list)
            cats.pop(code, None)
    # Ensure default bucket exists
    cats.setdefault(0, [])
    cats[0].extend(unknown_items)

    # Build groups list in order
    sidebar_groups = []
    for code, name in ordered_categories:
        group_items = cats.get(code, [])
        sidebar_groups.append((name, group_items))

    # If all groups empty, return nothing (fallback to static menu in template)
    any_items = any(len(group) > 0 for _, group in sidebar_groups)
    if not any_items:
        return {}

    return {
        'sidebar_groups': sidebar_groups,
    }
