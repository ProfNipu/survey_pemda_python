import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from django.core.exceptions import ObjectDoesNotExist

from apps.common.table_attrs import dt_actions_attrs, dt_col_attrs, dt_display, dt_map_status_dapat_tidak, dt_render_actions, dt_render_pegawai_identity, dt_render_row_number, dt_row_number_attrs

from apps.pegawai.models import MrAngkaKredit, MrAssessment, MrDiklatFungsional, MrDiklatStruktural, MrDiklatTeknis, MrGajiBerkala, MrHukumanDisiplin, MrJabatan, MrKeluarga, MrKinerja, MrOrtu, MrPangkat, MrPendidikan, MrSeminar, MrSkp, MrTandaJasa, MrTugasLn, MsPegawai, MsTataNaskahPegawai
from apps.manajemen.helpers import check_permission
from apps.master_data.models import BknJabatanFungsional


class MsPegawaiTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    nip = tables.Column(
        verbose_name='NIP',
        accessor='nip',
        attrs=dt_col_attrs(width='18%', td_color='gray-700'),
    )

    nama_lengkap = tables.Column(
        verbose_name='Nama',
        accessor='nama_lengkap',
        attrs=dt_col_attrs(td_weight='medium', td_color='gray-900'),
    )

    id_opd = tables.Column(
        verbose_name='OPD',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700', nowrap=False),
    )

    id_sub_opd = tables.Column(
        verbose_name='Sub OPD',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700', nowrap=False),
    )

    status_pegawai = tables.Column(
        verbose_name='Status',
        accessor='status_pegawai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MsPegawai
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'nip', 'nama_lengkap', 'id_opd', 'id_sub_opd', 'status_pegawai', 'actions')
        attrs = {
            'id': 'ms_pegawai_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_nip(self, value, record):
        nip_baru = getattr(record, 'nip_baru', None)
        nip_lama = getattr(record, 'nip_lama', None)
        parts = []
        if nip_baru:
            parts.append(format_html('<div class="text-sm text-gray-800">{}</div>', nip_baru))
        if nip_lama and (not nip_baru or str(nip_lama) != str(nip_baru)):
            parts.append(format_html('<div class="text-xs text-gray-500">{}</div>', nip_lama))
        return format_html(''.join([str(x) for x in parts])) if parts else '-'

    def render_nama_lengkap(self, value, record):
        nama = getattr(record, 'nama_display', None) or getattr(record, 'nama_lengkap', None) or value
        return format_html('<div class="font-medium text-gray-900">{}</div>', nama or '-')

    def render_status_pegawai(self, value):
        v = str(value or '').strip().upper()
        if v == 'PNS':
            return format_html('<span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">PNS</span>')
        if v == 'CPNS':
            return format_html('<span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800">CPNS</span>')
        if v == 'PPPK':
            return format_html('<span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">PPPK</span>')
        return value

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:ms_pegawai_detail', args=[record.id_pegawai])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MsPegawaiPreviewTable(MsPegawaiTable):
    row_number = MsPegawaiTable.base_columns['row_number']
    nip = MsPegawaiTable.base_columns['nip']
    nama_lengkap = MsPegawaiTable.base_columns['nama_lengkap']
    id_opd = tables.Column(
        verbose_name='OPD',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700', nowrap=False),
    )
    id_sub_opd = tables.Column(
        verbose_name='Sub OPD',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700', nowrap=False),
    )

    jabatan_struktural = tables.Column(
        verbose_name='Jabatan Struktural',
        empty_values=(),
        orderable=False,
        attrs=dt_col_attrs(td_color='gray-700', nowrap=False),
    )
    jabatan_jfu_jft = tables.Column(
        verbose_name='JFU/JFT',
        empty_values=(),
        orderable=False,
        attrs=dt_col_attrs(td_color='gray-700', nowrap=False),
    )

    status_pegawai = MsPegawaiTable.base_columns['status_pegawai']
    actions = MsPegawaiTable.base_columns['actions']

    class Meta:
        model = MsPegawai
        template_name = 'django_tables2/tailwind.html'
        fields = (
            'row_number',
            'nip',
            'nama_lengkap',
            'id_opd',
            'id_sub_opd',
            'jabatan_struktural',
            'jabatan_jfu_jft',
            'status_pegawai',
            'actions',
        )
        attrs = MsPegawaiTable.Meta.attrs
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_nip(self, value, record):
        nip_baru = getattr(record, 'nip_baru', None)
        nip_lama = getattr(record, 'nip_lama', None)
        parts = []
        if nip_baru:
            parts.append(format_html('<div class="text-sm text-gray-800">{}</div>', nip_baru))
        if nip_lama and (not nip_baru or str(nip_lama) != str(nip_baru)):
            parts.append(format_html('<div class="text-xs text-gray-500">{}</div>', nip_lama))
        return format_html(''.join([str(x) for x in parts])) if parts else '-'

    def render_nama_lengkap(self, value, record):
        nama = getattr(record, 'nama_display', None) or getattr(record, 'nama_lengkap', None) or value
        return format_html('<div class="font-medium text-gray-900">{}</div>', nama or '-')

    def render_status_pegawai(self, value):
        v = str(value or '').strip().upper()
        if v == 'PNS':
            return format_html('<span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">PNS</span>')
        if v == 'CPNS':
            return format_html('<span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800">CPNS</span>')
        if v == 'PPPK':
            return format_html('<span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">PPPK</span>')
        return value

    def render_actions(self, record):
        req = getattr(self, 'request', None)
        user = getattr(req, 'user', None) if req else None
        if user is not None and not check_permission(user, 'kepegawaian', 'Ms_pegawai', 'view'):
            return '-'
        detail_url = reverse('manajemen_data_kepegawaian:ms_pegawai_detail', args=[record.id_pegawai])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )

    def render_jabatan_struktural(self, record):
        j = getattr(record, 'id_jabatan', None)
        name = (getattr(j, 'nm_jabatan', None) or '').strip() if j else ''
        return name or '-'

    def render_jabatan_jfu_jft(self, record):
        j = getattr(record, 'id_jfu_jft', None)
        name = (getattr(j, 'nama_jabatan', None) or '').strip() if j else ''

        # If jenis jabatan = 2/3 (Fungsional), append jenjang (if available)
        try:
            jenis_id = getattr(record, 'id_jenis_jabatan_id', None) or getattr(getattr(record, 'id_jenis_jabatan', None), 'id', None)
        except Exception:
            jenis_id = None
        if str(jenis_id or '') in ['2', '3']:
            jenjang = ''

            # Primary: MdJenjangJabatan via MsPegawai.I_07
            try:
                jj = record.I_07
            except ObjectDoesNotExist:
                jj = None
            except Exception:
                jj = None
            if jj is not None:
                jenjang = (getattr(jj, 'nama_jenjang', None) or str(jj) or '').strip()

            if jenjang:
                return f'{name} - {jenjang}' if name else jenjang

        return name or '-'


class MrKinerjaTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    SKP2022_32 = tables.Column(
        verbose_name='Tahun',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    SKP2022_41 = tables.Column(
        verbose_name='Hasil Kinerja',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    SKP2022_43 = tables.Column(
        verbose_name='Perilaku Kerja',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    SKP2022_19 = tables.Column(
        verbose_name='Penilai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    jenis_jabatan = tables.Column(
        verbose_name='Jenis Jabatan',
        empty_values=(),
        orderable=False,
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrKinerja
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'SKP2022_32', 'jenis_jabatan', 'SKP2022_41', 'SKP2022_43', 'SKP2022_19', 'actions')
        attrs = {
            'id': 'mr_kinerja_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_kinerja_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )

    def render_jenis_jabatan(self, record):
        return getattr(record, 'id_jenis_jabatan', None) or '-'


class MrGajiBerkalaTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    MR_GK01 = tables.Column(
        verbose_name='Nomor',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    MR_GK04 = tables.Column(
        verbose_name='TMT',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    MR_GK09 = tables.Column(
        verbose_name='TMT Berikutnya',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    MR_GK11 = tables.Column(
        verbose_name='Gaji Pokok Baru',
        attrs=dt_col_attrs(th_align='right', td_align='right', width='14%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrGajiBerkala
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'MR_GK01', 'MR_GK04', 'MR_GK09', 'MR_GK11', 'actions')
        attrs = {
            'id': 'mr_gaji_berkala_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_gaji_berkala_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrAssessmentTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    MRA_01 = tables.Column(
        verbose_name='Tgl Ujian',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    MRA_02 = tables.Column(
        verbose_name='No Peserta',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    MRA_03 = tables.Column(
        verbose_name='Cognitive',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    MRA_04 = tables.Column(
        verbose_name='Behavior',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrAssessment
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'MRA_01', 'MRA_02', 'MRA_03', 'MRA_04', 'actions')
        attrs = {
            'id': 'mr_assessment_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_assessment_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrTandaJasaTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    JS_03 = tables.Column(
        verbose_name='Tanda Jasa',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    JS_06 = tables.Column(
        verbose_name='Tahun',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    JS_08 = tables.Column(
        verbose_name='Jenis Penghargaan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    JS_04 = tables.Column(
        verbose_name='No SK',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    JS_07 = tables.Column(
        verbose_name='Pemberi',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrTandaJasa
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'JS_03', 'JS_06', 'JS_08', 'JS_04', 'JS_07', 'actions')
        attrs = {
            'id': 'mr_tandajasa_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_tandajasa_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )

    def render_JS_08(self, record):
        return getattr(record, 'JS_08', None) or '-'


class MrTugasLnTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    TG_03 = tables.Column(
        verbose_name='Lokasi',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    TG_04 = tables.Column(
        verbose_name='Jenis Tugas',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    TG_08 = tables.Column(
        verbose_name='Mulai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    TG_09 = tables.Column(
        verbose_name='Selesai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrTugasLn
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'TG_03', 'TG_04', 'TG_08', 'TG_09', 'actions')
        attrs = {
            'id': 'mr_tugas_ln_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_tugas_ln_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrSkpTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    SKP2021_32 = tables.Column(
        verbose_name='Tahun',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    SKP2021_13 = tables.Column(
        verbose_name='Nilai SKP',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    SKP2021_12 = tables.Column(
        verbose_name='Nilai Prestasi',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='14%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrSkp
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'SKP2021_32', 'SKP2021_13', 'SKP2021_12', 'actions')
        attrs = {
            'id': 'mr_skp_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_skp_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrHukumanDisiplinTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    HD_02 = tables.Column(
        verbose_name='No SK',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    HD_03 = tables.Column(
        verbose_name='Tgl SK',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    HD_04 = tables.Column(
        verbose_name='Mulai Hukuman',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    HD_07 = tables.Column(
        verbose_name='Akhir Hukuman',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    jenis_hukuman = tables.Column(
        verbose_name='Jenis Hukuman',
        empty_values=(),
        orderable=False,
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    pangkat = tables.Column(
        verbose_name='Pangkat/Gol',
        empty_values=(),
        orderable=False,
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    nomor_pp = tables.Column(
        verbose_name='Nomor PP',
        empty_values=(),
        orderable=False,
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    tingkat_hukuman = tables.Column(
        verbose_name='Tingkat',
        empty_values=(),
        orderable=False,
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrHukumanDisiplin
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'HD_02', 'HD_03', 'jenis_hukuman', 'pangkat', 'nomor_pp', 'tingkat_hukuman', 'HD_04', 'HD_07', 'actions')
        attrs = {
            'id': 'mr_hukuman_disiplin_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_hukuman_disiplin_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )

    def render_jenis_hukuman(self, record):
        return getattr(record, 'jenis_hukuman_resolved', None) or '-'

    def render_pangkat(self, record):
        return getattr(record, 'pangkat_resolved', None) or '-'

    def render_nomor_pp(self, record):
        return getattr(record, 'nomor_pp_resolved', None) or '-'

    def render_tingkat_hukuman(self, record):
        return getattr(record, 'tingkat_hukuman_resolved', None) or '-'


class MrAngkaKreditTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    AK_01 = tables.Column(
        verbose_name='No SK',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    AK_02 = tables.Column(
        verbose_name='Tgl SK',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    AK_09 = tables.Column(
        verbose_name='Kredit Total Baru',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='14%', td_color='gray-700'),
    )

    AK_13 = tables.Column(
        verbose_name='Riwayat Jabatan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrAngkaKredit
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'AK_01', 'AK_02', 'AK_09', 'AK_13', 'actions')
        attrs = {
            'id': 'mr_angka_kredit_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_angka_kredit_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrSeminarTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_03 = tables.Column(
        verbose_name='Nama Seminar',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_05 = tables.Column(
        verbose_name='Penyelenggara',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_07 = tables.Column(
        verbose_name='Mulai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    LT_08 = tables.Column(
        verbose_name='Selesai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrSeminar
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'LT_03', 'LT_05', 'LT_07', 'LT_08', 'actions')
        attrs = {
            'id': 'mr_seminar_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_seminar_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrDiklatTeknisTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_03 = tables.Column(
        verbose_name='Nama Diklat',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_05 = tables.Column(
        verbose_name='Penyelenggara',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_07 = tables.Column(
        verbose_name='Mulai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    LT_08 = tables.Column(
        verbose_name='Selesai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrDiklatTeknis
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'LT_03', 'LT_05', 'LT_07', 'LT_08', 'actions')
        attrs = {
            'id': 'mr_diklat_teknis_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_diklat_teknis_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrDiklatFungsionalTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_03 = tables.Column(
        verbose_name='Nama Diklat',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_05 = tables.Column(
        verbose_name='Penyelenggara',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_07 = tables.Column(
        verbose_name='Mulai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    LT_08 = tables.Column(
        verbose_name='Selesai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrDiklatFungsional
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'LT_03', 'LT_05', 'LT_07', 'LT_08', 'actions')
        attrs = {
            'id': 'mr_diklat_fungsional_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_diklat_fungsional_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrDiklatStrukturalTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_03 = tables.Column(
        verbose_name='Diklat',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_05 = tables.Column(
        verbose_name='Penyelenggara',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    LT_07 = tables.Column(
        verbose_name='Mulai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    LT_08 = tables.Column(
        verbose_name='Selesai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrDiklatStruktural
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'LT_03', 'LT_05', 'LT_07', 'LT_08', 'actions')
        attrs = {
            'id': 'mr_diklat_struktural_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_diklat_struktural_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrPasanganTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    KF_04 = tables.Column(
        verbose_name='Nama Pasangan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    KF_06 = tables.Column(
        verbose_name='Tgl Nikah',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    KF_07 = tables.Column(
        verbose_name='Tunjangan',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrKeluarga
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'KF_04', 'KF_06', 'KF_07', 'actions')
        attrs = {
            'id': 'mr_pasangan_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_KF_07(self, value):
        return dt_map_status_dapat_tidak(value)

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_pasangan_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrAnakTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    KF_03 = tables.Column(
        verbose_name='Anak Ke-',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    KF_04 = tables.Column(
        verbose_name='Nama Anak',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    KF_05 = tables.Column(
        verbose_name='Tgl Lahir',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    KF_08 = tables.Column(
        verbose_name='Status Anak',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrKeluarga
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'KF_03', 'KF_04', 'KF_05', 'KF_08', 'actions')
        attrs = {
            'id': 'mr_anak_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_KF_08(self, value):
        return dt_display(value)

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_anak_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrPangkatTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    PF_03 = tables.Column(
        verbose_name='Golongan',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='14%', td_color='gray-700'),
    )

    PF_06 = tables.Column(
        verbose_name='TMT',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='14%', td_color='gray-700'),
    )

    PF_04 = tables.Column(
        verbose_name='No SK',
        attrs=dt_col_attrs(td_color='gray-700', nowrap=False),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrPangkat
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'PF_03', 'PF_06', 'PF_04', 'actions')
        attrs = {
            'id': 'mr_pangkat_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_pangkat_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))


class MrOrtuTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    NM_02 = tables.Column(
        verbose_name='Jenis',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    NM_04 = tables.Column(
        verbose_name='Nama Ortu',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    NM_06 = tables.Column(
        verbose_name='Tgl Lahir',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrOrtu
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'NM_02', 'NM_04', 'NM_06', 'actions')
        attrs = {
            'id': 'mr_ortu_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_NM_02(self, value):
        if str(value) == '1':
            return 'Ayah'
        if str(value) == '2':
            return 'Ibu'
        return dt_display(value)

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_ortu_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MsTataNaskahPegawaiTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    PJ_03 = tables.Column(
        verbose_name='Angkatan Prajabatan',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='14%', td_color='gray-700'),
    )

    PJ_04 = tables.Column(
        verbose_name='Mulai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    PJ_05 = tables.Column(
        verbose_name='Selesai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    status = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MsTataNaskahPegawai
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'PJ_03', 'PJ_04', 'PJ_05', 'status', 'actions')
        attrs = {
            'id': 'ms_tata_naskah_pegawai_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:ms_tata_naskah_pegawai_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )


class MrJabatanTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    JF_03 = tables.Column(
        verbose_name='Nama Jabatan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    JF_07 = tables.Column(
        verbose_name='TMT',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='14%', td_color='gray-700'),
    )

    JF_05 = tables.Column(
        verbose_name='No SK',
        attrs=dt_col_attrs(width='18%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrJabatan
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'JF_03', 'JF_07', 'JF_05', 'actions')
        attrs = {
            'id': 'mr_jabatan_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_jabatan_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))


class MrPendidikanTable(tables.Table):
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='6%'),
        orderable=False,
    )

    id_pegawai = tables.Column(
        verbose_name='Pegawai',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    DK_03 = tables.Column(
        verbose_name='Jenjang',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%', td_color='gray-700'),
    )

    DK_05 = tables.Column(
        verbose_name='Sekolah/Universitas',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    DK_04 = tables.Column(
        verbose_name='Jurusan',
        attrs=dt_col_attrs(td_color='gray-700'),
    )

    DK_09 = tables.Column(
        verbose_name='Tgl STTB',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='14%', td_color='gray-700'),
    )

    actions = tables.Column(
        verbose_name='Actions',
        empty_values=(),
        orderable=False,
        attrs=dt_actions_attrs(width='8%'),
    )

    class Meta:
        model = MrPendidikan
        template_name = 'django_tables2/tailwind.html'
        fields = ('row_number', 'id_pegawai', 'DK_03', 'DK_05', 'DK_04', 'DK_09', 'actions')
        attrs = {
            'id': 'mr_pendidikan_table',
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10

    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)

    def render_actions(self, record):
        detail_url = reverse('manajemen_data_kepegawaian:mr_pendidikan_detail', args=[record.id])
        return dt_render_actions(
            {
                'url': detail_url,
                'title': 'Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
        )

    def render_id_pegawai(self, value, record):
        return dt_render_pegawai_identity(getattr(record, 'id_pegawai', None))
