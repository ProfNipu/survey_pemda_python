"""
Signals untuk Survey App
Otomatis membuat snapshot pegawai saat periode survey diaktifkan
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PeriodeSurvey, PegawaiRiwayatData
from apps.accounts.services import EsimpegAPIService
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=PeriodeSurvey)
def check_periode_activation(sender, instance, **kwargs):
    """
    Cek apakah periode survey baru diaktifkan
    Simpan status lama untuk dibandingkan di post_save
    """
    if instance.pk:
        try:
            old_instance = PeriodeSurvey.objects.get(pk=instance.pk)
            instance._old_is_active = old_instance.is_active
            instance._old_status = old_instance.status
        except PeriodeSurvey.DoesNotExist:
            instance._old_is_active = False
            instance._old_status = None
    else:
        instance._old_is_active = False
        instance._old_status = None


@receiver(post_save, sender=PeriodeSurvey)
def create_snapshot_on_periode_activation(sender, instance, created, **kwargs):
    """
    Otomatis membuat snapshot pegawai saat periode survey diaktifkan
    
    Kondisi:
    1. Periode baru dibuat DAN is_active=True DAN status='aktif'
    2. Periode existing diubah dari is_active=False ke is_active=True
    3. Periode existing status berubah menjadi 'aktif'
    """
    should_create_snapshot = False
    
    # Kondisi 1: Periode baru dibuat dan langsung aktif
    if created and instance.is_active and instance.status == 'aktif':
        should_create_snapshot = True
        logger.info(f'Periode baru dibuat dan aktif: {instance}')
    
    # Kondisi 2 & 3: Periode existing diaktifkan atau status berubah ke aktif
    elif not created:
        old_is_active = getattr(instance, '_old_is_active', False)
        old_status = getattr(instance, '_old_status', None)
        
        # Diaktifkan dari nonaktif ke aktif
        if not old_is_active and instance.is_active and instance.status == 'aktif':
            should_create_snapshot = True
            logger.info(f'Periode diaktifkan: {instance}')
        
        # Status berubah ke aktif
        elif old_status != 'aktif' and instance.status == 'aktif' and instance.is_active:
            should_create_snapshot = True
            logger.info(f'Periode status berubah ke aktif: {instance}')
    
    if should_create_snapshot:
        # Cek apakah sudah ada snapshot
        existing_count = PegawaiRiwayatData.objects.filter(periode_survey=instance).count()
        
        if existing_count > 0:
            logger.info(f'Snapshot sudah ada ({existing_count} records) untuk periode {instance}. Skip.')
            return
        
        logger.info(f'Membuat snapshot pegawai untuk periode: {instance}')
        
        try:
            # Ambil data pegawai dari ESIMPEG API
            api_service = EsimpegAPIService()
            pegawai_list = api_service.get_pegawai_list()
            
            if not pegawai_list:
                logger.warning(f'Tidak ada data pegawai dari API untuk periode {instance}')
                return
            
            created_count = 0
            error_count = 0
            
            for pegawai_data in pegawai_list:
                try:
                    PegawaiRiwayatData.objects.create(
                        periode_survey=instance,
                        jenis_survey=instance.jenis_survey,
                        id_pegawai=pegawai_data.get('id_pegawai'),
                        nip_baru=pegawai_data.get('nipPegawai'),
                        nip_lama=pegawai_data.get('nipLama'),
                        nama_pegawai=pegawai_data.get('namaPegawai', ''),
                        tempat_lahir=pegawai_data.get('tempatLahir'),
                        tanggal_lahir=pegawai_data.get('tanggalLahir'),
                        jenis_kelamin=pegawai_data.get('jenisKelamin'),
                        alamat_rumah=pegawai_data.get('alamatRumah'),
                        no_hp=pegawai_data.get('noHp'),
                        id_jabatan=pegawai_data.get('id_jabatan'),
                        nama_jabatan=pegawai_data.get('namaJabatan'),
                        masa_kerja_jabatan=pegawai_data.get('masaKerjaJabatan'),
                        kode_eselon=pegawai_data.get('kodeEselon'),
                        nama_eselon=pegawai_data.get('namaEselon'),
                        id_opd=pegawai_data.get('id_opd'),
                        nm_opd=pegawai_data.get('namaOpd'),
                        id_opd_urut=pegawai_data.get('id_opd_urut'),
                        is_opd_induk=pegawai_data.get('is_opd_induk', False),
                        id_sub_opd=pegawai_data.get('id_sub_opd'),
                        nm_sub_opd=pegawai_data.get('namaSubOpd'),
                        id_golongan=pegawai_data.get('kodeGolongan'),
                        nama_golongan=pegawai_data.get('namaGolongan'),
                        nama_pangkat=pegawai_data.get('namaPangkat'),
                        kategori_pegawai=pegawai_data.get('kategoriPegawai'),
                        nama_kategori_pegawai=pegawai_data.get('namaKategoriPegawai'),
                        tmt_cpns=pegawai_data.get('tmtCpns'),
                        masa_kerja_tahun=pegawai_data.get('masaKerjaTahun'),
                        masa_kerja_bulan=pegawai_data.get('masaKerjaBulan'),
                        akhir_kerja_p3k=pegawai_data.get('akhirKerjaP3k'),
                        raw_data=pegawai_data,
                        snapshot_by=None
                    )
                    created_count += 1
                
                except Exception as e:
                    error_count += 1
                    logger.error(f'Error creating snapshot for pegawai {pegawai_data.get("id_pegawai")}: {str(e)}')
            
            logger.info(f'Snapshot selesai dibuat: {created_count} pegawai berhasil, {error_count} gagal')
        
        except Exception as e:
            logger.exception(f'Error creating snapshot for periode {instance}: {str(e)}')
