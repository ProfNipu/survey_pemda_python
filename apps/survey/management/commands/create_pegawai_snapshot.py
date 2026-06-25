"""
Management command untuk membuat snapshot data pegawai saat survey dibuka
Snapshot ini akan digunakan untuk laporan survey agar data konsisten
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from apps.survey.models import PeriodeSurvey, PegawaiRiwayatData
from apps.accounts.services import EsimpegAPIService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Membuat snapshot data pegawai dari ESIMPEG API untuk periode survey tertentu'

    def add_arguments(self, parser):
        parser.add_argument(
            '--periode-id',
            type=int,
            help='ID Periode Survey untuk membuat snapshot'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force create snapshot meskipun sudah ada (akan hapus yang lama)'
        )

    def handle(self, *args, **options):
        periode_id = options.get('periode_id')
        force = options.get('force', False)

        if not periode_id:
            self.stdout.write(self.style.ERROR('Error: --periode-id harus diisi'))
            return

        try:
            periode = PeriodeSurvey.objects.select_related('jenis_survey').get(id=periode_id)
        except PeriodeSurvey.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Error: Periode Survey dengan ID {periode_id} tidak ditemukan'))
            return

        self.stdout.write(f'Membuat snapshot untuk: {periode.jenis_survey.nama} - {periode.nama_periode}')
        self.stdout.write(f'Periode: {periode.tanggal_mulai} s/d {periode.tanggal_selesai}')
        
        # Cek apakah sudah ada snapshot
        existing_count = PegawaiRiwayatData.objects.filter(periode_survey=periode).count()
        if existing_count > 0:
            if force:
                self.stdout.write(self.style.WARNING(f'Menghapus {existing_count} snapshot yang sudah ada...'))
                PegawaiRiwayatData.objects.filter(periode_survey=periode).delete()
            else:
                self.stdout.write(self.style.ERROR(
                    f'Error: Sudah ada {existing_count} snapshot untuk periode ini. '
                    f'Gunakan --force untuk menghapus dan membuat ulang.'
                ))
                return

        # Ambil data pegawai dari ESIMPEG API
        self.stdout.write('Mengambil data pegawai dari ESIMPEG API...')
        api_service = EsimpegAPIService()
        
        try:
            pegawai_list = api_service.get_pegawai_list()
            
            if not pegawai_list:
                self.stdout.write(self.style.ERROR('Error: Tidak ada data pegawai dari API'))
                return
            
            self.stdout.write(f'Ditemukan {len(pegawai_list)} pegawai dari API')
            
            # Buat snapshot
            created_count = 0
            error_count = 0
            
            with transaction.atomic():
                for pegawai_data in pegawai_list:
                    try:
                        # Extract data dari API response
                        snapshot = PegawaiRiwayatData(
                            periode_survey=periode,
                            jenis_survey=periode.jenis_survey,
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
                            snapshot_by=None  # System generated
                        )
                        snapshot.save()
                        created_count += 1
                        
                        if created_count % 100 == 0:
                            self.stdout.write(f'Progress: {created_count} pegawai...')
                    
                    except Exception as e:
                        error_count += 1
                        logger.error(f'Error creating snapshot for pegawai {pegawai_data.get("id_pegawai")}: {str(e)}')
                        if error_count <= 5:  # Only show first 5 errors
                            self.stdout.write(self.style.WARNING(
                                f'Warning: Error untuk pegawai {pegawai_data.get("namaPegawai")}: {str(e)}'
                            ))
            
            self.stdout.write(self.style.SUCCESS(
                f'\nSelesai! Berhasil membuat {created_count} snapshot pegawai'
            ))
            
            if error_count > 0:
                self.stdout.write(self.style.WARNING(
                    f'Warning: {error_count} pegawai gagal dibuat snapshot'
                ))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            logger.exception('Error creating pegawai snapshot')
            raise
