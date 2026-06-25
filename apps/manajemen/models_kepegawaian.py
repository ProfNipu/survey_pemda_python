from django.db import models
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _md_pangkat_order_index_map():
    from apps.master_data.models import MdPangkat

    ids = list(MdPangkat.objects.order_by('id').values_list('id', flat=True))
    return {pid: idx + 1 for idx, pid in enumerate(ids)}


class MsPegawai(models.Model):
    id_pegawai = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    id_opd = models.ForeignKey(
        'master_data.MsUnitOrganisasi',
        to_field='id_opd',
        on_delete=models.DO_NOTHING,
        db_column='id_opd',
        related_name='pegawai_id_opd_children',
        db_constraint=False,
        null=True,
        blank=True,
    )
    id_sub_opd = models.ForeignKey(
        'master_data.MsUnitOrganisasi',
        to_field='id_opd',
        on_delete=models.DO_NOTHING,
        db_column='id_sub_opd',
        related_name='pegawai_id_sub_opd_children',
        db_constraint=False,
        null=True,
        blank=True,
    )
    id_jenis_jabatan = models.ForeignKey(
        'master_data.MdJenisJabatan',
        on_delete=models.DO_NOTHING,
        db_column='id_jenis_jabatan',
        related_name='pegawai_jenis_jabatan_children',
        db_constraint=False,
        null=True,
        blank=True,
    )
    id_jabatan = models.ForeignKey(
        'master_data.MsJabatanStruktural',
        to_field='id_jabatan',
        on_delete=models.DO_NOTHING,
        db_column='id_jabatan',
        related_name='pegawai_jabatan_struktural_children',
        db_constraint=False,
        null=True,
        blank=True,
    )
    id_jfu_jft = models.ForeignKey(
        'master_data.MsJabatanNonStruktural',
        to_field='id_jabatan_fungsional',
        on_delete=models.DO_NOTHING,
        db_column='id_jfu_jft',
        related_name='pegawai_jabatan_non_struktural_children',
        db_constraint=False,
        null=True,
        blank=True,
    )
    id_sub_jabatan = models.ForeignKey(
        'master_data.BknSubJabatan',
        on_delete=models.DO_NOTHING,
        db_column='id_sub_jabatan',
        related_name='pegawai_bkn_jabatan_fungsional_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='Sub Jabatan',
        db_comment='Sub Jabatan',
    )
    tugas_tambahan = models.IntegerField(null=True, blank=True)
    id_lokasi = models.ForeignKey(
        'master_data.BknLokasiKerja',
        on_delete=models.DO_NOTHING,
        db_column='id_lokasi',
        related_name='pegawai_lokasi_kerja_children',
        db_constraint=False,
        null=True,
        blank=True,
    )

    A_01 = models.PositiveSmallIntegerField(null=True, blank=True, help_text='KODE SKPD', db_comment='KODE SKPD')
    B_02 = models.BigIntegerField(null=True, blank=True, help_text='NIP Lama', db_comment='NIP Lama')
    B_02B = models.CharField(max_length=18, null=True, blank=True, help_text='NIP baru', db_comment='NIP baru')
    B_03A = models.CharField(max_length=10, null=True, blank=True, help_text='Gelar Depan', db_comment='Gelar Depan')
    B_03 = models.CharField(max_length=35, null=True, blank=True, help_text='Nama Lengkap', db_comment='Nama Lengkap')
    B_03B = models.CharField(max_length=20, null=True, blank=True, help_text='Gelar Belakang', db_comment='Gelar Belakang')
    B_04 = models.CharField(max_length=30, null=True, blank=True, help_text='Tempat Lahir', db_comment='Tempat Lahir')
    B_05 = models.DateField(null=True, blank=True, help_text='Tanggal Lahir', db_comment='Tanggal Lahir')
    B_06 = models.SmallIntegerField(null=True, blank=True, help_text='Jenis Kelamin', db_comment='Jenis Kelamin')
    B_07 = models.ForeignKey(
        'master_data.MdAgama',
        on_delete=models.DO_NOTHING,
        db_column='B_07',
        related_name='pegawai_agama_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='Agama',
        db_comment='Agama',
    )
    B_08 = models.CharField(max_length=30, null=True, blank=True, help_text='No Karpeg', db_comment='No Karpeg')
    B_09 = models.ForeignKey(
        'master_data.MdKategoriPegawai',
        on_delete=models.DO_NOTHING,
        db_column='B_09',
        related_name='pegawai_kategori_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='Kategori Pegawai',
        db_comment='Kategori Pegawai',
    )
    B_10 = models.CharField(max_length=1, null=True, blank=True)
    B_11 = models.ForeignKey(
        'master_data.MdKedudukanPegawai',
        on_delete=models.DO_NOTHING,
        db_column='B_11',
        related_name='pegawai_kedudukan_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='Kedudukan Pegawai',
        db_comment='Kedudukan Pegawai',
    )
    B_12 = models.TextField(null=True, blank=True, help_text='Alamat', db_comment='Alamat')
    B_13 = models.IntegerField(null=True, blank=True, help_text='status_apel', db_comment='status_apel')

    C_01 = models.CharField(max_length=30, null=True, blank=True, help_text='No. Dokumen (NIK)', db_comment='No. Dokumen (NIK)')
    C_01A = models.CharField(max_length=3, null=True, blank=True, help_text='Status ETPP', db_comment='Status ETPP')
    C_02 = models.CharField(max_length=50, null=True, blank=True, help_text='Alamat Email', db_comment='Alamat Email')
    C_03 = models.CharField(max_length=50, null=True, blank=True, help_text='Alamat Email EGOV', db_comment='Alamat Email EGOV')
    C_04 = models.CharField(max_length=50, null=True, blank=True, help_text='NOMOR_HP', db_comment='NOMOR_HP')
    C_05 = models.CharField(max_length=40, null=True, blank=True, help_text='NOMOR_TELPON', db_comment='NOMOR_TELPON')

    D_01 = models.CharField(max_length=1, null=True, blank=True)
    D_02 = models.CharField(max_length=30, null=True, blank=True, help_text='Nomor SK CPNS', db_comment='Nomor SK CPNS')
    D_03 = models.DateField(null=True, blank=True, help_text='tgl sk cpns', db_comment='tgl sk cpns')
    D_04 = models.DateField(null=True, blank=True, help_text='TMT CPNS', db_comment='TMT CPNS')
    D_05 = models.ForeignKey(
        'master_data.MdPangkat',
        on_delete=models.DO_NOTHING,
        db_column='D_05',
        related_name='pegawai_pangkat_cpns_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='Golongan / Ruang cpns',
        db_comment='Golongan / Ruang cpns',
    )
    D_06 = models.CharField(max_length=4, null=True, blank=True)
    D_07 = models.DateField(null=True, blank=True)

    E_01 = models.CharField(max_length=1, null=True, blank=True)
    E_02 = models.CharField(max_length=30, null=True, blank=True, help_text='Nomor SK PNS', db_comment='Nomor SK PNS')
    E_03 = models.DateField(null=True, blank=True, help_text='Tanggal SK PNS', db_comment='Tanggal SK PNS')
    E_04 = models.DateField(null=True, blank=True, help_text='TMT PNS', db_comment='TMT PNS')
    E_05 = models.ForeignKey(
        'master_data.MdPangkat',
        on_delete=models.DO_NOTHING,
        db_column='E_05',
        related_name='pegawai_pangkat_pns_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='Golongan / Ruang pns',
        db_comment='Golongan / Ruang pns',
    )
    E_06 = models.CharField(max_length=1, null=True, blank=True, help_text='Sumpah / Janji', db_comment='Sumpah / Janji')
    E_07 = models.CharField(max_length=4, null=True, blank=True, help_text='Tahun Sumpah / Janji', db_comment='Tahun Sumpah / Janji')

    F_01 = models.CharField(max_length=1, null=True, blank=True, help_text='Ditetapkan oleh (gol.)', db_comment='Ditetapkan oleh (gol.) (Tidak Kepakek)')
    F_02 = models.DateField(null=True, blank=True, help_text='Tgl SK Pangkat', db_comment='Tgl SK Pangkat (Tidak Kepakek)')
    F_TMT = models.DateField(null=True, blank=True, help_text='TMT PANGKAT', db_comment='TMT PANGKAT (Tidak Kepakek)')
    F_03 = models.SmallIntegerField(null=True, blank=True, help_text='Golongan / Ruang terakhir', db_comment='Golongan / Ruang terakhir')
    F_SK = models.CharField(max_length=40, null=True, blank=True, help_text='No SK pangkat', db_comment='No SK pangkat (Tidak Kepakek)')
    F_PK = models.CharField(max_length=7, null=True, blank=True, db_comment='(TIDAK KEPAKEK)')
    F_04 = models.CharField(max_length=4, null=True, blank=True, help_text='Masa Kerja', db_comment='Masa Kerja')

    G_01 = models.DateField(null=True, blank=True, help_text='TMT Gaji Berkala', db_comment='TMT Gaji Berkala')
    G_02 = models.CharField(max_length=4, null=True, blank=True, help_text='Masa Kerja (Gaji)', db_comment='Masa Kerja (Gaji)')
    G_03 = models.FloatField(null=True, blank=True, help_text='Gaji Pokok', db_comment='Gaji Pokok')
    H_1A = models.SmallIntegerField(null=True, blank=True)

    I_01 = models.CharField(max_length=1, null=True, blank=True, help_text='Ditetapkan oleh (jbtn)', db_comment='Ditetapkan oleh (jbtn)')
    I_02 = models.CharField(max_length=30, null=True, blank=True, help_text='Nomor SK Jabatan', db_comment='Nomor SK Jabatan')
    I_03 = models.DateField(null=True, blank=True, help_text='Tanggal SK Jabatan', db_comment='Tanggal SK Jabatan')
    I_04 = models.DateField(null=True, blank=True, help_text='TMT Jabatan', db_comment='TMT Jabatan')
    I_05 = models.BigIntegerField(null=True, blank=True, help_text='kode_jabatan', db_comment='kode_jabatan')
    I_5A = models.CharField(max_length=3, null=True, blank=True, help_text='jenis_jabatan', db_comment='jenis_jabatan')
    I_06 = models.ForeignKey(
        'master_data.MdEselon',
        on_delete=models.DO_NOTHING,
        db_column='I_06',
        related_name='pegawai_eselon_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='Eselon',
        db_comment='Eselon',
    )
    I_07 = models.ForeignKey(
        'master_data.MdJenjangJabatan',
        on_delete=models.DO_NOTHING,
        db_column='I_07',
        related_name='pegawai_jenjang_jabatan_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='jenjang',
        db_comment='jenjang',
    )
    I_JB = models.CharField(max_length=150, null=True, blank=True, help_text='jabatan terakhir', db_comment='jabatan terakhir (Tidak Kepakek)')
    AK_JFK = models.FloatField(null=True, blank=True)
    AK_TMT = models.DateField(null=True, blank=True)

    J_01 = models.ForeignKey(
        'master_data.MdStatusPerkawinan',
        on_delete=models.DO_NOTHING,
        db_column='J_01',
        related_name='pegawai_status_perkawinan_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='Status Kawin',
        db_comment='Status Kawin',
    )
    J_02 = models.CharField(max_length=1, null=True, blank=True)
    J_03 = models.CharField(max_length=1, null=True, blank=True)
    K_01 = models.CharField(max_length=1, null=True, blank=True)

    L_01 = models.CharField(max_length=1, null=True, blank=True)
    L_01A = models.CharField(max_length=30, null=True, blank=True, help_text='nomor kartu askes', db_comment='nomor kartu askes')
    L_02 = models.CharField(max_length=1, null=True, blank=True, help_text='kartu taspen', db_comment='kartu taspen')
    L_02A = models.CharField(max_length=30, null=True, blank=True, help_text='NOMOR TASPEN', db_comment='NOMOR TASPEN')
    L_03 = models.CharField(max_length=30, null=True, blank=True, help_text='NPWP', db_comment='NPWP')
    L_04 = models.CharField(max_length=255, null=True, blank=True, help_text='Nomor Karis/Karsu', db_comment='Nomor Karis/Karsu')
    L_05 = models.CharField(max_length=40, null=True, blank=True, help_text='tabrum2', db_comment='tabrum2')
    L_06 = models.DateField(null=True, blank=True, help_text='tanggal_taspen', db_comment='tanggal_taspen')
    L_07 = models.DateField(null=True, blank=True, help_text='npwp_tanggal', db_comment='npwp_tanggal')
    L_08 = models.IntegerField(null=True, blank=True, help_text='id_kpkn', db_comment='id_kpkn')

    M_01 = models.DateField(null=True, blank=True, help_text='Masa Awal Kerja pada PPPK', db_comment='Masa Awal Kerja pada PPPK')
    M_02 = models.DateField(null=True, blank=True, help_text='Masa Akhir Kerja pada PPPK', db_comment='Masa Akhir Kerja pada PPPK')

    kpe_no = models.CharField(max_length=20, null=True, blank=True)
    kpe_rek = models.CharField(max_length=25, null=True, blank=True)
    kpe_tmp = models.CharField(max_length=20, null=True, blank=True)
    kpe_tgl = models.DateField(null=True, blank=True)
    slb = models.IntegerField(null=True, blank=True, help_text='diisi jika ybs @ guru slb', db_comment='diisi jika ybs @ guru slb')
    conf = models.CharField(max_length=4, null=True, blank=True)
    id_bkn = models.CharField(max_length=42, null=True, blank=True, help_text='ID SAPK untuk referensi ke Aplikasi SAPK BKN', db_comment='ID SAPK untuk referensi ke Aplikasi SAPK BKN')

    id_penjabat = models.ForeignKey(
        'master_data.BknJenisPenugasan',
        on_delete=models.DO_NOTHING,
        db_column='id_penjabat',
        related_name='pegawai_jenis_penugasan_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='id_jenis_penugasan',
        db_comment='id_jenis_penugasan',
    )
    id_opd_rangkap = models.ForeignKey(
        'master_data.MsUnitOrganisasi',
        to_field='id_opd',
        on_delete=models.DO_NOTHING,
        db_column='id_opd_rangkap',
        related_name='pegawai_id_opd_rangkap_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='khusus penjabat rangkap',
        db_comment='khusus penjabat rangkap',
    )
    id_jabatan_rangkap = models.ForeignKey(
        'master_data.MsJabatanStruktural',
        to_field='id_jabatan',
        on_delete=models.DO_NOTHING,
        db_column='id_jabatan_rangkap',
        related_name='pegawai_jabatan_rangkap_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='khusus penjabat rangkap',
        db_comment='khusus penjabat rangkap',
    )
    id_sub_opd_rangkap = models.ForeignKey(
        'master_data.MsUnitOrganisasi',
        to_field='id_opd',
        on_delete=models.DO_NOTHING,
        db_column='id_sub_opd_rangkap',
        related_name='pegawai_id_sub_opd_rangkap_children',
        db_constraint=False,
        null=True,
        blank=True,
        help_text='khusus penjabat rangkap',
        db_comment='khusus penjabat rangkap',
    )

    class Meta:
        db_table = 'Ms_pegawai'
        app_label = 'pegawai'
        verbose_name = 'Data Pegawai'
        verbose_name_plural = 'Data Pegawai'

    def __str__(self):
        return f"{self.B_02B or self.B_02} - {self.B_03}"

    @property
    def id_jenis_penugasan(self):
        return self.id_penjabat

    @property
    def id_jenis_penugasan_id(self):
        return self.id_penjabat_id

    @property
    def nip(self):
        return self.B_02B or str(self.B_02) if self.B_02 else None

    @property
    def nip_baru(self):
        v = (self.B_02B or '').strip() if isinstance(self.B_02B, str) else self.B_02B
        return v or None

    @property
    def nip_lama(self):
        return str(self.B_02) if self.B_02 else None

    @property
    def nip_display(self):
        if self.nip_baru and self.nip_lama and self.nip_baru != self.nip_lama:
            return f"{self.nip_baru} / {self.nip_lama}"
        return self.nip_baru or self.nip_lama

    @property
    def nama_lengkap(self):
        nama_parts = []
        if self.B_03A:
            nama_parts.append(self.B_03A)
        if self.B_03:
            nama_parts.append(self.B_03)
        if self.B_03B:
            nama_parts.append(self.B_03B)
        return ' '.join(nama_parts)

    @property
    def nama_display(self):
        return self.nama_lengkap

    @property
    def status_pegawai(self):
        kategori_id = getattr(self, 'B_09_id', None)
        if kategori_id in ('1', 1):
            return 'CPNS'
        if kategori_id in ('2', 2):
            return 'PNS'
        return 'PPPK' if self.M_01 else 'Unknown'

    @property
    def tugas_tambahan_label(self):
        if self.tugas_tambahan == 1:
            return 'Memberikan Tugas Tambahan'
        if self.tugas_tambahan == 0:
            return 'Tidak Memberikan Tugas Tambahan'
        return None

    @property
    def status_apel_label(self):
        if self.B_13 == 1:
            return 'Mengikuti Apel Gabungan di Lapangan Bupati'
        if self.B_13 == 0:
            return 'Tidak Mengikuti Apel Gabungan di Lapangan Bupati'
        return None

    @property
    def sumpah_janji_label(self):
        if self.E_06 == '1':
            return 'SUDAH'
        if self.E_06 == '2':
            return 'BELUM'
        if self.E_06 == '3':
            return 'TIDAK DIKETAHUI'
        return None

    def _masa_kerja_label_from_0000(self, value):
        if value is None:
            return None
        s = str(value).strip()
        if not s or s == '0' or s == '0000':
            return None
        if len(s) != 4 or not s.isdigit():
            return s
        tahun = int(s[:2])
        bulan = int(s[2:])
        if tahun == 0 and bulan == 0:
            return None
        return f'{tahun:02d} tahun {bulan:02d} bulan'

    @property
    def masa_kerja_pangkat_label(self):
        return self._masa_kerja_label_from_0000(self.F_04)

    @property
    def masa_kerja_gaji_label(self):
        return self._masa_kerja_label_from_0000(self.G_02)

    @property
    def pangkat_terakhir_label(self):
        value = self.F_03
        if value is None or value == 0 or value == '0' or value == '':
            return None

        kategori_id = getattr(self, 'B_09_id', None)

        if kategori_id in ('1', 1, '2', 2):
            try:
                from apps.master_data.models import MdPangkat

                pangkat = MdPangkat.objects.filter(id=int(value)).first()
                return str(pangkat) if pangkat else str(value)
            except Exception:
                return str(value)

        def to_roman(n: int):
            if n <= 0:
                return str(n)
            vals = [
                (1000, 'M'),
                (900, 'CM'),
                (500, 'D'),
                (400, 'CD'),
                (100, 'C'),
                (90, 'XC'),
                (50, 'L'),
                (40, 'XL'),
                (10, 'X'),
                (9, 'IX'),
                (5, 'V'),
                (4, 'IV'),
                (1, 'I'),
            ]
            out = []
            for v, s in vals:
                while n >= v:
                    out.append(s)
                    n -= v
            return ''.join(out)

        try:
            n = int(value)
            idx_map = _md_pangkat_order_index_map()
            idx = idx_map.get(n)
            if idx:
                return to_roman(idx)
            return str(value)
        except (TypeError, ValueError):
            return str(value)
