from __future__ import annotations


def select_search_attrs(
    placeholder: str | None = None,
    *,
    base_class: str | None = None,
    extra_class: str | None = None,
    threshold: int = 1,
    **extra_attrs,
):
    """Reusable attrs for searchable <select> widgets.

    This matches the existing project convention: class `js-select-search` plus
    data-attributes consumed by the frontend helper.
    """

    cls = (
        base_class
        or 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary '
        'focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'
    )

    if 'js-select-search' not in cls:
        cls = (cls + ' js-select-search').strip()

    if extra_class:
        cls = (cls + ' ' + str(extra_class)).strip()

    attrs = {
        'class': cls,
        'data-select-search': 'on',
        'data-search-threshold': str(threshold),
    }

    if placeholder:
        attrs['data-search-placeholder'] = placeholder

    attrs.update(extra_attrs)
    return attrs


def date_ddmmyyyy_attrs(
    placeholder: str | None = None,
    *,
    base_class: str | None = None,
    extra_class: str | None = None,
    **extra_attrs,
):
    cls = (
        base_class
        or 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 '
        'focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'
    )

    if 'js-date-ddmmyyyy' not in cls:
        cls = (cls + ' js-date-ddmmyyyy').strip()

    if extra_class:
        cls = (cls + ' ' + str(extra_class)).strip()

    attrs = {
        'class': cls,
        'inputmode': 'numeric',
        'autocomplete': 'off',
        'data-date-format': 'dd-mm-yyyy',
    }

    if placeholder:
        attrs['placeholder'] = placeholder

    attrs.update(extra_attrs)
    return attrs
