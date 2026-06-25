import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html

from apps.common.table_attrs import dt_actions_attrs, dt_checkbox_attrs, dt_col_attrs, dt_display, dt_render_actions, dt_render_row_number, dt_row_number_attrs

from apps.master_data.models import MsUnitOrganisasi, MsJabatanStruktural, MsJabatanNonStruktural


class _MsUnitOrganisasiBaseTable(tables.Table):
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False,
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    nm_opd = tables.Column(
        verbose_name='Nama Unit',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900', nowrap=False),
    )

    id_opd = tables.Column(
        verbose_name='ID OPD',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    parent_id = tables.Column(
        verbose_name='Parent',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    hierarchy_string = tables.Column(
        verbose_name='Hierarki',
        empty_values=(),
        attrs=dt_col_attrs(td_color='gray-700', nowrap=False),
    )

    level_dinas = tables.Column(
        verbose_name='Dinas',
        empty_values=(),
        attrs=dt_col_attrs(td_color='gray-700', nowrap=False),
    )

    level_bidang = tables.Column(
        verbose_name='Bidang',
        empty_values=(),
        attrs=dt_col_attrs(td_color='gray-700', nowrap=False),
    )

    level_seksi = tables.Column(
        verbose_name='Seksi',
        empty_values=(),
        attrs=dt_col_attrs(td_color='gray-700', nowrap=False),
    )

    status = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='10%'),
    )

    class Meta:
        model = MsUnitOrganisasi
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nm_opd', 'hierarchy_string', 'level_dinas', 'level_bidang', 'level_seksi', 'id_opd', 'parent_id', 'status', 'actions')
        attrs = {
            'id': 'unit_organisasi_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_bkn_nama(self, record):
        bkn_map = getattr(self, 'bkn_map', None) or {}
        info = bkn_map.get((record.id_bkn or '').strip())
        if not info:
            return ''
        return info.get('nama') or ''

    def render_bkn_jenjang(self, record):
        bkn_map = getattr(self, 'bkn_map', None) or {}
        info = bkn_map.get((record.id_bkn or '').strip())
        if not info:
            return ''
        jenjang_list = info.get('jenjang_list') or []
        return ', '.join([str(x) for x in jenjang_list if x])

    def render_actions(self, record):
        edit_url = reverse(self.EDIT_URL_NAME, args=[record.pk])
        delete_url = reverse(self.DELETE_URL_NAME, args=[record.pk])
        return dt_render_actions(
            {
                'url': edit_url,
                'title': 'Edit',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-edit',
            },
            {
                'url': delete_url,
                'title': 'Delete',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
                'confirm': 'Yakin hapus data ini?',
            },
        )

    def render_level_dinas(self, record):
        u = getattr(record, 'nama_opd_ii', None)
        return dt_display(getattr(u, 'nm_opd', None) if u else None)

    def render_level_bidang(self, record):
        u = getattr(record, 'nama_bidang_iii', None)
        return dt_display(getattr(u, 'nm_opd', None) if u else None)

    def render_level_seksi(self, record):
        u = getattr(record, 'nama_sub_bidang_iv', None)
        return dt_display(getattr(u, 'nm_opd', None) if u else None)


class MsJabatanNonStrukturalTable(tables.Table):
    EDIT_URL_NAME = 'manajemen_relasi_organisasi:jabatan_non_struktural_edit'
    DELETE_URL_NAME = 'manajemen_relasi_organisasi:jabatan_non_struktural_delete'

    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False,
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_jabatan_fungsional = tables.Column(
        verbose_name='ID',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    nama_jabatan = tables.Column(
        verbose_name='Nama Jabatan',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900', nowrap=False),
    )

    id_jenis_jabatan = tables.Column(
        verbose_name='Jenis',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    kategori_jabatan = tables.Column(
        verbose_name='Kategori',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    bkn_nama = tables.Column(
        verbose_name='BKN Nama',
        empty_values=(),
        attrs=dt_col_attrs(td_color='gray-700', nowrap=False),
    )

    bkn_jenjang = tables.Column(
        verbose_name='Jenjang',
        empty_values=(),
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700', nowrap=False),
        orderable=False,
    )

    id_status = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='10%'),
    )

    class Meta:
        model = MsJabatanNonStruktural
        template_name = 'django_tables2/tailwind.html'
        fields = (
            'selection',
            'row_number',
            'id_jabatan_fungsional',
            'nama_jabatan',
            'id_jenis_jabatan',
            'kategori_jabatan',
            'id_bkn',
            'bkn_nama',
            'bkn_jenjang',
            'id_status',
            'actions',
        )
        attrs = {
            'id': 'jabatan_non_struktural_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_actions(self, record):
        edit_url = reverse(self.EDIT_URL_NAME, args=[record.pk])
        delete_url = reverse(self.DELETE_URL_NAME, args=[record.pk])
        return dt_render_actions(
            {
                'url': edit_url,
                'title': 'Edit',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-edit',
            },
            {
                'url': delete_url,
                'title': 'Delete',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
                'confirm': 'Yakin hapus data ini?',
            },
        )


class MsUnitOrganisasiTabelTable(_MsUnitOrganisasiBaseTable):
    EDIT_URL_NAME = 'manajemen_relasi_organisasi:unit_organisasi_tabel_edit'
    DELETE_URL_NAME = 'manajemen_relasi_organisasi:unit_organisasi_tabel_delete'


class MsUnitOrganisasiStrukturalTable(_MsUnitOrganisasiBaseTable):
    EDIT_URL_NAME = 'manajemen_relasi_organisasi:unit_organisasi_struktural_edit'
    DELETE_URL_NAME = 'manajemen_relasi_organisasi:unit_organisasi_struktural_delete'


class MsUnitOrganisasiHierarkiTable(tables.Table):
    """Table khusus untuk export dengan format hierarki Dinas-Bidang-Seksi"""
    
    id_opd = tables.Column(
        verbose_name='ID OPD',
    )
    
    nm_opd = tables.Column(
        verbose_name='Nama Unit',
    )
    
    hierarchy_string = tables.Column(
        verbose_name='Hierarki Lengkap',
    )
    
    level_dinas = tables.Column(
        verbose_name='Dinas (Level 0)',
    )
    
    level_bidang = tables.Column(
        verbose_name='Bidang (Level 1)',
    )
    
    level_seksi = tables.Column(
        verbose_name='Seksi (Level 2)',
    )
    
    level_sub_seksi = tables.Column(
        verbose_name='Sub Seksi (Level 3)',
    )
    
    status = tables.Column(
        verbose_name='Status',
    )
    
    class Meta:
        model = MsUnitOrganisasi
        template_name = 'django_tables2/tailwind.html'
        fields = ('id_opd', 'nm_opd', 'hierarchy_string', 'level_dinas', 'level_bidang', 'level_seksi', 'level_sub_seksi', 'status')
        attrs = {
            'class': 'w-full table-auto',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
    
    def render_hierarchy_string(self, record):
        return record.get_hierarchy_string(' → ')
    
    def render_level_dinas(self, record):
        return record.get_level_name(0)
    
    def render_level_bidang(self, record):
        return record.get_level_name(1)
    
    def render_level_seksi(self, record):
        return record.get_level_name(2)
    
    def render_level_sub_seksi(self, record):
        return record.get_level_name(3)


class MsJabatanStrukturalTable(tables.Table):
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False,
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_jabatan = tables.Column(
        verbose_name='ID Jabatan',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    nm_jabatan = tables.Column(
        verbose_name='Nama Jabatan',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900', nowrap=False),
    )

    id_opd = tables.Column(
        verbose_name='ID OPD',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    id_sub_opd = tables.Column(
        verbose_name='ID Sub OPD',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    id_opd_lama = tables.Column(
        verbose_name='ID OPD Lama',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    id_eselon = tables.Column(
        verbose_name='Eselon',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    status = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%', td_color='gray-700'),
    )

    class Meta:
        model = MsJabatanStruktural
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_jabatan', 'nm_jabatan', 'id_opd', 'id_sub_opd', 'id_opd_lama', 'id_eselon', 'status')
        attrs = {
            'id': 'jabatan_struktural_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)
