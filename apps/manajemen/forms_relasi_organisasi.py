from django import forms
from django.forms.models import ModelChoiceField

from apps.master_data.models import MsUnitOrganisasi, MdJenisOrganisasi, MsJabatanStruktural, MdEselon, MsJabatanNonStruktural, MdJenisJabatan, MdKategoriJabatan
from apps.common.forms import select_search_attrs, date_ddmmyyyy_attrs
from apps.common.choices import STATUS_CHOICES_AKTIF_NONAKTIF


class _LabelRequiredMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            try:
                label = (f.label or '').strip()
                if not label:
                    continue
                f.error_messages = {**getattr(f, 'error_messages', {}), 'required': f'{label} harus diisi.'}
            except Exception:
                continue


class MsUnitOrganisasiSimpleForm(_LabelRequiredMixin, forms.ModelForm):
    """Form sederhana untuk menambah child/sub-unit dengan parent_id system"""
    STATUS_CHOICES = STATUS_CHOICES_AKTIF_NONAKTIF

    parent = ModelChoiceField(
        queryset=MsUnitOrganisasi.objects.filter(deleted_at__isnull=True).order_by('nm_opd'),
        required=True,
        label='Unit Induk (Parent)',
        widget=forms.Select(
            attrs={
                **select_search_attrs('Cari unit induk...'),
            }
        ),
    )

    nm_opd = forms.CharField(
        required=True,
        label='Nama Unit Organisasi',
        widget=forms.TextInput(
            attrs={
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan nama unit organisasi'
            }
        ),
    )

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=int,
        required=True,
        label='Status',
        widget=forms.Select(
            attrs={
                **select_search_attrs('Cari status...', base_class='w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'),
            }
        ),
    )

    keterangan = forms.CharField(
        required=False,
        label='Keterangan',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan keterangan (opsional)'
            }
        ),
    )

    class Meta:
        model = MsUnitOrganisasi
        fields = ['parent_id', 'nm_opd', 'status', 'keterangan']
        widgets = {
            'parent_id': forms.HiddenInput(),  # Hidden, use 'parent' field instead
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'parent' in self.data:
            try:
                parent_id = self.data['parent']
                self.fields['parent_id'].initial = parent_id
            except (ValueError, KeyError):
                pass
        elif self.instance and self.instance.parent_id:
            self.fields['parent'].initial = self.instance.parent_id

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set parent_id dari field 'parent'
        if 'parent' in self.cleaned_data:
            instance.parent_id = self.cleaned_data['parent']
        if commit:
            instance.save()
        return instance


class MsUnitOrganisasiChildModalForm(_LabelRequiredMixin, forms.ModelForm):
    """Form untuk modal Add Child, mengikuti kebutuhan penting Ms_unit_organisasi."""

    STATUS_CHOICES = STATUS_CHOICES_AKTIF_NONAKTIF

    parent = ModelChoiceField(
        queryset=MsUnitOrganisasi.objects.filter(deleted_at__isnull=True).order_by('nm_opd'),
        required=True,
        label='Unit Induk (Parent)',
        widget=forms.Select(
            attrs={
                **select_search_attrs('Cari unit induk...'),
            }
        ),
    )

    nm_opd = forms.CharField(
        required=True,
        label='Nama Unit Organisasi',
        widget=forms.TextInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan nama unit organisasi',
            }
        ),
    )

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=int,
        required=True,
        label='Status',
        widget=forms.Select(
            attrs={
                **select_search_attrs(
                    'Cari status...',
                    base_class='w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                ),
            }
        ),
    )

    id_unit = forms.ModelChoiceField(
        queryset=MdJenisOrganisasi.objects.filter(deleted_at__isnull=True, jo_03=1).order_by('jo_01'),
        required=False,
        label='Jenis Organisasi (id_unit)',
        widget=forms.Select(
            attrs={
                **select_search_attrs(
                    'Cari jenis organisasi...',
                    base_class='w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                    **{'data-dropdown-max-items': '5'},
                ),
            }
        ),
    )

    id_bkn = forms.CharField(
        required=True,
        label='ID BKN',
        widget=forms.TextInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan ID BKN (opsional)',
            }
        ),
    )

    no_urut = forms.IntegerField(
        required=False,
        label='No Urut',
        widget=forms.NumberInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan no urut (opsional)',
            }
        ),
    )

    npsn = forms.IntegerField(
        required=False,
        label='NPSN',
        widget=forms.NumberInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan NPSN (opsional)',
            }
        ),
    )

    rombel = forms.IntegerField(
        required=False,
        label='Rombel',
        widget=forms.NumberInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan rombel (opsional)',
            }
        ),
    )

    waktu_update_rombel = forms.DateTimeField(
        required=False,
        label='Waktu Update Rombel',
        input_formats=['%d-%m-%Y'],
        widget=forms.DateTimeInput(
            format='%d-%m-%Y',
            attrs={
                **date_ddmmyyyy_attrs('dd-mm-yyyy'),
            }
        ),
    )

    keterangan = forms.CharField(
        required=False,
        label='Keterangan',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'style': 'resize:none;',
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all resize-none',
                'placeholder': 'Masukkan keterangan (opsional)',
            }
        ),
    )

    class Meta:
        model = MsUnitOrganisasi
        fields = ['parent_id', 'nm_opd', 'status', 'id_unit', 'id_bkn', 'no_urut', 'npsn', 'rombel', 'waktu_update_rombel', 'keterangan']
        widgets = {
            'parent_id': forms.HiddenInput(),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.parent_id = self.cleaned_data.get('parent')
        if commit:
            instance.save()
        return instance


class MsJabatanNonStrukturalForm(_LabelRequiredMixin, forms.ModelForm):
    STATUS_CHOICES = STATUS_CHOICES_AKTIF_NONAKTIF

    id_jenis_jabatan = forms.ModelChoiceField(
        queryset=MdJenisJabatan.objects.filter(deleted_at__isnull=True, id__in=[2, 3]).order_by('id'),
        required=True,
        label='Jenis Jabatan',
        widget=forms.Select(
            attrs={
                **select_search_attrs(
                    'Cari jenis jabatan...',
                    base_class='w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                ),
            }
        ),
    )

    nama_jabatan = forms.CharField(
        required=True,
        label='Nama Jabatan',
        widget=forms.TextInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan nama jabatan',
            }
        ),
    )

    id_status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=int,
        required=True,
        label='Status',
        widget=forms.Select(
            attrs={
                **select_search_attrs(
                    'Cari status...',
                    base_class='w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                ),
            }
        ),
    )

    grade = forms.CharField(
        required=False,
        label='Grade',
        widget=forms.TextInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan grade (opsional)',
            }
        ),
    )

    id_bkn = forms.CharField(
        required=False,
        label='ID BKN',
        widget=forms.TextInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan ID BKN (opsional)',
            }
        ),
    )

    kategori_jabatan = forms.ModelChoiceField(
        queryset=MdKategoriJabatan.objects.filter(deleted_at__isnull=True).order_by('id'),
        required=True,
        label='Kategori Jabatan',
        widget=forms.Select(
            attrs={
                **select_search_attrs(
                    'Cari kategori jabatan...',
                    base_class='w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                ),
            }
        ),
    )

    bup_umur = forms.IntegerField(
        required=False,
        label='BUP Umur',
        widget=forms.NumberInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan BUP umur (opsional)',
            }
        ),
    )

    JF_01 = forms.CharField(
        required=False,
        label='Instansi Teknis',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'style': 'resize:none;',
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all resize-none',
                'placeholder': 'Masukkan instansi teknis (opsional)',
            }
        ),
    )

    JF_02 = forms.CharField(
        required=False,
        label='Kualifikasi Pendidikan Minimal',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'style': 'resize:none;',
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all resize-none',
                'placeholder': 'Masukkan kualifikasi pendidikan minimal (opsional)',
            }
        ),
    )

    JF_03 = forms.CharField(
        required=False,
        label='Kualifikasi Pendidikan Minimal (detail program studi)',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'style': 'resize:none;',
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all resize-none',
                'placeholder': 'Masukkan detail program studi (opsional)',
            }
        ),
    )

    JF_04 = forms.CharField(
        required=False,
        label='Syarat Jabatan ( Sertifikat Keahlian )',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'style': 'resize:none;',
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all resize-none',
                'placeholder': 'Masukkan syarat jabatan sertifikat keahlian (opsional)',
            }
        ),
    )

    JF_05 = forms.CharField(
        required=False,
        label='Syarat Jabatan ( Sertifikat Keterampiran  )',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'style': 'resize:none;',
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all resize-none',
                'placeholder': 'Masukkan syarat jabatan sertifikat keterampilan (opsional)',
            }
        ),
    )

    JF_06 = forms.CharField(
        required=False,
        label='Tugas Jabatan',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'style': 'resize:none;',
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all resize-none',
                'placeholder': 'Masukkan tugas jabatan (opsional)',
            }
        ),
    )

    JF_07 = forms.CharField(
        required=False,
        label='Keterangan',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'style': 'resize:none;',
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all resize-none',
                'placeholder': 'Masukkan keterangan (opsional)',
            }
        ),
    )

    class Meta:
        model = MsJabatanNonStruktural
        fields = [
            'id_jenis_jabatan',
            'nama_jabatan',
            'id_status',
            'grade',
            'id_bkn',
            'kategori_jabatan',
            'bup_umur',
            'JF_01',
            'JF_02',
            'JF_03',
            'JF_04',
            'JF_05',
            'JF_06',
            'JF_07',
        ]


class MsUnitOrganisasiEditModalForm(_LabelRequiredMixin, forms.ModelForm):
    STATUS_CHOICES = STATUS_CHOICES_AKTIF_NONAKTIF

    nm_opd = forms.CharField(
        required=True,
        label='Nama Unit Organisasi',
        widget=forms.TextInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan nama unit organisasi',
            }
        ),
    )

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=int,
        required=True,
        label='Status',
        widget=forms.Select(
            attrs={
                **select_search_attrs(
                    'Cari status...',
                    base_class='w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                ),
            }
        ),
    )

    id_unit = forms.ModelChoiceField(
        queryset=MdJenisOrganisasi.objects.filter(deleted_at__isnull=True, jo_03=1).order_by('jo_01'),
        required=False,
        label='Jenis Organisasi (id_unit)',
        widget=forms.Select(
            attrs={
                **select_search_attrs(
                    'Cari jenis organisasi...',
                    base_class='w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                    **{'data-dropdown-max-items': '5'},
                ),
            }
        ),
    )

    id_bkn = forms.CharField(
        required=False,
        label='ID BKN',
        widget=forms.TextInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan ID BKN (opsional)',
            }
        ),
    )

    no_urut = forms.IntegerField(
        required=False,
        label='No Urut',
        widget=forms.NumberInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan no urut (opsional)',
            }
        ),
    )

    npsn = forms.IntegerField(
        required=False,
        label='NPSN',
        widget=forms.NumberInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan NPSN (opsional)',
            }
        ),
    )

    rombel = forms.IntegerField(
        required=False,
        label='Rombel',
        widget=forms.NumberInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan rombel (opsional)',
            }
        ),
    )

    waktu_update_rombel = forms.DateTimeField(
        required=False,
        label='Waktu Update Rombel',
        input_formats=['%d-%m-%Y'],
        widget=forms.DateTimeInput(
            format='%d-%m-%Y',
            attrs={
                **date_ddmmyyyy_attrs('dd-mm-yyyy'),
            }
        ),
    )

    keterangan = forms.CharField(
        required=False,
        label='Keterangan',
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'style': 'resize:none;',
                'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all resize-none',
                'placeholder': 'Masukkan keterangan (opsional)',
            }
        ),
    )

    class Meta:
        model = MsUnitOrganisasi
        fields = ['nm_opd', 'status', 'id_unit', 'id_bkn', 'no_urut', 'npsn', 'rombel', 'waktu_update_rombel', 'keterangan']


class MsJabatanStrukturalModalForm(_LabelRequiredMixin, forms.ModelForm):
    STATUS_CHOICES = STATUS_CHOICES_AKTIF_NONAKTIF

    nm_jabatan = forms.CharField(
        required=True,
        label='Nama Jabatan',
        widget=forms.TextInput(
            attrs={
                'class': 'w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                'placeholder': 'Masukkan nama jabatan',
            }
        ),
    )

    id_eselon = forms.ModelChoiceField(
        queryset=MdEselon.objects.filter(deleted_at__isnull=True).order_by('urutan'),
        required=False,
        label='Eselon',
        widget=forms.Select(
            attrs={
                **select_search_attrs('Cari eselon...', base_class='w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'),
            }
        ),
    )

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=int,
        required=True,
        label='Status',
        widget=forms.Select(
            attrs={
                **select_search_attrs(
                    'Cari status...',
                    base_class='w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                ),
            }
        ),
    )

    class Meta:
        model = MsJabatanStruktural
        fields = ['id_opd', 'id_sub_opd', 'id_opd_lama', 'id_eselon', 'nm_jabatan', 'status']
        widgets = {
            'id_opd': forms.HiddenInput(),
            'id_sub_opd': forms.HiddenInput(),
            'id_opd_lama': forms.HiddenInput(),
        }


class MsUnitOrganisasiMoveParentForm(_LabelRequiredMixin, forms.Form):
    parent = ModelChoiceField(
        queryset=MsUnitOrganisasi.objects.filter(deleted_at__isnull=True).order_by('nm_opd'),
        required=True,
        label='Unit Induk (Parent Baru)',
        widget=forms.Select(
            attrs={
                **select_search_attrs(
                    'Cari unit induk...',
                    base_class='w-full h-12 px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                ),
            }
        ),
    )

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        if not instance:
            return

        try:
            nodes = MsUnitOrganisasi.objects.filter(deleted_at__isnull=True).values('pk', 'parent_id_id')
            children_map = {}
            for n in nodes:
                pid = n.get('parent_id_id')
                if not pid:
                    continue
                children_map.setdefault(pid, []).append(n.get('pk'))

            descendants = set()
            queue = [instance.pk]
            while queue:
                current = queue.pop(0)
                for cid in children_map.get(current, []) or []:
                    if cid in descendants:
                        continue
                    descendants.add(cid)
                    queue.append(cid)

            blocked_ids = descendants | {instance.pk}
            self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(pk__in=blocked_ids)
        except Exception:
            self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(pk=instance.pk)


class MsUnitOrganisasiForm(_LabelRequiredMixin, forms.ModelForm):
    STATUS_CHOICES = STATUS_CHOICES_AKTIF_NONAKTIF

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=int,
        required=False,
        widget=forms.Select(
            attrs={
                **select_search_attrs('Cari status...'),
            }
        ),
    )

    waktu_update_rombel = forms.DateTimeField(
        required=False,
        label='Waktu Update Rombel',
        input_formats=['%d-%m-%Y'],
        widget=forms.TextInput(
            attrs={
                **date_ddmmyyyy_attrs('dd-mm-yyyy'),
            }
        ),
    )

    class Meta:
        model = MsUnitOrganisasi
        fields = [
            'instansi_id',
            'tahun_sotk',
            'nama_opd_ii',
            'nama_bidang_iii',
            'nama_sub_bidang_iv',
            'nama_kategori_upt',
            'nama_upt',
            'parent_id',
            'nm_opd',
            'id_unit',
            'type_opd',
            'no_urut',
            'npsn',
            'rombel',
            'waktu_update_rombel',
            'keterangan',
            'status',
            'id_bkn',
            'id_bkn_x',
        ]
        labels = {
            'instansi_id': 'Instansi',
            'tahun_sotk': 'Tahun SOTK',
            'nama_opd_ii': 'Nama OPD (II)',
            'nama_bidang_iii': 'Nama Bidang (III)',
            'nama_sub_bidang_iv': 'Nama Sub Bidang (IV)',
            'nama_kategori_upt': 'Nama Kategori UPT',
            'nama_upt': 'Nama UPT',
            'parent_id': 'Parent ID',
            'nm_opd': 'Nama Unit Organisasi',
            'id_unit': 'ID Unit',
            'type_opd': 'Tipe OPD',
            'no_urut': 'No Urut',
            'npsn': 'NPSN',
            'rombel': 'Rombel',
            'waktu_update_rombel': 'Waktu Update Rombel',
            'keterangan': 'Keterangan',
            'status': 'Status',
            'id_bkn': 'ID BKN',
            'id_bkn_x': 'ID BKN X',
        }
        widgets = {
            'instansi_id': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'tahun_sotk': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'nama_opd_ii': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'nama_bidang_iii': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'nama_sub_bidang_iv': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'nama_kategori_upt': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'nama_upt': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'parent_id': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'nm_opd': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'id_unit': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'type_opd': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'no_urut': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'npsn': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'rombel': forms.NumberInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'waktu_update_rombel': forms.TextInput(
                attrs={
                    **date_ddmmyyyy_attrs('dd-mm-yyyy', base_class='w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'),
                }
            ),
            'keterangan': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'id_bkn': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
            'id_bkn_x': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all',
                }
            ),
        }
