import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html

from apps.common.table_attrs import dt_actions_attrs, dt_checkbox_attrs, dt_col_attrs, dt_render_actions, dt_render_row_number, dt_row_number_attrs

from apps.manajemen.helpers import check_permission
from apps.master_data.models import (
    MdKategoriPegawai,
    MdAgama,
    MdStatusPerkawinan,
    MdJenjangPendidikan,
    MsDaftarPendidikan,
    MdKedudukanPegawai,
    MdJenisJabatan,
    MdKategoriJabatan,
    MdPangkat,
    MdJenjangJabatan,
    MdEselon,
    MdDiklatStruktural,
    MdJenisSurat,
    MdPejabatMenetapkan,
    MdJenisOrganisasi,
    MdKategoriPemberitahuan,
    MdKategoriPeraturan,
    MdPeraturan,
    MdTentang,
    BknLokasiKerja,
    BknAlasanHukuman,
    BknJenisHukuman,
    BknTingkatHukdis,
    BknNomorppHukdis,
    BknJabatanFungsional,
    BknJenisKenaikanPangkat,
    BknJenisDiklat,
    BknDaftarKppn,
    BknJenisPenghargaan,
    BknJenisMutasi,
    BknJenisPenugasan,
    BknSubJabatan,
)


def _dt_actions_user(table):
    request = getattr(table, 'request', None)
    user = getattr(request, 'user', None)
    if user is None or not getattr(user, 'is_authenticated', False):
        return None
    return user


def _dt_render_actions(record, table, module_name, control_name, edit_url, delete_url):
    user = _dt_actions_user(table)
    can_edit = False
    can_delete = False
    try:
        if user is not None:
            can_edit = check_permission(user, module_name, control_name, 'edit')
            can_delete = check_permission(user, module_name, control_name, 'delete')
    except Exception:
        can_edit = False
        can_delete = False

    edit_link = (
        {
            'url': edit_url,
            'title': 'Edit',
            'a_class': 'text-blue-600 hover:text-blue-800',
            'icon_class': 'fas fa-edit',
        }
        if can_edit
        else None
    )
    delete_link = (
        {
            'url': delete_url,
            'title': 'Delete',
            'a_class': 'text-red-600 hover:text-red-800',
            'icon_class': 'fas fa-trash',
        }
        if can_delete
        else None
    )
    return dt_render_actions(*(link for link in [edit_link, delete_link] if link))


class _BaseMasterDataTable(tables.Table):
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

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)


def _actions_col(width='10%'):
    return tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width=width),
    )


class KategoriPegawaiTable(_BaseMasterDataTable):
    nama_kategori_pegawai = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    keterangan_kategori_pegawai = tables.Column(
        verbose_name='Keterangan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    status = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdKategoriPegawai
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nama_kategori_pegawai', 'keterangan_kategori_pegawai', 'status', 'actions')
        attrs = {'id': 'kategori_pegawai_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:kategori_pegawai_edit', args=[record.id])
        delete_url = reverse('manajemen_data:kategori_pegawai_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_kategori_pegawai', edit_url, delete_url)


class AgamaTable(_BaseMasterDataTable):
    nama_agama = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(th_align='left', td_align='left', width='12%', td_color='gray-700'),
    )
    status = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdAgama
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nama_agama', 'id_bkn', 'status', 'actions')
        attrs = {'id': 'agama_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:agama_edit', args=[record.id])
        delete_url = reverse('manajemen_data:agama_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_agama', edit_url, delete_url)


class StatusPerkawinanTable(_BaseMasterDataTable):
    status_perkawinan = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(th_align='left', td_align='left', width='12%', td_color='gray-700'),
    )
    status = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdStatusPerkawinan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'status_perkawinan', 'id_bkn', 'actions')
        attrs = {'id': 'status_perkawinan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:status_perkawinan_edit', args=[record.id])
        delete_url = reverse('manajemen_data:status_perkawinan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_status_perkawinan', edit_url, delete_url)


class JenjangPendidikanTable(_BaseMasterDataTable):
    kode_tingkat = tables.Column(
        verbose_name='Kode',
        attrs=dt_col_attrs(width='10%', td_weight='medium', td_color='gray-900'),
    )
    tingkat_pendidikan = tables.Column(
        verbose_name='Tingkat Pendidikan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    keterangan = tables.Column(
        verbose_name='Keterangan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    status = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdJenjangPendidikan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'kode_tingkat', 'tingkat_pendidikan', 'keterangan', 'status', 'id_bkn', 'actions')
        attrs = {'id': 'jenjang_pendidikan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:jenjang_pendidikan_edit', args=[record.id])
        delete_url = reverse('manajemen_data:jenjang_pendidikan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_jenjang_pendidikan', edit_url, delete_url)


class DaftarPendidikanTable(_BaseMasterDataTable):
    kode_pendidikan = tables.Column(
        verbose_name='Kode Pendidikan',
        attrs=dt_col_attrs(width='14%', td_weight='medium', td_color='gray-900'),
    )
    kode_tingkat = tables.Column(
        verbose_name='Kode Tingkat',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nm_pendidikan = tables.Column(
        verbose_name='Nama Pendidikan',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    status = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MsDaftarPendidikan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'kode_pendidikan', 'kode_tingkat', 'nm_pendidikan', 'status', 'actions')
        attrs = {'id': 'daftar_pendidikan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:daftar_pendidikan_edit', args=[record.id])
        delete_url = reverse('manajemen_data:daftar_pendidikan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'ms_daftar_pendidikan', edit_url, delete_url)


class KedudukanPegawaiTable(_BaseMasterDataTable):
    nama_kedudukan_pegawai = tables.Column(
        verbose_name='Kedudukan',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    status_hitung = tables.Column(
        verbose_name='Status Hitung',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='14%', td_color='gray-700'),
    )
    nomor_urut = tables.Column(
        verbose_name='No Urut',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdKedudukanPegawai
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nama_kedudukan_pegawai', 'status_hitung', 'nomor_urut', 'actions')
        attrs = {'id': 'kedudukan_pegawai_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:kedudukan_pegawai_edit', args=[record.id])
        delete_url = reverse('manajemen_data:kedudukan_pegawai_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_kedudukan_pegawai', edit_url, delete_url)


class JenisJabatanTable(_BaseMasterDataTable):
    jenis_jabatan = tables.Column(
        verbose_name='Jenis Jabatan',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    urutan = tables.Column(
        verbose_name='Urutan',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdJenisJabatan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'jenis_jabatan', 'urutan', 'id_bkn', 'actions')
        attrs = {'id': 'jenis_jabatan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:jenis_jabatan_edit', args=[record.id])
        delete_url = reverse('manajemen_data:jenis_jabatan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_jenis_jabatan', edit_url, delete_url)


class KategoriJabatanTable(_BaseMasterDataTable):
    kj_02 = tables.Column(
        verbose_name='Kode',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )
    kj_01 = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = MdKategoriJabatan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'kj_02', 'kj_01', 'actions')
        attrs = {'id': 'kategori_jabatan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:kategori_jabatan_edit', args=[record.id])
        delete_url = reverse('manajemen_data:kategori_jabatan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_kategori_jabatan', edit_url, delete_url)


class PangkatTable(_BaseMasterDataTable):
    nama_golongan = tables.Column(
        verbose_name='Golongan',
        attrs=dt_col_attrs(width='15%', td_weight='medium', td_color='gray-900'),
    )
    nama_pangkat = tables.Column(
        verbose_name='Pangkat',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdPangkat
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nama_golongan', 'nama_pangkat', 'actions')
        attrs = {'id': 'pangkat_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:pangkat_edit', args=[record.id])
        delete_url = reverse('manajemen_data:pangkat_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_pangkat', edit_url, delete_url)


class JenjangJabatanTable(_BaseMasterDataTable):
    nama_jenjang = tables.Column(
        verbose_name='Jenjang',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    keterangan = tables.Column(
        verbose_name='Keterangan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdJenjangJabatan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nama_jenjang', 'keterangan', 'actions')
        attrs = {'id': 'jenjang_jabatan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:jenjang_jabatan_edit', args=[record.id])
        delete_url = reverse('manajemen_data:jenjang_jabatan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_jenjang_jabatan', edit_url, delete_url)


class EselonTable(_BaseMasterDataTable):
    eselon = tables.Column(
        verbose_name='Eselon',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    urutan = tables.Column(
        verbose_name='Urutan',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdEselon
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'eselon', 'urutan', 'actions')
        attrs = {'id': 'eselon_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:eselon_edit', args=[record.id])
        delete_url = reverse('manajemen_data:eselon_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_eselon', edit_url, delete_url)


class DiklatStrukturalTable(_BaseMasterDataTable):
    ds_01 = tables.Column(
        verbose_name='Kode',
        accessor='eselon_level',
        attrs=dt_col_attrs(width='12%', td_weight='medium', td_color='gray-900'),
    )
    ds_02 = tables.Column(
        verbose_name='Nama',
        accessor='diklat_struktural',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = MdDiklatStruktural
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'ds_01', 'ds_02', 'actions')
        attrs = {'id': 'diklat_struktural_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:diklat_struktural_edit', args=[record.id])
        delete_url = reverse('manajemen_data:diklat_struktural_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_diklat_struktural', edit_url, delete_url)


class JenisSuratTable(_BaseMasterDataTable):
    js_01 = tables.Column(
        verbose_name='Kode',
        attrs=dt_col_attrs(width='12%', td_weight='medium', td_color='gray-900'),
    )
    js_02 = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    js_03 = tables.Column(
        verbose_name='Keterangan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdJenisSurat
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'js_01', 'js_02', 'js_03', 'actions')
        attrs = {'id': 'jenis_surat_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:jenis_surat_edit', args=[record.id])
        delete_url = reverse('manajemen_data:jenis_surat_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_jenis_surat', edit_url, delete_url)


class PejabatMenetapkanTable(_BaseMasterDataTable):
    kode_pejabat_menetapkan = tables.Column(
        verbose_name='Kode',
        attrs=dt_col_attrs(width='12%', td_weight='medium', td_color='gray-900'),
    )
    pm_01 = tables.Column(
        verbose_name='PM 01',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    pm_02 = tables.Column(
        verbose_name='PM 02',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    pm_03 = tables.Column(
        verbose_name='PM 03',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdPejabatMenetapkan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'kode_pejabat_menetapkan', 'pm_01', 'pm_02', 'pm_03', 'actions')
        attrs = {'id': 'pejabat_menetapkan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:pejabat_menetapkan_edit', args=[record.id])
        delete_url = reverse('manajemen_data:pejabat_menetapkan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_pejabat_menetapkan', edit_url, delete_url)


class JenisOrganisasiTable(_BaseMasterDataTable):
    jo_01 = tables.Column(
        verbose_name='JO 01',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    jo_02 = tables.Column(
        verbose_name='JO 02',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    jo_03 = tables.Column(
        verbose_name='JO 03',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    jo_04 = tables.Column(
        verbose_name='JO 04',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdJenisOrganisasi
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'jo_01', 'jo_02', 'jo_03', 'jo_04', 'actions')
        attrs = {'id': 'jenis_organisasi_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:jenis_organisasi_edit', args=[record.id])
        delete_url = reverse('manajemen_data:jenis_organisasi_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_jenis_organisasi', edit_url, delete_url)


class KategoriPemberitahuanTable(_BaseMasterDataTable):
    nama_kategori_pemberitahuan = tables.Column(
        verbose_name='Kategori',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    status_kategori_pemberitahuan = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdKategoriPemberitahuan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nama_kategori_pemberitahuan', 'status_kategori_pemberitahuan', 'actions')
        attrs = {'id': 'kategori_pemberitahuan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:kategori_pemberitahuan_edit', args=[record.id])
        delete_url = reverse('manajemen_data:kategori_pemberitahuan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_kategori_pemberitahuan', edit_url, delete_url)


class KategoriPeraturanTable(_BaseMasterDataTable):
    KPP_01 = tables.Column(
        verbose_name='KPP 01',
        attrs=dt_col_attrs(width='18%', td_weight='medium', td_color='gray-900'),
    )
    KPP_02 = tables.Column(
        verbose_name='KPP 02',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdKategoriPeraturan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'KPP_01', 'KPP_02', 'actions')
        attrs = {'id': 'kategori_peraturan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:kategori_peraturan_edit', args=[record.id])
        delete_url = reverse('manajemen_data:kategori_peraturan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_kategori_peraturan', edit_url, delete_url)


class PeraturanTable(_BaseMasterDataTable):
    nomor_peraturan = tables.Column(
        verbose_name='Nomor',
        attrs=dt_col_attrs(width='20%', td_weight='medium', td_color='gray-900'),
    )
    judul_peraturan = tables.Column(
        verbose_name='Judul',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    tanggal_peraturan = tables.DateColumn(
        verbose_name='Tanggal',
        format='d-m-Y',
        attrs=dt_col_attrs(width='14%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdPeraturan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nomor_peraturan', 'judul_peraturan', 'tanggal_peraturan', 'actions')
        attrs = {'id': 'peraturan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:peraturan_edit', args=[record.id])
        delete_url = reverse('manajemen_data:peraturan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_peraturan', edit_url, delete_url)


class TentangTable(_BaseMasterDataTable):
    nama_aplikasi = tables.Column(
        verbose_name='Nama Aplikasi',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    versi = tables.Column(
        verbose_name='Versi',
        attrs=dt_col_attrs(width='14%', td_color='gray-700'),
    )
    tahun = tables.Column(
        verbose_name='Tahun',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = MdTentang
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nama_aplikasi', 'versi', 'tahun', 'actions')
        attrs = {'id': 'tentang_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_data:tentang_edit', args=[record.id])
        delete_url = reverse('manajemen_data:tentang_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_data', 'md_tentang', edit_url, delete_url)


# ===================== BKN TABLES =====================

class BknLokasiKerjaTable(_BaseMasterDataTable):
    nama_lokasi = tables.Column(
        verbose_name='Nama Lokasi',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    cepat_kode = tables.Column(
        verbose_name='Cepat Kode',
        attrs=dt_col_attrs(width='14%', td_color='gray-700'),
    )
    kanreg_id = tables.Column(
        verbose_name='Kanreg',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )
    jenis_lokasi = tables.Column(
        verbose_name='Jenis',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = BknLokasiKerja
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nama_lokasi', 'cepat_kode', 'kanreg_id', 'jenis_lokasi', 'actions')
        attrs = {'id': 'bkn_lokasi_kerja_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_lokasi_kerja_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_lokasi_kerja_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_lokasi_kerja', edit_url, delete_url)


class BknAlasanHukumanTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nama = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    keterangan = tables.Column(
        verbose_name='Keterangan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )
    actions = _actions_col()

    class Meta:
        model = BknAlasanHukuman
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'nama', 'keterangan', 'actions')
        attrs = {'id': 'bkn_alasan_hukuman_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_alasan_hukuman_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_alasan_hukuman_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_alasan_hukuman', edit_url, delete_url)


class BknJenisHukumanTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nama = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknJenisHukuman
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'nama', 'actions')
        attrs = {'id': 'bkn_jenis_hukuman_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_hukuman_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_hukuman_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_jenis_hukuman', edit_url, delete_url)


class BknTingkatHukdisTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nama = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknTingkatHukdis
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'nama', 'actions')
        attrs = {'id': 'bkn_tingkat_hukdis_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_tingkat_hukdis_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_tingkat_hukdis_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_tingkat_hukdis', edit_url, delete_url)


class BknNomorppHukdisTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nomor = tables.Column(
        verbose_name='Nomor',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknNomorppHukdis
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'nomor', 'actions')
        attrs = {'id': 'bkn_nomorpp_hukdis_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_nomorpp_hukdis_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_nomorpp_hukdis_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_nomorpp_hukdis', edit_url, delete_url)


class BknJabatanFungsionalTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nama_jabatan = tables.Column(
        verbose_name='Nama',
        accessor='nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknJabatanFungsional
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'nama_jabatan', 'actions')
        attrs = {'id': 'bkn_jabatan_fungsional_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_jabatan_fungsional_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_jabatan_fungsional_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_jabatan_fungsional', edit_url, delete_url)


class BknJenisKenaikanPangkatTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        accessor='id',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nama = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknJenisKenaikanPangkat
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'nama', 'actions')
        attrs = {'id': 'bkn_jenis_kenaikan_pangkat_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_kenaikan_pangkat_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_kenaikan_pangkat_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_jenis_kenaikan_pangkat', edit_url, delete_url)


class BknJenisDiklatTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        accessor='id',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nama = tables.Column(
        verbose_name='Nama',
        accessor='jenis_diklat',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknJenisDiklat
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'nama', 'actions')
        attrs = {'id': 'bkn_jenis_diklat_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_diklat_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_diklat_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_jenis_diklat', edit_url, delete_url)


class BknDaftarKppnTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nama_kppn = tables.Column(
        verbose_name='Nama KPPN',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknDaftarKppn
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'nama_kppn', 'actions')
        attrs = {'id': 'bkn_daftar_kppn_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_daftar_kppn_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_daftar_kppn_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_daftar_kppn', edit_url, delete_url)


class BknJenisPenghargaanTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        accessor='id',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nama = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknJenisPenghargaan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'nama', 'actions')
        attrs = {'id': 'bkn_jenis_penghargaan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_penghargaan_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_penghargaan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_jenis_penghargaan', edit_url, delete_url)


class BknJenisMutasiTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    jm_01 = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknJenisMutasi
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'jm_01', 'actions')
        attrs = {'id': 'bkn_jenis_mutasi_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_mutasi_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_mutasi_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_jenis_mutasi', edit_url, delete_url)


class BknJenisPenugasanTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    jp_01 = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknJenisPenugasan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'jp_01', 'actions')
        attrs = {'id': 'bkn_jenis_penugasan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_penugasan_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_jenis_penugasan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_jenis_penugasan', edit_url, delete_url)


class BknSubJabatanTable(_BaseMasterDataTable):
    id_bkn = tables.Column(
        verbose_name='ID BKN',
        accessor='kel_jabatan_id',
        attrs=dt_col_attrs(width='12%', td_color='gray-700'),
    )
    nama = tables.Column(
        verbose_name='Nama',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )
    actions = _actions_col()

    class Meta:
        model = BknSubJabatan
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'id_bkn', 'nama', 'actions')
        attrs = {'id': 'bkn_sub_jabatan_table', 'class': 'w-full table-auto border-collapse border border-gray-300', 'thead': {'class': 'bg-gray-50'}, 'tbody': {'class': 'bg-white'}}
        per_page = 10

    def render_actions(self, record, table):
        edit_url = reverse('manajemen_referensi_data_bkn:bkn_sub_jabatan_edit', args=[record.id])
        delete_url = reverse('manajemen_referensi_data_bkn:bkn_sub_jabatan_delete', args=[record.id])
        return _dt_render_actions(record, table, 'manajemen_referensi_data_bkn', 'bkn_sub_jabatan', edit_url, delete_url)
