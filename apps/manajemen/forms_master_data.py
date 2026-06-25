from django import forms

from apps.master_data.models import (
    MdKategoriPegawai,
    MdAgama,
    MdStatusPerkawinan,
    MdJenjangPendidikan,
    MsDaftarPendidikan,
    MdKedudukanPegawai,
    MdJenisJabatan,
    MdKategoriJabatan,
    MdEselon,
    MdPangkat,
    MdJenjangJabatan,
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

from apps.common.forms import select_search_attrs
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


class MdKategoriPegawaiForm(_LabelRequiredMixin, forms.ModelForm):
    STATUS_CHOICES = STATUS_CHOICES_AKTIF_NONAKTIF

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=int,
        required=True,
        widget=forms.Select(
            attrs={
                **select_search_attrs('Cari status...'),
            }
        ),
    )

    class Meta:
        model = MdKategoriPegawai
        fields = ['nama_kategori_pegawai', 'keterangan_kategori_pegawai', 'status']
        labels = {
            'nama_kategori_pegawai': 'Nama',
            'keterangan_kategori_pegawai': 'Keterangan',
            'status': 'Status',
        }
        widgets = {
            'nama_kategori_pegawai': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'keterangan_kategori_pegawai': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdAgamaForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdAgama
        fields = ['nama_agama', 'id_bkn']
        labels = {
            'nama_agama': 'Nama',
            'id_bkn': 'ID BKN',
        }
        widgets = {
            'nama_agama': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'id_bkn': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdStatusPerkawinanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdStatusPerkawinan
        fields = ['status_perkawinan', 'id_bkn']
        labels = {
            'status_perkawinan': 'Status Perkawinan',
            'id_bkn': 'ID BKN',
        }
        widgets = {
            'status_perkawinan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'id_bkn': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdJenjangPendidikanForm(_LabelRequiredMixin, forms.ModelForm):
    STATUS_CHOICES = STATUS_CHOICES_AKTIF_NONAKTIF

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=int,
        widget=forms.Select(
            attrs={
                **select_search_attrs('Cari status...'),
            }
        ),
    )

    class Meta:
        model = MdJenjangPendidikan
        fields = ['kode_tingkat', 'tingkat_pendidikan', 'keterangan', 'status', 'id_bkn', 'group_tk_pend_nm']
        labels = {
            'kode_tingkat': 'Kode Tingkat',
            'tingkat_pendidikan': 'Tingkat Pendidikan',
            'keterangan': 'Keterangan',
            'status': 'Status',
            'id_bkn': 'ID BKN',
            'group_tk_pend_nm': 'Group TK Pend NM',
        }
        widgets = {
            'kode_tingkat': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'tingkat_pendidikan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'keterangan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'group_tk_pend_nm': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdKedudukanPegawaiForm(_LabelRequiredMixin, forms.ModelForm):
    STATUS_HITUNG_CHOICES = (
        (1, 'Hitung'),
        (2, 'Tidak Dihitung'),
    )

    status_hitung = forms.TypedChoiceField(
        choices=STATUS_HITUNG_CHOICES,
        coerce=int,
        widget=forms.Select(
            attrs={
                **select_search_attrs('Cari status...'),
            }
        ),
    )

    class Meta:
        model = MdKedudukanPegawai
        fields = ['nama_kedudukan_pegawai', 'status_hitung', 'nomor_urut']
        labels = {
            'nama_kedudukan_pegawai': 'Kedudukan Pegawai',
            'status_hitung': 'Status Hitung',
            'nomor_urut': 'Nomor Urut',
        }
        widgets = {
            'nama_kedudukan_pegawai': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nomor_urut': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MsDaftarPendidikanForm(_LabelRequiredMixin, forms.ModelForm):
    STATUS_CHOICES = STATUS_CHOICES_AKTIF_NONAKTIF

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=int,
        required=True,
        widget=forms.Select(
            attrs={
                **select_search_attrs('Cari status...'),
            }
        ),
    )

    class Meta:
        model = MsDaftarPendidikan
        fields = ['kode_pendidikan', 'kode_tingkat', 'nm_pendidikan', 'status']
        labels = {
            'kode_pendidikan': 'Kode Pendidikan',
            'kode_tingkat': 'Jenjang Pendidikan',
            'nm_pendidikan': 'Nama Pendidikan',
            'status': 'Status',
        }
        widgets = {
            'kode_pendidikan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'kode_tingkat': forms.Select(attrs={**select_search_attrs('Cari jenjang pendidikan...')}),
            'nm_pendidikan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdJenisJabatanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdJenisJabatan
        fields = ['jenis_jabatan', 'urutan', 'id_bkn']
        labels = {
            'jenis_jabatan': 'Jenis Jabatan',
            'urutan': 'Urutan',
            'id_bkn': 'ID BKN',
        }
        widgets = {
            'jenis_jabatan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'urutan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'id_bkn': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdKategoriJabatanForm(_LabelRequiredMixin, forms.ModelForm):
    STATUS_CHOICES = STATUS_CHOICES_AKTIF_NONAKTIF

    kj_02 = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=int,
        widget=forms.Select(
            attrs={
                **select_search_attrs('Cari status...'),
            }
        ),
    )

    class Meta:
        model = MdKategoriJabatan
        fields = ['kj_01', 'kj_02']
        labels = {
            'kj_01': 'Kategori Jabatan',
            'kj_02': 'Status',
        }
        widgets = {
            'kj_01': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdEselonForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdEselon
        fields = ['eselon', 'urutan']
        labels = {
            'eselon': 'Eselon',
            'urutan': 'Urutan',
        }
        widgets = {
            'eselon': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'urutan': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdPangkatForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdPangkat
        fields = ['nama_golongan', 'nama_pangkat']
        labels = {
            'nama_golongan': 'Golongan',
            'nama_pangkat': 'Pangkat',
        }
        widgets = {
            'nama_golongan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nama_pangkat': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdJenjangJabatanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdJenjangJabatan
        fields = ['id', 'jenis', 'nama_jenjang', 'kgol_a', 'kgol_b', 'id_bkn', 'status']
        labels = {
            'id': 'Kode',
            'jenis': 'Jenis',
            'nama_jenjang': 'Nama Jenjang',
            'kgol_a': 'KGOL A',
            'kgol_b': 'KGOL B',
            'id_bkn': 'ID BKN',
            'status': 'Status',
        }
        widgets = {
            'id': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all', 'maxlength': '3'}),
            'jenis': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nama_jenjang': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'kgol_a': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'kgol_b': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'status': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknJenisHukumanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknJenisHukuman
        fields = [
            'id_bkn',
            'nama',
            'jenis_tingkat_hukuman',
            'status',
        ]
        labels = {
            'id_bkn': 'ID BKN',
            'nama': 'Nama',
            'jenis_tingkat_hukuman': 'Jenis Tingkat Hukuman',
            'status': 'Status',
        }
        widgets = {
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nama': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'jenis_tingkat_hukuman': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'status': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknTingkatHukdisForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknTingkatHukdis
        fields = [
            'id_bkn',
            'nama',
        ]
        labels = {
            'id_bkn': 'ID BKN',
            'nama': 'Nama',
        }
        widgets = {
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nama': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknNomorppHukdisForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknNomorppHukdis
        fields = [
            'id_bkn',
            'nomor',
        ]
        labels = {
            'id_bkn': 'ID BKN',
            'nomor': 'Nomor',
        }
        widgets = {
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nomor': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknJabatanFungsionalForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknJabatanFungsional
        fields = [
            'id_bkn',
            'nama',
            'bup_usia',
            'kel_jabatan_id',
            'jenjang',
            'status',
            'cepat_kode',
        ]
        labels = {
            'id_bkn': 'ID BKN',
            'nama': 'Nama',
            'bup_usia': 'BUP Usia',
            'kel_jabatan_id': 'Kel Jabatan ID',
            'jenjang': 'Jenjang',
            'status': 'Status',
            'cepat_kode': 'Cepat Kode',
        }
        widgets = {
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nama': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'bup_usia': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'kel_jabatan_id': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'jenjang': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'status': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'cepat_kode': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknJenisKenaikanPangkatForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknJenisKenaikanPangkat
        fields = [
            'nama',
        ]
        labels = {
            'nama': 'Nama',
        }
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknJenisMutasiForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknJenisMutasi
        fields = [
            'id_bkn',
            'jm_01',
        ]
        labels = {
            'id_bkn': 'ID BKN',
            'jm_01': 'Nama Mutasi',
        }
        widgets = {
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'jm_01': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknJenisPenugasanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknJenisPenugasan
        fields = [
            'id_bkn',
            'jp_01',
        ]
        labels = {
            'id_bkn': 'ID BKN',
            'jp_01': 'Jenis Penugasan',
        }
        widgets = {
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'jp_01': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknSubJabatanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknSubJabatan
        fields = [
            'kel_jabatan_id',
            'nama',
        ]
        labels = {
            'kel_jabatan_id': 'Kelompok Jabatan ID',
            'nama': 'Sub Jabatan',
        }
        widgets = {
            'kel_jabatan_id': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nama': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknJenisDiklatForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknJenisDiklat
        fields = [
            'jenis_diklat',
            'jenis_kursus_sertipikat',
        ]
        labels = {
            'jenis_diklat': 'Jenis Diklat',
            'jenis_kursus_sertipikat': 'Jenis Kursus/Sertipikat',
        }
        widgets = {
            'jenis_diklat': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'jenis_kursus_sertipikat': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknDaftarKppnForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknDaftarKppn
        fields = [
            'id_bkn',
            'nama_kppn',
            'status_kppn',
        ]
        labels = {
            'id_bkn': 'ID BKN',
            'nama_kppn': 'Nama KPPN',
            'status_kppn': 'Status KPPN',
        }
        widgets = {
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nama_kppn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'status_kppn': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknJenisPenghargaanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknJenisPenghargaan
        fields = [
            'nama',
        ]
        labels = {
            'nama': 'Nama',
        }
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdDiklatStrukturalForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdDiklatStruktural
        fields = ['diklat_struktural', 'eselon_level']
        labels = {
            'diklat_struktural': 'Diklat Struktural',
            'eselon_level': 'Eselon Level',
        }
        widgets = {
            'diklat_struktural': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'eselon_level': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdJenisSuratForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdJenisSurat
        fields = ['js_01', 'js_02', 'js_03']
        labels = {
            'js_01': 'Jenis Surat',
            'js_02': 'Urutan',
            'js_03': 'Status',
        }
        widgets = {
            'js_01': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'js_02': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'js_03': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdPejabatMenetapkanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdPejabatMenetapkan
        fields = ['kode_pejabat_menetapkan', 'pm_01', 'pm_02', 'pm_03']
        labels = {
            'kode_pejabat_menetapkan': 'Kode Pejabat Menetapkan',
            'pm_01': 'Nama Pejabat Menetapkan',
            'pm_02': 'Status',
            'pm_03': 'Urutan',
        }
        widgets = {
            'kode_pejabat_menetapkan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'pm_01': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'pm_02': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'pm_03': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdJenisOrganisasiForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdJenisOrganisasi
        fields = ['jo_01', 'jo_02', 'jo_03', 'jo_04']
        labels = {
            'jo_01': 'Jenis Organisasi',
            'jo_02': 'Nomor Urut',
            'jo_03': 'Status',
            'jo_04': 'Status UPT',
        }
        widgets = {
            'jo_01': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'jo_02': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'jo_03': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'jo_04': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdKategoriPemberitahuanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdKategoriPemberitahuan
        fields = ['nama_kategori_pemberitahuan', 'status_kategori_pemberitahuan']
        labels = {
            'nama_kategori_pemberitahuan': 'Kategori Pemberitahuan',
            'status_kategori_pemberitahuan': 'Status',
        }
        widgets = {
            'nama_kategori_pemberitahuan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'status_kategori_pemberitahuan': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdKategoriPeraturanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdKategoriPeraturan
        fields = ['KPP_01', 'KPP_02']
        labels = {
            'KPP_01': 'Kategori Peraturan',
            'KPP_02': 'Urutan',
        }
        widgets = {
            'KPP_01': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'KPP_02': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdPeraturanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdPeraturan
        fields = ['id_kategori_peraturan', 'nomor_peraturan', 'judul_peraturan', 'tanggal_peraturan', 'file_peraturan']
        labels = {
            'id_kategori_peraturan': 'Kategori Peraturan',
            'nomor_peraturan': 'Nomor Peraturan',
            'judul_peraturan': 'Judul Peraturan',
            'tanggal_peraturan': 'Tanggal Peraturan',
            'file_peraturan': 'File Peraturan',
        }
        widgets = {
            'id_kategori_peraturan': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nomor_peraturan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'judul_peraturan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'tanggal_peraturan': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'file_peraturan': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class MdTentangForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = MdTentang
        fields = ['nama_aplikasi', 'versi', 'deskripsi', 'developer', 'tahun']
        labels = {
            'nama_aplikasi': 'Nama Aplikasi',
            'versi': 'Versi',
            'deskripsi': 'Deskripsi',
            'developer': 'Developer',
            'tahun': 'Tahun',
        }
        widgets = {
            'nama_aplikasi': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'versi': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'deskripsi': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'developer': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'tahun': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknLokasiKerjaForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknLokasiKerja
        fields = [
            'id_bkn',
            'kanreg_id',
            'id_lokasi',
            'nama_lokasi',
            'jenis_lokasi',
            'jenis_kabupaten',
            'cepat_kode',
            'urutan_lokasi',
            'status_lokasi',
            'kode_instansi',
        ]
        labels = {
            'id_bkn': 'ID BKN',
            'kanreg_id': 'Kanreg ID',
            'id_lokasi': 'ID Lokasi',
            'nama_lokasi': 'Nama Lokasi',
            'jenis_lokasi': 'Jenis Lokasi',
            'jenis_kabupaten': 'Jenis Kabupaten',
            'cepat_kode': 'Cepat Kode',
            'urutan_lokasi': 'Urutan Lokasi',
            'status_lokasi': 'Status Lokasi',
            'kode_instansi': 'Kode Instansi',
        }
        widgets = {
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'kanreg_id': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'id_lokasi': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nama_lokasi': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'jenis_lokasi': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'jenis_kabupaten': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'cepat_kode': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'urutan_lokasi': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'status_lokasi': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'kode_instansi': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }


class BknAlasanHukumanForm(_LabelRequiredMixin, forms.ModelForm):
    class Meta:
        model = BknAlasanHukuman
        fields = [
            'id_bkn',
            'nama',
            'keterangan',
            'status',
        ]
        labels = {
            'id_bkn': 'ID BKN',
            'nama': 'Nama',
            'keterangan': 'Keterangan',
            'status': 'Status',
        }
        widgets = {
            'id_bkn': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'nama': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'keterangan': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
            'status': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25 focus:outline-none transition-all'}),
        }
