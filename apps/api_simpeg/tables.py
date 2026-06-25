"""
Django Tables2 definitions for API SIMPEG
"""
import django_tables2 as tables
from django.utils.html import format_html
from django.urls import reverse


# Import helper functions from common
try:
    from apps.common.table_attrs import (
        dt_checkbox_attrs,
        dt_row_number_attrs,
        dt_col_attrs,
        dt_actions_attrs,
        dt_render_row_number,
        dt_render_badge,
        dt_render_actions,
    )
except ImportError:
    # Fallback if common helpers not available
    def dt_checkbox_attrs(**kwargs):
        return {'th': {'class': 'px-4 py-3'}, 'td': {'class': 'px-4 py-4'}}
    
    def dt_row_number_attrs(**kwargs):
        return {'th': {'class': 'px-4 py-3'}, 'td': {'class': 'px-4 py-4'}}
    
    def dt_col_attrs(**kwargs):
        return {'th': {'class': 'px-4 py-3'}, 'td': {'class': 'px-4 py-4'}}
    
    def dt_actions_attrs(**kwargs):
        return {'th': {'class': 'px-4 py-3'}, 'td': {'class': 'px-4 py-4'}}
    
    def dt_render_row_number(table, column):
        return table.page.start_index() + column
    
    def dt_render_badge(label, **kwargs):
        return format_html('<span class="badge">{}</span>', label)
    
    def dt_render_actions(*links, **kwargs):
        html = ''
        for link in links:
            if link:
                html += f'<a href="{link["url"]}" class="{link.get("a_class", "")}" title="{link.get("title", "")}"><i class="{link.get("icon_class", "")}"></i></a> '
        return format_html(html)


class PegawaiTable(tables.Table):
    """Table for displaying pegawai data from DATABASE"""
    
    selection = tables.CheckBoxColumn(
        accessor='id_pegawai',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )

    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )

    id_pegawai = tables.Column(
        verbose_name='ID',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='5%', td_weight='medium', td_color='gray-700'),
        orderable=True  # Enable sorting
    )

    nip = tables.Column(
        verbose_name='NIP',
        accessor='nip_baru',
        attrs=dt_col_attrs(width='12%', td_weight='medium', td_color='gray-900', nowrap=False),
        orderable=True  # Enable sorting
    )

    nama = tables.Column(
        verbose_name='Nama Pegawai',
        accessor='nama_pegawai',
        attrs=dt_col_attrs(width='18%', td_weight='medium', td_color='gray-900', nowrap=False),
        orderable=True  # Enable sorting
    )

    jabatan = tables.Column(
        verbose_name='Jabatan',
        accessor='nama_jabatan',
        attrs=dt_col_attrs(width='18%', td_color='gray-700', nowrap=False),
        orderable=True  # Enable sorting
    )

    opd = tables.Column(
        verbose_name='OPD',
        accessor='nm_opd',
        attrs=dt_col_attrs(width='15%', td_color='gray-700', nowrap=False),
        orderable=True  # Enable sorting
    )

    golongan = tables.Column(
        verbose_name='Golongan',
        accessor='nama_golongan',
        attrs=dt_col_attrs(width='10%', td_color='gray-700'),
        orderable=True  # Enable sorting
    )

    jenis_kelamin = tables.Column(
        verbose_name='Jenis Kelamin',
        accessor='jenis_kelamin',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%'),
        orderable=True  # Enable sorting
    )

    actions = tables.Column(
        verbose_name='Aksi',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='5%', th_align='center', td_align='center')
    )

    class Meta:
        from .models import Pegawai
        model = Pegawai
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_pegawai', 'nip', 'nama', 'jabatan', 'opd', 'golongan', 'jenis_kelamin', 'actions')
        attrs = {
            'id': 'pegawai_table',  # ID untuk JavaScript
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10  # Default 10 items per page seperti manajemen fungsi

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_nip(self, record):
        """Render NIP column"""
        nip = record.nip_baru or record.nip_lama or '-'
        return format_html('<div class="text-sm font-medium text-gray-900">{}</div>', nip)

    def render_nama(self, record):
        """Render Nama column with tempat/tanggal lahir"""
        nama = record.nama_pegawai or ''
        tempat = record.tempat_lahir or ''
        tanggal = record.tanggal_lahir or ''
        
        html = f'<div class="text-sm font-medium text-gray-900">{nama}</div>'
        if tempat and tanggal:
            html += f'<div class="text-sm text-gray-500">{tempat}, {tanggal}</div>'
        
        return format_html(html)

    def render_jabatan(self, record):
        """Render Jabatan column with masa kerja"""
        jabatan = record.nama_jabatan or '-'
        masa_kerja = record.masa_kerja_jabatan or ''
        
        html = f'<div class="text-sm text-gray-900">{jabatan}</div>'
        if masa_kerja:
            html += f'<div class="text-sm text-gray-500">{masa_kerja}</div>'
        
        return format_html(html)

    def render_opd(self, record):
        """Render OPD column with sub OPD"""
        opd = record.nm_opd or '-'
        sub_opd = record.nm_sub_opd or ''
        
        html = f'<div class="text-sm font-medium text-gray-900">{opd}</div>'
        if sub_opd:
            html += f'<div class="text-sm text-gray-500">{sub_opd}</div>'
        
        return format_html(html)

    def render_golongan(self, record):
        """Render Golongan column with pangkat"""
        golongan = record.nama_golongan or '-'
        pangkat = record.nama_pangkat or ''
        
        html = f'<div class="text-sm text-gray-900">{golongan}</div>'
        if pangkat:
            html += f'<div class="text-sm text-gray-500">{pangkat}</div>'
        
        return format_html(html)

    def render_jenis_kelamin(self, record):
        """Render Jenis Kelamin column with badge"""
        jk = record.jenis_kelamin
        
        if jk == 1:
            return dt_render_badge(
                'L',
                bg_class='bg-blue-100',
                text_class='text-blue-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
            )
        elif jk == 2:
            return dt_render_badge(
                'P',
                bg_class='bg-pink-100',
                text_class='text-pink-800',
                extra_class='text-xs px-2 py-1 rounded font-semibold',
            )
        else:
            return '-'

    def render_actions(self, record, table):
        """Render Actions column"""
        id_pegawai = record.id_pegawai
        
        # Detail button with onclick
        detail_html = format_html(
            '<button onclick="showDetail{}()" class="text-green-600 hover:text-green-800" title="Lihat Detail">'
            '<i class="fas fa-eye"></i>'
            '</button>',
            id_pegawai
        )
        
        return detail_html
