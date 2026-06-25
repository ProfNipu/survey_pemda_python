from django.utils.html import format_html, format_html_join


def _join_classes(*parts):
    return ' '.join([p.strip() for p in parts if p and str(p).strip()])


_TH_BASE = 'px-3 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border border-gray-300'
_TD_BASE = 'px-3 py-3 text-sm border border-gray-300'


def dt_th(*, align='left', width=None, extra_class=''):
    align_class = {
        'left': 'text-left',
        'center': 'text-center',
        'right': 'text-right',
    }.get(align, 'text-left')

    attrs = {'class': _join_classes(_TH_BASE, align_class, extra_class)}
    if width:
        attrs['style'] = f'width: {width}'
    return attrs


def dt_td(*, align='left', nowrap=True, weight=None, color=None, extra_class=''):
    align_class = {
        'left': 'text-left',
        'center': 'text-center',
        'right': 'text-right',
    }.get(align, 'text-left')

    nowrap_class = 'whitespace-nowrap' if nowrap else 'max-w-0 overflow-hidden whitespace-normal break-words'
    weight_class = {
        None: '',
        'normal': 'font-normal',
        'medium': 'font-medium',
        'semibold': 'font-semibold',
        'bold': 'font-bold',
    }.get(weight, '')
    color_class = {
        None: '',
        'gray-900': 'text-gray-900',
        'gray-700': 'text-gray-700',
        'gray-500': 'text-gray-500',
        'gray-800': 'text-gray-800',
    }.get(color, '')

    attrs = {
        'class': _join_classes(_TD_BASE, nowrap_class, align_class, weight_class, color_class, extra_class)
    }
    if not nowrap:
        attrs['style'] = 'white-space: normal !important; word-break: break-word !important; overflow-wrap: anywhere !important;'
    return attrs


def dt_col_attrs(
    *,
    th_align='left',
    td_align='left',
    width=None,
    nowrap=True,
    th_extra_class='',
    td_extra_class='',
    td_weight=None,
    td_color=None,
):
    return {
        'th': dt_th(align=th_align, width=width, extra_class=th_extra_class),
        'td': dt_td(
            align=td_align,
            nowrap=nowrap,
            weight=td_weight,
            color=td_color,
            extra_class=td_extra_class,
        ),
    }


def dt_actions_attrs(*, width='10%', th_align='left', td_align='left'):
    return dt_col_attrs(
        th_align=th_align,
        td_align=td_align,
        width=width,
        nowrap=True,
        td_color='gray-500',
    )


def dt_row_number_attrs(*, width='6%'):
    return dt_col_attrs(
        th_align='center',
        td_align='center',
        width=width,
        nowrap=True,
        td_weight='medium',
        td_color='gray-700',
    )


def dt_checkbox_attrs(*, th_width='3%', td_extra_class=''):
    return {
        'th__input': {
            'id': 'select-all-top',
            'class': 'w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500',
        },
        'td__input': {
            'class': 'row-checkbox w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500'
        },
        'th': dt_th(align='center', width=th_width),
        'td': {
            'class': _join_classes('px-3 py-3 text-center border border-gray-300', td_extra_class),
        },
    }


def dt_checkbox_attrs_with(*, th_width='3%', td_extra_class='', th_input_extra=None, td_input_extra=None):
    attrs = dt_checkbox_attrs(th_width=th_width, td_extra_class=td_extra_class)
    if th_input_extra:
        attrs['th__input'] = {**attrs.get('th__input', {}), **th_input_extra}
    if td_input_extra:
        attrs['td__input'] = {**attrs.get('td__input', {}), **td_input_extra}
    return attrs


def dt_render_row_number(table, owner, *, per_page_default=10, counter_attr='_row_counter'):
    page_number = getattr(table.page, 'number', 1) if hasattr(table, 'page') else 1
    per_page = getattr(table.paginator, 'per_page', per_page_default) if hasattr(table, 'paginator') else per_page_default
    if not hasattr(owner, counter_attr):
        setattr(owner, counter_attr, (page_number - 1) * per_page)
    setattr(owner, counter_attr, getattr(owner, counter_attr) + 1)
    return getattr(owner, counter_attr)


def dt_render_pegawai_identity(p):
    if not p:
        return '-'
    nip_baru = getattr(p, 'nip_baru', None)
    nip_lama = getattr(p, 'nip_lama', None)
    nama = getattr(p, 'nama_display', None) or getattr(p, 'nama_lengkap', None) or str(p)
    parts = [format_html('<div class="font-medium text-gray-900">{}</div>', nama)]
    if nip_baru:
        parts.append(format_html('<div class="text-xs text-gray-600">NIP Baru: {}</div>', nip_baru))
    if nip_lama and (not nip_baru or str(nip_lama) != str(nip_baru)):
        parts.append(format_html('<div class="text-xs text-gray-500">NIP Lama: {}</div>', nip_lama))
    return format_html(''.join([str(x) for x in parts]))


def dt_render_actions(*links, container_class='flex gap-2'):
    items = []
    for link in links:
        if not link:
            continue
        if link.get('html'):
            items.append(format_html('{}', link.get('html')))
            continue
        if not link.get('url'):
            continue
        items.append(
            format_html(
                '<a href="{}" class="{}" title="{}"{}><i class="{}"></i></a>',
                link.get('url'),
                link.get('a_class', ''),
                link.get('title', ''),
                format_html(' onclick="return confirm(\'{}\')"', link.get('confirm')) if link.get('confirm') else '',
                link.get('icon_class', ''),
            )
        )
    return format_html('<div class="{}">{}</div>', container_class, format_html(''.join([str(x) for x in items])))


def dt_display(value, *, default='-'):
    return value if value not in (None, '') else default


def dt_render_badge(
    label,
    *,
    bg_class,
    text_class,
    extra_class='',
    icon_class=None,
):
    if icon_class:
        return format_html(
            '<span class="inline-block {} {} {}"><i class="{} mr-1"></i>{}</span>',
            bg_class,
            text_class,
            extra_class,
            icon_class,
            label,
        )
    return format_html(
        '<span class="inline-block {} {} {}">{}</span>',
        bg_class,
        text_class,
        extra_class,
        label,
    )


def dt_map_status_aktif_nonaktif(value, *, aktif_value='1', aktif_label='Aktif', nonaktif_label='Non Aktif'):
    return aktif_label if str(value) == str(aktif_value) else nonaktif_label


def dt_map_status_dapat_tidak(value, *, dapat_value='D', tidak_value='T', dapat_label='Dapat', tidak_label='Tidak'):
    if str(value) == str(dapat_value):
        return dapat_label
    if str(value) == str(tidak_value):
        return tidak_label
    return dt_display(value)
