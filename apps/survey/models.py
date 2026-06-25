from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class PenilaianJPT(models.Model):
    """
    Form Penilaian JPT - Survey khusus untuk penilaian JPT
    """
    # Data Pegawai yang Dinilai
    nip_dinilai = models.CharField(max_length=255, verbose_name='NIP yang Dinilai')
    nama_dinilai = models.CharField(max_length=255, verbose_name='Nama yang Dinilai')
    jabatan_dinilai = models.CharField(max_length=255, verbose_name='Jabatan yang Dinilai')
    unit_kerja_dinilai = models.CharField(max_length=255, verbose_name='Unit Kerja yang Dinilai')
    
    # Data Penilai
    nip_penilai = models.CharField(max_length=255, verbose_name='NIP Penilai')
    nama_penilai = models.CharField(max_length=255, verbose_name='Nama Penilai')
    jabatan_penilai = models.CharField(max_length=255, verbose_name='Jabatan Penilai')
    unit_kerja_penilai = models.CharField(max_length=255, verbose_name='Unit Kerja Penilai')
    
    # Periode Penilaian
    periode_mulai = models.DateField(verbose_name='Periode Mulai')
    periode_selesai = models.DateField(verbose_name='Periode Selesai')
    
    # Aspek Penilaian (1-5)
    kepemimpinan = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Kepemimpinan',
        help_text='Kemampuan memimpin dan mengarahkan tim'
    )
    kerjasama = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Kerjasama',
        help_text='Kemampuan bekerja sama dengan tim'
    )
    komunikasi = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Komunikasi',
        help_text='Kemampuan berkomunikasi efektif'
    )
    inovasi = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Inovasi',
        help_text='Kemampuan berinovasi dan berkreasi'
    )
    integritas = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Integritas',
        help_text='Kejujuran dan konsistensi dalam bertindak'
    )
    orientasi_hasil = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Orientasi Hasil',
        help_text='Fokus pada pencapaian hasil yang berkualitas'
    )
    
    # Komentar dan Saran
    komentar = models.TextField(blank=True, null=True, verbose_name='Komentar')
    saran = models.TextField(blank=True, null=True, verbose_name='Saran Perbaikan')
    
    # Status dan Metadata
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('reviewed', 'Reviewed'),
            ('approved', 'Approved')
        ],
        default='draft',
        verbose_name='Status'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='Tanggal Submit')

    class Meta:
        db_table = 'penilaian_jpt'
        verbose_name = 'Penilaian JPT'
        verbose_name_plural = 'Penilaian JPT'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['nip_dinilai']),
            models.Index(fields=['nip_penilai']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Penilaian {self.nama_dinilai} oleh {self.nama_penilai}"

    @property
    def total_skor(self):
        """Hitung total skor penilaian"""
        return (
            self.kepemimpinan + self.kerjasama + self.komunikasi + 
            self.inovasi + self.integritas + self.orientasi_hasil
        )

    @property
    def rata_rata(self):
        """Hitung rata-rata skor"""
        return round(self.total_skor / 6, 2)

    @property
    def kategori_nilai(self):
        """Kategori berdasarkan rata-rata"""
        rata = self.rata_rata
        if rata >= 4.5:
            return 'Sangat Baik'
        elif rata >= 3.5:
            return 'Baik'
        elif rata >= 2.5:
            return 'Cukup'
        elif rata >= 1.5:
            return 'Kurang'
        else:
            return 'Sangat Kurang'

    def submit(self):
        """Submit penilaian"""
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()


class JenisSurvey(models.Model):
    """
    Master Jenis Survey - DINAMIS
    Bisa tambah jenis survey baru tanpa ubah kode
    """
    kode = models.CharField(max_length=50, unique=True, verbose_name='Kode Survey')
    nama = models.CharField(max_length=200, verbose_name='Nama Survey')
    deskripsi = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'survey_jenis'
        verbose_name = 'Jenis Survey'
        verbose_name_plural = 'Jenis Survey'
        ordering = ['kode']

    def __str__(self):
        return f"{self.kode} - {self.nama}"

    @property
    def periode_aktif(self):
        """Dapatkan periode yang sedang aktif untuk jenis survey ini"""
        return self.periode.filter(is_active=True).filter(
            tanggal_mulai__lte=timezone.now(),
            tanggal_selesai__gte=timezone.now()
        ).first()

    @property
    def can_access(self):
        """Apakah jenis survey ini bisa diakses saat ini"""
        periode = self.periode_aktif
        return periode is not None and periode.can_access

    def get_access_message(self):
        """Pesan akses untuk user"""
        if not self.is_active:
            return f"Jenis survey '{self.nama}' sedang tidak aktif."
        
        periode = self.periode_aktif
        if periode:
            return periode.get_access_message()
        
        # Cek apakah ada periode yang akan datang
        periode_mendatang = self.periode.filter(
            is_active=True,
            tanggal_mulai__gt=timezone.now()
        ).order_by('tanggal_mulai').first()
        
        if periode_mendatang:
            return f"Survey '{self.nama}' akan dibuka pada {periode_mendatang.tanggal_mulai.strftime('%d %B %Y pukul %H:%M')}."
        
        return f"Survey '{self.nama}' belum memiliki periode yang aktif."


class PeriodeSurvey(models.Model):
    """
    Periode Survey - Mengatur waktu buka/tutup survey
    """
    jenis_survey = models.ForeignKey(JenisSurvey, on_delete=models.CASCADE, related_name='periode')
    nama_periode = models.CharField(max_length=200, verbose_name='Nama Periode')
    tanggal_mulai = models.DateTimeField(verbose_name='Tanggal & Jam Mulai')
    tanggal_selesai = models.DateTimeField(verbose_name='Tanggal & Jam Selesai')
    deskripsi = models.TextField(blank=True, null=True, verbose_name='Deskripsi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'survey_periode'
        verbose_name = 'Periode Survey'
        verbose_name_plural = 'Periode Survey'
        ordering = ['-tanggal_mulai']

    def __str__(self):
        return f"{self.jenis_survey.nama} - {self.nama_periode}"

    @property
    def is_open(self):
        """Cek apakah periode survey sedang terbuka"""
        now = timezone.now()
        return (
            self.is_active and 
            self.tanggal_mulai <= now <= self.tanggal_selesai
        )

    @property
    def status(self):
        """Status periode: belum_mulai, aktif, selesai, nonaktif"""
        if not self.is_active:
            return 'nonaktif'
        
        now = timezone.now()
        if now < self.tanggal_mulai:
            return 'belum_mulai'
        elif now > self.tanggal_selesai:
            return 'selesai'
        else:
            return 'aktif'

    @property
    def status_display(self):
        """Display status untuk template"""
        status_map = {
            'nonaktif': 'Nonaktif',
            'belum_mulai': 'Belum Mulai',
            'aktif': 'Sedang Berlangsung',
            'selesai': 'Selesai'
        }
        return status_map.get(self.status, 'Unknown')

    @property
    def can_access(self):
        """Apakah survey bisa diakses saat ini"""
        return self.is_open

    def get_access_message(self):
        """Pesan akses untuk user"""
        if not self.is_active:
            return f"Survey '{self.jenis_survey.nama}' sedang tidak aktif."
        
        now = timezone.now()
        if now < self.tanggal_mulai:
            return f"Survey '{self.jenis_survey.nama}' akan dibuka pada {self.tanggal_mulai.strftime('%d %B %Y pukul %H:%M')}."
        elif now > self.tanggal_selesai:
            return f"Survey '{self.jenis_survey.nama}' telah ditutup pada {self.tanggal_selesai.strftime('%d %B %Y pukul %H:%M')}."
        else:
            return f"Survey '{self.jenis_survey.nama}' sedang terbuka hingga {self.tanggal_selesai.strftime('%d %B %Y pukul %H:%M')}."


class PertanyaanSurvey(models.Model):
    """
    Pertanyaan Survey - DINAMIS
    Setiap jenis survey punya pertanyaan sendiri
    """
    jenis_survey = models.ForeignKey(JenisSurvey, on_delete=models.CASCADE, related_name='pertanyaan')
    kode_pertanyaan = models.CharField(max_length=50, verbose_name='Kode Pertanyaan')
    judul = models.CharField(max_length=200, verbose_name='Judul Aspek', help_text='Judul singkat aspek penilaian (contoh: Berorientasi Pelayanan)')
    pertanyaan = models.TextField(null=True, blank=True, verbose_name='Pertanyaan Lengkap', help_text='Kalimat pertanyaan lengkap (contoh: Sejauh mana pegawai mampu memberikan pelayanan yang baik?)')
    urutan = models.IntegerField(default=0, verbose_name='Urutan')
    bobot = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name='Bobot')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'survey_pertanyaan'
        verbose_name = 'Pertanyaan Survey'
        verbose_name_plural = 'Pertanyaan Survey'
        ordering = ['jenis_survey', 'urutan']
        unique_together = ['jenis_survey', 'kode_pertanyaan']

    def __str__(self):
        return f"{self.jenis_survey.kode} - {self.judul}"


class RespondenSurvey(models.Model):
    """
    Data Responden yang dinilai
    """
    jenis_survey = models.ForeignKey(JenisSurvey, on_delete=models.SET_NULL, null=True, blank=True, related_name='responden', verbose_name='Jenis Survey')
    periode = models.ForeignKey(PeriodeSurvey, on_delete=models.SET_NULL, null=True, blank=True, related_name='responden', verbose_name='Periode Survey')
    id_pegawaiPenilai = models.BigIntegerField(verbose_name='ID Pegawai Penilai')
    nip_pegawaiPenilai = models.CharField(max_length=255, verbose_name='NIP Penilai')
    id_pegawaiDinilai = models.BigIntegerField(verbose_name='ID Pegawai Dinilai')
    nip_pegawaiDinilai = models.CharField(max_length=255, verbose_name='NIP Dinilai')
    peranPenilai = models.CharField(max_length=100, verbose_name='Peran Penilai')
    statusData = models.CharField(max_length=50, default='draft', verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'survey_responden'
        verbose_name = 'Responden Survey'
        verbose_name_plural = 'Responden Survey'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['nip_pegawaiPenilai']),
            models.Index(fields=['nip_pegawaiDinilai']),
        ]

    def __str__(self):
        return f"{self.nip_pegawaiPenilai} menilai {self.nip_pegawaiDinilai}"


class JawabanSurvey(models.Model):
    """
    Jawaban Survey - DINAMIS
    Menyimpan nilai untuk setiap pertanyaan
    """
    responden = models.ForeignKey(RespondenSurvey, on_delete=models.CASCADE, related_name='jawaban')
    pertanyaan = models.ForeignKey(PertanyaanSurvey, on_delete=models.CASCADE)
    nilai = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Nilai (1-5)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'survey_jawaban'
        verbose_name = 'Jawaban Survey'
        verbose_name_plural = 'Jawaban Survey'
        unique_together = ['responden', 'pertanyaan']

    def __str__(self):
        return f"{self.responden} - {self.pertanyaan.kode_pertanyaan}: {self.nilai}"

    @property
    def nilai_terbobot(self):
        """Hitung nilai dengan bobot"""
        return float(self.nilai) * float(self.pertanyaan.bobot)

# Import Survey Configuration Models
from .models_survey_config import (
    SurveyConfiguration,
    SurveyAspek,
    SurveyResponse,
    SurveyResponseDetail
)

# Import Pegawai Riwayat Data Model
from .models_pegawai_riwayat import PegawaiRiwayatData