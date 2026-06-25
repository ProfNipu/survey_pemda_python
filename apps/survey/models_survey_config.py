from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class SurveyConfiguration(models.Model):
    """
    Model untuk konfigurasi survey yang bisa diatur oleh Super Admin
    """
    nama_survey = models.CharField(max_length=200, verbose_name='Nama Survey')
    deskripsi = models.TextField(blank=True, verbose_name='Deskripsi')
    tahun = models.IntegerField(verbose_name='Tahun Survey')
    periode_mulai = models.DateField(verbose_name='Periode Mulai')
    periode_selesai = models.DateField(verbose_name='Periode Selesai')
    is_active = models.BooleanField(default=True, verbose_name='Status Aktif')
    
    # Konfigurasi tampilan
    show_pegawai_penilai = models.BooleanField(default=False, verbose_name='Tampilkan Data Penilai')
    show_foto_pegawai = models.BooleanField(default=True, verbose_name='Tampilkan Foto Pegawai')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='survey_configs_created'
    )

    class Meta:
        db_table = 'survey_configuration'
        verbose_name = 'Konfigurasi Survey'
        verbose_name_plural = 'Konfigurasi Survey'
        ordering = ['-tahun', '-created_at']

    def __str__(self):
        return f"{self.nama_survey} - {self.tahun}"


class SurveyAspek(models.Model):
    """
    Model untuk aspek penilaian yang bisa dikonfigurasi
    """
    survey_config = models.ForeignKey(
        SurveyConfiguration, 
        on_delete=models.CASCADE, 
        related_name='aspek_penilaian'
    )
    nama_aspek = models.CharField(max_length=200, verbose_name='Nama Aspek')
    deskripsi = models.TextField(verbose_name='Deskripsi/Pertanyaan')
    urutan = models.PositiveIntegerField(verbose_name='Urutan')
    
    # Konfigurasi skala
    skala_min = models.IntegerField(default=1, verbose_name='Skala Minimum')
    skala_max = models.IntegerField(default=5, verbose_name='Skala Maximum')
    
    # Label skala
    label_min = models.CharField(max_length=50, default='Sangat Kurang', verbose_name='Label Minimum')
    label_max = models.CharField(max_length=50, default='Sangat Baik', verbose_name='Label Maximum')
    
    is_required = models.BooleanField(default=True, verbose_name='Wajib Diisi')
    is_active = models.BooleanField(default=True, verbose_name='Status Aktif')

    class Meta:
        db_table = 'survey_aspek'
        verbose_name = 'Aspek Penilaian'
        verbose_name_plural = 'Aspek Penilaian'
        ordering = ['survey_config', 'urutan']
        unique_together = ['survey_config', 'urutan']

    def __str__(self):
        return f"{self.nama_aspek} ({self.survey_config.nama_survey})"


class SurveyResponse(models.Model):
    """
    Model untuk menyimpan response survey
    """
    survey_config = models.ForeignKey(
        SurveyConfiguration, 
        on_delete=models.CASCADE, 
        related_name='responses'
    )
    
    # Data Penilai
    nip_penilai = models.CharField(max_length=20, verbose_name='NIP Penilai')
    nama_penilai = models.CharField(max_length=200, verbose_name='Nama Penilai')
    jabatan_penilai = models.CharField(max_length=200, verbose_name='Jabatan Penilai')
    unit_kerja_penilai = models.CharField(max_length=200, verbose_name='Unit Kerja Penilai')
    
    # Data yang Dinilai
    nip_dinilai = models.CharField(max_length=20, verbose_name='NIP yang Dinilai')
    nama_dinilai = models.CharField(max_length=200, verbose_name='Nama yang Dinilai')
    jabatan_dinilai = models.CharField(max_length=200, verbose_name='Jabatan yang Dinilai')
    unit_kerja_dinilai = models.CharField(max_length=200, verbose_name='Unit Kerja yang Dinilai')
    
    # Komentar dan Saran
    komentar = models.TextField(blank=True, verbose_name='Komentar')
    saran = models.TextField(blank=True, verbose_name='Saran')
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('reviewed', 'Reviewed'),
        ],
        default='draft',
        verbose_name='Status'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'survey_response'
        verbose_name = 'Response Survey'
        verbose_name_plural = 'Response Survey'
        ordering = ['-created_at']
        unique_together = ['survey_config', 'nip_penilai', 'nip_dinilai']

    def __str__(self):
        return f"{self.nama_penilai} → {self.nama_dinilai} ({self.survey_config.nama_survey})"


class SurveyResponseDetail(models.Model):
    """
    Model untuk detail jawaban per aspek
    """
    response = models.ForeignKey(
        SurveyResponse, 
        on_delete=models.CASCADE, 
        related_name='detail_jawaban'
    )
    aspek = models.ForeignKey(
        SurveyAspek, 
        on_delete=models.CASCADE, 
        related_name='jawaban'
    )
    nilai = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Nilai'
    )

    class Meta:
        db_table = 'survey_response_detail'
        verbose_name = 'Detail Response Survey'
        verbose_name_plural = 'Detail Response Survey'
        unique_together = ['response', 'aspek']

    def __str__(self):
        return f"{self.aspek.nama_aspek}: {self.nilai}"