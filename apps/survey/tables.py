import django_tables2 as tables
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from apps.common.table_attrs import dt_col_attrs, dt_actions_attrs, dt_checkbox_attrs, dt_row_number_attrs, dt_render_row_number, dt_render_actions
from .models import JenisSurvey, PertanyaanSurvey, RespondenSurvey, JawabanSurvey, PeriodeSurvey, PenilaianJPT


class PenilaianJPTTable(tables.Table):
    """Table untuk Penilaian JPT"""
    
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )
    
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )
    
    nama_dinilai = tables.Column(
        verbose_name='Yang Dinilai',
        attrs=dt_col_attrs(width='20%', td_weight='medium', td_color='gray-900')
    )
    
    nama_penilai = tables.Column(
        verbose_name='Penilai',
        attrs=dt_col_attrs(width='20%', td_weight='medium', td_color='gray-900')
    )
    
    periode = tables.Column(
        empty_values=(),
        verbose_name='Periode',
        attrs=dt_col_attrs(width='15%'),
        orderable=False
    )
    
    rata_rata = tables.Column(
        empty_values=(),
        verbose_name='Rata-rata',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=False
    )
    
    kategori_nilai = tables.Column(
        empty_values=(),
        verbose_name='Kategori',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%'),
        orderable=False
    )
    
    status = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%')
    )
    
    actions = tables.Column(
        empty_values=(),
        verbose_name='Aksi',
        attrs=dt_actions_attrs(width='6%'),
        orderable=False
    )

    class Meta:
        model = PenilaianJPT
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('selection', 'row_number', 'nama_dinilai', 'nama_penilai', 'periode', 'rata_rata', 'kategori_nilai', 'status', 'actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'id': 'survey_jpt_table'
        }

    def render_row_number(self, record, table):
        return dt_render_row_number(record, table)

    def render_periode(self, record):
        """Render periode"""
        return f"{record.periode_mulai.strftime('%d/%m/%Y')} - {record.periode_selesai.strftime('%d/%m/%Y')}"

    def render_rata_rata(self, record):
        """Render rata-rata"""
        return f"{record.rata_rata:.2f}"

    def render_kategori_nilai(self, record):
        """Render kategori nilai dengan badge"""
        kategori = record.kategori_nilai
        if kategori == 'Sangat Baik':
            badge_class = 'bg-green-100 text-green-800'
        elif kategori == 'Baik':
            badge_class = 'bg-blue-100 text-blue-800'
        elif kategori == 'Cukup':
            badge_class = 'bg-yellow-100 text-yellow-800'
        elif kategori == 'Kurang':
            badge_class = 'bg-orange-100 text-orange-800'
        else:
            badge_class = 'bg-red-100 text-red-800'
        
        return format_html(
            '<span class="px-2 py-1 text-xs font-medium rounded-full {}">{}</span>',
            badge_class, kategori
        )

    def render_status(self, record):
        """Render status dengan badge"""
        status_map = {
            'draft': ('bg-gray-100 text-gray-800', 'Draft'),
            'submitted': ('bg-blue-100 text-blue-800', 'Submitted'),
            'reviewed': ('bg-yellow-100 text-yellow-800', 'Reviewed'),
            'approved': ('bg-green-100 text-green-800', 'Approved')
        }
        badge_class, label = status_map.get(record.status, ('bg-gray-100 text-gray-800', record.status))
        
        return format_html(
            '<span class="px-2 py-1 text-xs font-medium rounded-full {}">{}</span>',
            badge_class, label
        )

    def render_actions(self, record, request):
        """Render action buttons with permission checks"""
        from apps.manajemen.helpers import check_permission
        
        user = getattr(request, 'user', None)
        if not user:
            return ''

        actions = []
        
        # View action
        if check_permission(user, 'survey', 'survey_jpt', 'view'):
            actions.append({
                'url': reverse('survey:penilaian_detail', args=[record.id]),
                'icon': 'fas fa-eye',
                'title': 'Lihat Detail',
                'a_class': 'text-blue-600 hover:text-blue-800',
            })
        
        # Edit action
        if check_permission(user, 'survey', 'survey_jpt', 'edit'):
            actions.append({
                'url': reverse('survey:penilaian_edit', args=[record.id]),
                'icon': 'fas fa-edit',
                'title': 'Edit Penilaian',
                'a_class': 'text-orange-600 hover:text-orange-800',
            })
        
        # Delete action
        if check_permission(user, 'survey', 'survey_jpt', 'delete'):
            actions.append({
                'url': reverse('survey:penilaian_delete', args=[record.id]),
                'icon': 'fas fa-trash',
                'title': 'Delete Penilaian',
                'a_class': 'text-red-600 hover:text-red-800',
            })

        return dt_render_actions(actions)


class JenisSurveyTable(tables.Table):
    """Table untuk Jenis Survey"""
    
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )
    
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )
    
    kode = tables.Column(
        verbose_name='Kode',
        attrs=dt_col_attrs(width='15%', td_weight='medium', td_color='gray-900')
    )
    
    nama = tables.Column(
        verbose_name='Nama Survey',
        attrs=dt_col_attrs(width='25%', td_weight='medium', td_color='gray-900')
    )
    
    jumlah_pertanyaan = tables.Column(
        empty_values=(),
        verbose_name='Jumlah Pertanyaan',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='15%'),
        orderable=False,
    )
    
    is_active = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%'),
        orderable=True,
    )
    
    actions = tables.Column(
        empty_values=(),
        verbose_name='Aksi',
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center'),
        orderable=False,
    )
    
    class Meta:
        model = JenisSurvey
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'kode', 'nama', 'jumlah_pertanyaan', 'is_active', 'actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'id': 'jenis_survey_table',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10
    
    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)
    
    def render_jumlah_pertanyaan(self, record):
        count = record.pertanyaan.filter(is_active=True).count()
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">{}</span>',
            count
        )
    
    def render_is_active(self, value):
        if value:
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">'
                '<i class="fas fa-check-circle mr-1"></i> Aktif'
                '</span>'
            )
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">'
            '<i class="fas fa-times-circle mr-1"></i> Nonaktif'
            '</span>'
        )
    
    def render_actions(self, record, table):
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_edit = check_permission(user, 'survey', 'jenis_survey', 'edit')
                can_delete = check_permission(user, 'survey', 'jenis_survey', 'delete')
        except Exception:
            can_edit = False
            can_delete = False

        edit_link = (
            {
                'url': reverse('survey:jenis_survey_edit', args=[record.id]),
                'title': 'Edit Jenis Survey',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )
        delete_link = (
            {
                'url': reverse('survey:jenis_survey_delete', args=[record.id]),
                'title': 'Delete Jenis Survey',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            }
            if can_delete
            else None
        )
        return dt_render_actions(
            *(link for link in [edit_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )


class PertanyaanSurveyTable(tables.Table):
    """Table untuk Pertanyaan Survey"""
    
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )
    
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )
    
    jenis_survey = tables.Column(
        verbose_name='Jenis Survey',
        accessor='jenis_survey__nama',
        attrs=dt_col_attrs(width='20%', td_weight='medium', td_color='gray-900')
    )
    
    kode_pertanyaan = tables.Column(
        verbose_name='Kode',
        attrs=dt_col_attrs(width='12%', td_weight='medium', td_color='gray-700')
    )
    
    pertanyaan = tables.Column(
        verbose_name='Judul Aspek',
        accessor='judul',
        attrs=dt_col_attrs(width='30%', td_color='gray-700')
    )
    
    urutan = tables.Column(
        verbose_name='Urutan',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%')
    )
    
    bobot = tables.Column(
        verbose_name='Bobot',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%')
    )
    
    is_active = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=True,
    )
    
    actions = tables.Column(
        empty_values=(),
        verbose_name='Aksi',
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center'),
        orderable=False,
    )
    
    class Meta:
        model = PertanyaanSurvey
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'jenis_survey', 'kode_pertanyaan', 'pertanyaan', 'urutan', 'bobot', 'is_active', 'actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'id': 'pertanyaan_survey_table',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10
    
    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)
    
    def render_pertanyaan(self, record):
        value = record.judul
        if len(value) > 80:
            return format_html(
                '<span title="{}">{}</span>',
                value,
                value[:80] + '...'
            )
        return value
    
    def render_bobot(self, value):
        return format_html(
            '<span class="font-mono text-sm">{}</span>',
            value
        )
    
    def render_is_active(self, value):
        if value:
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">'
                '<i class="fas fa-check-circle mr-1"></i> Aktif'
                '</span>'
            )
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">'
            '<i class="fas fa-times-circle mr-1"></i> Nonaktif'
            '</span>'
        )
    
    def render_actions(self, record, table):
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_edit = check_permission(user, 'survey', 'pertanyaan_survey', 'edit')
                can_delete = check_permission(user, 'survey', 'pertanyaan_survey', 'delete')
        except Exception:
            can_edit = False
            can_delete = False

        edit_link = (
            {
                'url': reverse('survey:pertanyaan_survey_edit', args=[record.id]),
                'title': 'Edit Pertanyaan Survey',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )
        delete_link = (
            {
                'url': reverse('survey:pertanyaan_survey_delete', args=[record.id]),
                'title': 'Delete Pertanyaan Survey',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            }
            if can_delete
            else None
        )
        return dt_render_actions(
            *(link for link in [edit_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )


class RespondenSurveyTable(tables.Table):
    """Table untuk Responden Survey"""
    
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )
    
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )
    
    nip_pegawaiPenilai = tables.Column(
        verbose_name='NIP Penilai',
        attrs=dt_col_attrs(width='15%', td_weight='medium', td_color='gray-900')
    )
    
    nip_pegawaiDinilai = tables.Column(
        verbose_name='NIP Dinilai',
        attrs=dt_col_attrs(width='15%', td_weight='medium', td_color='gray-900')
    )
    
    peranPenilai = tables.Column(
        verbose_name='Peran Penilai',
        attrs=dt_col_attrs(width='12%', td_color='gray-700')
    )
    
    statusData = tables.Column(
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=True,
    )
    
    jumlah_jawaban = tables.Column(
        empty_values=(),
        verbose_name='Jumlah Jawaban',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%'),
        orderable=False,
    )
    
    created_at = tables.DateTimeColumn(
        format='d M Y H:i',
        verbose_name='Tanggal Dibuat',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='15%')
    )
    
    actions = tables.Column(
        empty_values=(),
        verbose_name='Aksi',
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center'),
        orderable=False,
    )
    
    class Meta:
        model = RespondenSurvey
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'nip_pegawaiPenilai', 'nip_pegawaiDinilai', 'peranPenilai', 'statusData', 'jumlah_jawaban', 'created_at', 'actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'id': 'responden_survey_table',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10
    
    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)
    
    def render_peranPenilai(self, value):
        peran_map = {
            'atasan': ('Atasan', 'bg-blue-100 text-blue-800'),
            'bawahan': ('Bawahan', 'bg-green-100 text-green-800'),
            'rekan': ('Rekan Kerja', 'bg-yellow-100 text-yellow-800'),
            'diri_sendiri': ('Diri Sendiri', 'bg-purple-100 text-purple-800'),
        }
        label, css_class = peran_map.get(value, (value, 'bg-gray-100 text-gray-800'))
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {}">{}</span>',
            css_class, label
        )
    
    def render_statusData(self, value):
        status_map = {
            'draft': ('Draft', 'bg-gray-100 text-gray-800', 'fas fa-edit'),
            'submitted': ('Submitted', 'bg-yellow-100 text-yellow-800', 'fas fa-paper-plane'),
            'completed': ('Completed', 'bg-green-100 text-green-800', 'fas fa-check-circle'),
        }
        label, css_class, icon = status_map.get(value, (value, 'bg-gray-100 text-gray-800', 'fas fa-question'))
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {}">'
            '<i class="{} mr-1"></i> {}'
            '</span>',
            css_class, icon, label
        )
    
    def render_jumlah_jawaban(self, record):
        count = record.jawaban.count()
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">{}</span>',
            count
        )
    
    def render_actions(self, record, table):
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        can_view = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_view = check_permission(user, 'survey', 'responden_survey', 'view')
                can_edit = check_permission(user, 'survey', 'responden_survey', 'edit')
                can_delete = check_permission(user, 'survey', 'responden_survey', 'delete')
        except Exception:
            can_view = False
            can_edit = False
            can_delete = False

        view_link = (
            {
                'url': reverse('survey:responden_survey_detail', args=[record.id]),
                'title': 'Lihat Detail Responden',
                'a_class': 'text-blue-600 hover:text-blue-800',
                'icon_class': 'fas fa-eye',
            }
            if can_view
            else None
        )
        edit_link = (
            {
                'url': reverse('survey:responden_survey_edit', args=[record.id]),
                'title': 'Edit Responden Survey',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )
        delete_link = (
            {
                'url': reverse('survey:responden_survey_delete', args=[record.id]),
                'title': 'Delete Responden Survey',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            }
            if can_delete
            else None
        )
        return dt_render_actions(
            *(link for link in [view_link, edit_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )


class JawabanSurveyTable(tables.Table):
    """Table untuk Jawaban Survey"""
    
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )
    
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )
    
    responden_penilai = tables.Column(
        empty_values=(),
        verbose_name='Penilai',
        accessor='responden__nip_pegawaiPenilai',
        attrs=dt_col_attrs(width='12%', td_weight='medium', td_color='gray-900'),
        orderable=False
    )
    
    responden_dinilai = tables.Column(
        empty_values=(),
        verbose_name='Dinilai',
        accessor='responden__nip_pegawaiDinilai',
        attrs=dt_col_attrs(width='12%', td_weight='medium', td_color='gray-900'),
        orderable=False
    )
    
    pertanyaan_kode = tables.Column(
        verbose_name='Kode Pertanyaan',
        accessor='pertanyaan__kode_pertanyaan',
        attrs=dt_col_attrs(width='12%', td_color='gray-700')
    )
    
    pertanyaan_text = tables.Column(
        verbose_name='Pertanyaan',
        accessor='pertanyaan__pertanyaan',
        attrs=dt_col_attrs(width='25%', td_color='gray-700')
    )
    
    nilai = tables.Column(
        verbose_name='Nilai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%')
    )
    
    nilai_terbobot = tables.Column(
        empty_values=(),
        verbose_name='Nilai Terbobot',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='10%'),
        orderable=False
    )
    
    created_at = tables.DateTimeColumn(
        format='d M Y H:i',
        verbose_name='Tanggal Jawab',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%')
    )
    
    actions = tables.Column(
        empty_values=(),
        verbose_name='Aksi',
        attrs=dt_actions_attrs(width='8%', th_align='center', td_align='center'),
        orderable=False,
    )
    
    class Meta:
        model = JawabanSurvey
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'responden_penilai', 'responden_dinilai', 'pertanyaan_kode', 'pertanyaan_text', 'nilai', 'nilai_terbobot', 'created_at', 'actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'id': 'jawaban_survey_table',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10
    
    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)
    
    def render_pertanyaan_text(self, value):
        if len(value) > 60:
            return format_html(
                '<span title="{}">{}</span>',
                value,
                value[:60] + '...'
            )
        return value
    
    def render_nilai(self, value):
        nilai_map = {
            1: ('1', 'bg-red-100 text-red-800'),
            2: ('2', 'bg-orange-100 text-orange-800'),
            3: ('3', 'bg-yellow-100 text-yellow-800'),
            4: ('4', 'bg-blue-100 text-blue-800'),
            5: ('5', 'bg-green-100 text-green-800'),
        }
        label, css_class = nilai_map.get(value, (str(value), 'bg-gray-100 text-gray-800'))
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {}">{}</span>',
            css_class, label
        )
    
    def render_nilai_terbobot(self, record):
        nilai_terbobot = record.nilai_terbobot
        return format_html(
            '<span class="font-mono text-sm font-medium">{:.2f}</span>',
            nilai_terbobot
        )
    
    def render_actions(self, record, table):
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_edit = check_permission(user, 'survey', 'jawaban_survey', 'edit')
                can_delete = check_permission(user, 'survey', 'jawaban_survey', 'delete')
        except Exception:
            can_edit = False
            can_delete = False

        edit_link = (
            {
                'url': reverse('survey:jawaban_survey_edit', args=[record.id]),
                'title': 'Edit Jawaban Survey',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )
        delete_link = (
            {
                'url': reverse('survey:jawaban_survey_delete', args=[record.id]),
                'title': 'Delete Jawaban Survey',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            }
            if can_delete
            else None
        )
        return dt_render_actions(
            *(link for link in [edit_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )


class PeriodeSurveyTable(tables.Table):
    """Table untuk Periode Survey"""
    
    selection = tables.CheckBoxColumn(
        accessor='pk',
        attrs=dt_checkbox_attrs(th_width='3%'),
        orderable=False
    )
    
    row_number = tables.Column(
        empty_values=(),
        verbose_name='No',
        attrs=dt_row_number_attrs(width='4%'),
        orderable=False
    )
    
    jenis_survey = tables.Column(
        verbose_name='Jenis Survey',
        accessor='jenis_survey__nama',
        attrs=dt_col_attrs(width='20%', td_weight='medium', td_color='gray-900')
    )
    
    nama_periode = tables.Column(
        verbose_name='Nama Periode',
        attrs=dt_col_attrs(width='25%', td_weight='medium', td_color='gray-900')
    )
    
    tanggal_mulai = tables.DateTimeColumn(
        format='d M Y H:i',
        verbose_name='Mulai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%')
    )
    
    tanggal_selesai = tables.DateTimeColumn(
        format='d M Y H:i',
        verbose_name='Selesai',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%')
    )
    
    status = tables.Column(
        empty_values=(),
        verbose_name='Status',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='12%'),
        orderable=False,
    )
    
    is_active = tables.Column(
        verbose_name='Aktif',
        attrs=dt_col_attrs(th_align='center', td_align='center', width='8%'),
        orderable=True,
    )
    
    actions = tables.Column(
        empty_values=(),
        verbose_name='Aksi',
        attrs=dt_actions_attrs(width='10%', th_align='center', td_align='center'),
        orderable=False,
    )
    
    class Meta:
        model = PeriodeSurvey
        template_name = 'django_tables2/tailwind.html'
        fields = ('selection', 'row_number', 'jenis_survey', 'nama_periode', 'tanggal_mulai', 'tanggal_selesai', 'status', 'is_active', 'actions')
        attrs = {
            'class': 'w-full table-auto border-collapse border border-gray-300',
            'id': 'periode_survey_table',
            'thead': {'class': 'bg-gray-50'},
            'tbody': {'class': 'bg-white'},
        }
        per_page = 10
    
    def render_row_number(self, record, table):
        return dt_render_row_number(table, self)
    
    def render_status(self, record):
        status = record.status
        
        if status == 'nonaktif':
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">'
                '<i class="fas fa-pause-circle mr-1"></i> Nonaktif'
                '</span>'
            )
        elif status == 'belum_mulai':
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">'
                '<i class="fas fa-clock mr-1"></i> Belum Mulai'
                '</span>'
            )
        elif status == 'aktif':
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">'
                '<i class="fas fa-play-circle mr-1"></i> Aktif'
                '</span>'
            )
        elif status == 'selesai':
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">'
                '<i class="fas fa-stop-circle mr-1"></i> Selesai'
                '</span>'
            )
        else:
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">'
                '{}'
                '</span>',
                status
            )
    
    def render_is_active(self, value):
        if value:
            return format_html(
                '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">'
                '<i class="fas fa-check-circle mr-1"></i> Ya'
                '</span>'
            )
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">'
            '<i class="fas fa-times-circle mr-1"></i> Tidak'
            '</span>'
        )
    
    def render_actions(self, record, table):
        request = getattr(table, 'request', None)
        user = getattr(request, 'user', None)

        can_edit = False
        can_delete = False
        try:
            if user and getattr(user, 'is_authenticated', False):
                from apps.manajemen.helpers import check_permission
                can_edit = check_permission(user, 'survey', 'periode_survey', 'edit')
                can_delete = check_permission(user, 'survey', 'periode_survey', 'delete')
        except Exception:
            can_edit = False
            can_delete = False

        edit_link = (
            {
                'url': reverse('survey:periode_survey_edit', args=[record.id]),
                'title': 'Edit Periode Survey',
                'a_class': 'text-orange-600 hover:text-orange-800',
                'icon_class': 'fas fa-edit',
            }
            if can_edit
            else None
        )
        delete_link = (
            {
                'url': reverse('survey:periode_survey_delete', args=[record.id]),
                'title': 'Delete Periode Survey',
                'a_class': 'text-red-600 hover:text-red-800',
                'icon_class': 'fas fa-trash',
            }
            if can_delete
            else None
        )
        return dt_render_actions(
            *(link for link in [edit_link, delete_link] if link),
            container_class='flex gap-2 justify-center',
        )