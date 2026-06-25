from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PegawaiRiwayatData(models.Model):
    """
    Model untuk menyimpan snapshot data pegawai saat survey dibuka
    Data ini FROZEN - tidak berubah meskipun data pegawai di ESIMPEG berubah
    Digunakan untuk laporan survey agar konsisten dengan data saat survey dilakukan
    """
    # Relasi ke periode survey
    periode_survey = models.ForeignKey(
        'survey.PeriodeSurvey',
        on_delete=models.CASCADE,
        related_name='pegawai_snapshots',
        verbose_name='Periode Survey'
    )
    jenis_survey = models.ForeignKey(
        'survey.JenisSurvey',
        on_delete=models.CASCADE,
        related_name='pegawai_snapshots',
        verbose_name='Jenis Survey'
    )
    
    # Data Pegawai (Snapshot dari ESIMPEG API)
    id_pegawai = models.BigIntegerField(verbose_name='ID Pegawai', db_index=True)
    nip_baru = models.CharField(max_length=50, null=True, blank=True, verbose_name='NIP Baru', db_index=True)
    nip_lama = models.CharField(max_length=50, null=True, blank=True, verbose_name='NIP Lama')
    nama_pegawai = models.CharField(max_length=255, verbose_name='Nama Pegawai', db_index=True)
    
    # Data Personal
    tempat_lahir = models.CharField(max_length=100, null=True, blank=True, verbose_name='Tempat Lahir')
    tanggal_lahir = models.CharField(max_length=50, null=True, blank=True, verbose_name='Tanggal Lahir')
    jenis_kelamin = models.IntegerField(null=True, blank=True, verbose_name='Jenis Kelamin')  # 1=L, 2=P
    alamat_rumah = models.TextField(null=True, blank=True, verbose_name='Alamat')
    no_hp = models.CharField(max_length=50, null=True, blank=True, verbose_name='No HP')
    
    # Data Jabatan (saat snapshot diambil)
    id_jabatan = models.BigIntegerField(null=True, blank=True, verbose_name='ID Jabatan')
    nama_jabatan = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nama Jabatan')
    masa_kerja_jabatan = models.CharField(max_length=100, null=True, blank=True, verbose_name='Masa Kerja Jabatan')
    
    # Eselon (saat snapshot diambil)
    kode_eselon = models.BigIntegerField(null=True, blank=True, verbose_name='Kode Eselon', db_index=True)
    nama_eselon = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nama Eselon')
    
    # OPD (saat snapshot diambil)
    id_opd = models.BigIntegerField(null=True, blank=True, verbose_name='ID OPD', db_index=True)
    nm_opd = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nama OPD')
    id_opd_urut = models.IntegerField(null=True, blank=True, verbose_name='Urutan OPD (A_12)', db_index=True)
    is_opd_induk = models.BooleanField(default=False, verbose_name='Is OPD Induk', db_index=True)
    id_sub_opd = models.BigIntegerField(null=True, blank=True, verbose_name='ID Sub OPD')
    nm_sub_opd = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nama Sub OPD')
    
    # Golongan/Pangkat (saat snapshot diambil)
    id_golongan = models.BigIntegerField(null=True, blank=True, verbose_name='ID Golongan', db_index=True)
    nama_golongan = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nama Golongan')
    nama_pangkat = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nama Pangkat')
    
    # Status Pegawai (saat snapshot diambil)
    kategori_pegawai = models.IntegerField(null=True, blank=True, verbose_name='Kategori Pegawai (1=CPNS, 2=PNS, 3=P3K)', db_index=True)
    nama_kategori_pegawai = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nama Kategori Pegawai')
    
    # Masa kerja (saat snapshot diambil)
    tmt_cpns = models.CharField(max_length=50, null=True, blank=True, verbose_name='TMT CPNS')
    masa_kerja_tahun = models.IntegerField(null=True, blank=True, verbose_name='Masa Kerja (Tahun)')
    masa_kerja_bulan = models.IntegerField(null=True, blank=True, verbose_name='Masa Kerja (Bulan)')
    akhir_kerja_p3k = models.CharField(max_length=50, null=True, blank=True, verbose_name='Akhir Kerja P3K')
    
    # Full JSON data from API (for reference)
    raw_data = models.JSONField(verbose_name='Raw Data dari API', help_text='Full JSON response dari ESIMPEG API')
    
    # Metadata
    snapshot_at = models.DateTimeField(auto_now_add=True, verbose_name='Waktu Snapshot Diambil', db_index=True)
    snapshot_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Snapshot Dibuat Oleh')
    
    class Meta:
        db_table = 'pegawai_riwayat_data'
        verbose_name = 'Riwayat Data Pegawai (Snapshot)'
        verbose_name_plural = 'Riwayat Data Pegawai (Snapshot)'
        ordering = ['-snapshot_at']
        indexes = [
            models.Index(fields=['periode_survey', 'nip_baru']),
            models.Index(fields=['jenis_survey', 'id_pegawai']),
            models.Index(fields=['periode_survey', 'id_opd']),
            models.Index(fields=['periode_survey', 'kode_eselon']),
            models.Index(fields=['snapshot_at']),
        ]
        # Unique constraint: satu pegawai hanya punya satu snapshot per periode
        unique_together = ['periode_survey', 'id_pegawai']

    def __str__(self):
        return f"{self.nip_baru or self.nip_lama} - {self.nama_pegawai} (Snapshot: {self.periode_survey.nama_periode})"
    
    @property
    def jenis_kelamin_display(self):
        """Return display text for jenis_kelamin"""
        if self.jenis_kelamin == 1:
            return 'Laki-laki'
        elif self.jenis_kelamin == 2:
            return 'Perempuan'
        return '-'
    
    @property
    def nip(self):
        """Return NIP (prioritas NIP baru)"""
        return self.nip_baru or self.nip_lama
