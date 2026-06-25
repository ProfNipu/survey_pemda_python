from django import forms
from .models import JenisSurvey, PertanyaanSurvey, RespondenSurvey, JawabanSurvey, PeriodeSurvey, PenilaianJPT


class PenilaianJPTForm(forms.ModelForm):
    """Form untuk Penilaian JPT"""
    
    class Meta:
        model = PenilaianJPT
        fields = [
            'nip_dinilai', 'nama_dinilai', 'jabatan_dinilai', 'unit_kerja_dinilai',
            'nip_penilai', 'nama_penilai', 'jabatan_penilai', 'unit_kerja_penilai',
            'periode_mulai', 'periode_selesai',
            'kepemimpinan', 'kerjasama', 'komunikasi', 'inovasi', 'integritas', 'orientasi_hasil',
            'komentar', 'saran'
        ]
        widgets = {
            'nip_dinilai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Masukkan NIP yang dinilai'
            }),
            'nama_dinilai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Nama lengkap yang dinilai'
            }),
            'jabatan_dinilai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Jabatan yang dinilai'
            }),
            'unit_kerja_dinilai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Unit kerja yang dinilai'
            }),
            'nip_penilai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Masukkan NIP penilai'
            }),
            'nama_penilai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Nama lengkap penilai'
            }),
            'jabatan_penilai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Jabatan penilai'
            }),
            'unit_kerja_penilai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Unit kerja penilai'
            }),
            'periode_mulai': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'type': 'date'
            }),
            'periode_selesai': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'type': 'date'
            }),
            'kepemimpinan': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent'
            }, choices=[(i, f'{i} - {"Sangat Kurang" if i==1 else "Kurang" if i==2 else "Cukup" if i==3 else "Baik" if i==4 else "Sangat Baik"}') for i in range(1, 6)]),
            'kerjasama': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent'
            }, choices=[(i, f'{i} - {"Sangat Kurang" if i==1 else "Kurang" if i==2 else "Cukup" if i==3 else "Baik" if i==4 else "Sangat Baik"}') for i in range(1, 6)]),
            'komunikasi': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent'
            }, choices=[(i, f'{i} - {"Sangat Kurang" if i==1 else "Kurang" if i==2 else "Cukup" if i==3 else "Baik" if i==4 else "Sangat Baik"}') for i in range(1, 6)]),
            'inovasi': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent'
            }, choices=[(i, f'{i} - {"Sangat Kurang" if i==1 else "Kurang" if i==2 else "Cukup" if i==3 else "Baik" if i==4 else "Sangat Baik"}') for i in range(1, 6)]),
            'integritas': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent'
            }, choices=[(i, f'{i} - {"Sangat Kurang" if i==1 else "Kurang" if i==2 else "Cukup" if i==3 else "Baik" if i==4 else "Sangat Baik"}') for i in range(1, 6)]),
            'orientasi_hasil': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent'
            }, choices=[(i, f'{i} - {"Sangat Kurang" if i==1 else "Kurang" if i==2 else "Cukup" if i==3 else "Baik" if i==4 else "Sangat Baik"}') for i in range(1, 6)]),
            'komentar': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Komentar umum tentang kinerja yang dinilai'
            }),
            'saran': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Saran untuk perbaikan dan pengembangan'
            }),
        }
        labels = {
            'nip_dinilai': 'NIP yang Dinilai',
            'nama_dinilai': 'Nama yang Dinilai',
            'jabatan_dinilai': 'Jabatan yang Dinilai',
            'unit_kerja_dinilai': 'Unit Kerja yang Dinilai',
            'nip_penilai': 'NIP Penilai',
            'nama_penilai': 'Nama Penilai',
            'jabatan_penilai': 'Jabatan Penilai',
            'unit_kerja_penilai': 'Unit Kerja Penilai',
            'periode_mulai': 'Periode Mulai',
            'periode_selesai': 'Periode Selesai',
            'kepemimpinan': 'Kepemimpinan',
            'kerjasama': 'Kerjasama',
            'komunikasi': 'Komunikasi',
            'inovasi': 'Inovasi',
            'integritas': 'Integritas',
            'orientasi_hasil': 'Orientasi Hasil',
            'komentar': 'Komentar',
            'saran': 'Saran Perbaikan',
        }
        help_texts = {
            'kepemimpinan': 'Kemampuan memimpin dan mengarahkan tim',
            'kerjasama': 'Kemampuan bekerja sama dengan tim',
            'komunikasi': 'Kemampuan berkomunikasi efektif',
            'inovasi': 'Kemampuan berinovasi dan berkreasi',
            'integritas': 'Kejujuran dan konsistensi dalam bertindak',
            'orientasi_hasil': 'Fokus pada pencapaian hasil yang berkualitas',
        }

    def clean(self):
        cleaned_data = super().clean()
        periode_mulai = cleaned_data.get('periode_mulai')
        periode_selesai = cleaned_data.get('periode_selesai')

        if periode_mulai and periode_selesai:
            if periode_mulai >= periode_selesai:
                raise forms.ValidationError('Periode mulai harus lebih awal dari periode selesai.')

        return cleaned_data


class JenisSurveyForm(forms.ModelForm):
    """Form untuk Jenis Survey"""
    
    class Meta:
        model = JenisSurvey
        fields = ['kode', 'nama', 'deskripsi', 'is_active']
        widgets = {
            'kode': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Contoh: JPT, SURVEY_360',
            }),
            'nama': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Contoh: Penilaian JPT',
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Deskripsi jenis survey (opsional)',
                'rows': 3,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500',
            }),
        }
        labels = {
            'kode': 'Kode Survey',
            'nama': 'Nama Survey',
            'deskripsi': 'Deskripsi',
            'is_active': 'Aktif',
        }
        help_texts = {
            'kode': 'Kode unik untuk jenis survey (huruf besar, underscore)',
            'nama': 'Nama lengkap jenis survey',
            'deskripsi': 'Penjelasan singkat tentang jenis survey ini',
            'is_active': 'Centang jika survey ini aktif dan bisa digunakan',
        }


class PertanyaanSurveyForm(forms.ModelForm):
    """Form untuk Pertanyaan Survey"""
    
    class Meta:
        model = PertanyaanSurvey
        fields = ['jenis_survey', 'kode_pertanyaan', 'judul', 'pertanyaan', 'urutan', 'bobot', 'is_active']
        widgets = {
            'jenis_survey': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
            }),
            'kode_pertanyaan': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Contoh: survey01, q01',
            }),
            'judul': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Contoh: Berorientasi Pelayanan, Akuntabel',
            }),
            'pertanyaan': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Tulis pertanyaan lengkap di sini (contoh: Sejauh mana pegawai mampu memberikan pelayanan yang baik kepada masyarakat?)',
                'rows': 3,
            }),
            'urutan': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': '1',
                'min': '1',
            }),
            'bobot': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': '1.0',
                'step': '0.1',
                'min': '0.1',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500',
            }),
        }
        labels = {
            'jenis_survey': 'Jenis Survey',
            'kode_pertanyaan': 'Kode Pertanyaan',
            'judul': 'Judul Aspek',
            'pertanyaan': 'Pertanyaan Lengkap',
            'urutan': 'Urutan',
            'bobot': 'Bobot',
            'is_active': 'Aktif',
        }
        help_texts = {
            'jenis_survey': 'Pilih jenis survey untuk pertanyaan ini',
            'kode_pertanyaan': 'Kode unik untuk pertanyaan (contoh: survey01)',
            'judul': 'Judul singkat aspek penilaian (contoh: Berorientasi Pelayanan)',
            'pertanyaan': 'Kalimat pertanyaan lengkap yang akan ditampilkan (opsional)',
            'urutan': 'Nomor urut pertanyaan (untuk sorting)',
            'bobot': 'Bobot pertanyaan untuk perhitungan nilai (default: 1.0)',
            'is_active': 'Centang jika pertanyaan ini aktif',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter hanya jenis survey yang aktif
        self.fields['jenis_survey'].queryset = JenisSurvey.objects.filter(is_active=True)


class RespondenSurveyForm(forms.ModelForm):
    """Form untuk Responden Survey"""
    
    class Meta:
        model = RespondenSurvey
        fields = ['id_pegawaiPenilai', 'nip_pegawaiPenilai', 'id_pegawaiDinilai', 'nip_pegawaiDinilai', 'peranPenilai', 'statusData']
        widgets = {
            'id_pegawaiPenilai': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'ID Pegawai Penilai',
            }),
            'nip_pegawaiPenilai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'NIP Pegawai Penilai',
            }),
            'id_pegawaiDinilai': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'ID Pegawai Dinilai',
            }),
            'nip_pegawaiDinilai': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'NIP Pegawai Dinilai',
            }),
            'peranPenilai': forms.Select(choices=[
                ('atasan', 'Atasan'),
                ('bawahan', 'Bawahan'),
                ('rekan', 'Rekan Kerja'),
                ('diri_sendiri', 'Diri Sendiri'),
            ], attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
            }),
            'statusData': forms.Select(choices=[
                ('draft', 'Draft'),
                ('submitted', 'Submitted'),
                ('completed', 'Completed'),
            ], attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
            }),
        }
        labels = {
            'id_pegawaiPenilai': 'ID Pegawai Penilai',
            'nip_pegawaiPenilai': 'NIP Pegawai Penilai',
            'id_pegawaiDinilai': 'ID Pegawai Dinilai',
            'nip_pegawaiDinilai': 'NIP Pegawai Dinilai',
            'peranPenilai': 'Peran Penilai',
            'statusData': 'Status Data',
        }
        help_texts = {
            'id_pegawaiPenilai': 'ID pegawai yang melakukan penilaian',
            'nip_pegawaiPenilai': 'NIP pegawai yang melakukan penilaian',
            'id_pegawaiDinilai': 'ID pegawai yang dinilai',
            'nip_pegawaiDinilai': 'NIP pegawai yang dinilai',
            'peranPenilai': 'Hubungan penilai dengan yang dinilai',
            'statusData': 'Status data responden',
        }


class JawabanSurveyForm(forms.ModelForm):
    """Form untuk Jawaban Survey"""
    
    class Meta:
        model = JawabanSurvey
        fields = ['responden', 'pertanyaan', 'nilai']
        widgets = {
            'responden': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
            }),
            'pertanyaan': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
            }),
            'nilai': forms.Select(choices=[
                (1, '1 - Sangat Kurang'),
                (2, '2 - Kurang'),
                (3, '3 - Cukup'),
                (4, '4 - Baik'),
                (5, '5 - Sangat Baik'),
            ], attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
            }),
        }
        labels = {
            'responden': 'Responden',
            'pertanyaan': 'Pertanyaan',
            'nilai': 'Nilai',
        }
        help_texts = {
            'responden': 'Pilih responden yang memberikan jawaban',
            'pertanyaan': 'Pilih pertanyaan yang dijawab',
            'nilai': 'Nilai jawaban (1-5)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter hanya pertanyaan yang aktif
        self.fields['pertanyaan'].queryset = PertanyaanSurvey.objects.filter(is_active=True)


class PeriodeSurveyForm(forms.ModelForm):
    """Form untuk Periode Survey"""
    
    class Meta:
        model = PeriodeSurvey
        fields = ['jenis_survey', 'nama_periode', 'tanggal_mulai', 'tanggal_selesai', 'deskripsi', 'is_active']
        widgets = {
            'jenis_survey': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
            }),
            'nama_periode': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Contoh: Periode Penilaian JPT 2024',
            }),
            'tanggal_mulai': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'type': 'datetime-local',
            }),
            'tanggal_selesai': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'type': 'datetime-local',
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Deskripsi periode survey (opsional)',
                'rows': 3,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500',
            }),
        }
        labels = {
            'jenis_survey': 'Jenis Survey',
            'nama_periode': 'Nama Periode',
            'tanggal_mulai': 'Tanggal & Jam Mulai',
            'tanggal_selesai': 'Tanggal & Jam Selesai',
            'deskripsi': 'Deskripsi',
            'is_active': 'Aktif',
        }
        help_texts = {
            'jenis_survey': 'Pilih jenis survey untuk periode ini',
            'nama_periode': 'Nama periode yang mudah diingat',
            'tanggal_mulai': 'Tanggal dan jam mulai survey dapat diakses',
            'tanggal_selesai': 'Tanggal dan jam survey ditutup',
            'deskripsi': 'Penjelasan tambahan tentang periode ini',
            'is_active': 'Centang jika periode ini aktif',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter hanya jenis survey yang aktif
        self.fields['jenis_survey'].queryset = JenisSurvey.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        tanggal_mulai = cleaned_data.get('tanggal_mulai')
        tanggal_selesai = cleaned_data.get('tanggal_selesai')
        
        if tanggal_mulai and tanggal_selesai:
            if tanggal_mulai >= tanggal_selesai:
                raise forms.ValidationError('Tanggal selesai harus lebih besar dari tanggal mulai.')
        
        return cleaned_data
