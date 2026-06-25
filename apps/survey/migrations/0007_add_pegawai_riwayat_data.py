# Generated manually for pegawai_riwayat_data table

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('survey', '0006_add_periode_to_responden'),
    ]

    operations = [
        migrations.CreateModel(
            name='PegawaiRiwayatData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_pegawai', models.BigIntegerField(db_index=True, verbose_name='ID Pegawai')),
                ('nip_baru', models.CharField(blank=True, db_index=True, max_length=50, null=True, verbose_name='NIP Baru')),
                ('nip_lama', models.CharField(blank=True, max_length=50, null=True, verbose_name='NIP Lama')),
                ('nama_pegawai', models.CharField(db_index=True, max_length=255, verbose_name='Nama Pegawai')),
                ('tempat_lahir', models.CharField(blank=True, max_length=100, null=True, verbose_name='Tempat Lahir')),
                ('tanggal_lahir', models.CharField(blank=True, max_length=50, null=True, verbose_name='Tanggal Lahir')),
                ('jenis_kelamin', models.IntegerField(blank=True, null=True, verbose_name='Jenis Kelamin')),
                ('alamat_rumah', models.TextField(blank=True, null=True, verbose_name='Alamat')),
                ('no_hp', models.CharField(blank=True, max_length=50, null=True, verbose_name='No HP')),
                ('id_jabatan', models.BigIntegerField(blank=True, null=True, verbose_name='ID Jabatan')),
                ('nama_jabatan', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nama Jabatan')),
                ('masa_kerja_jabatan', models.CharField(blank=True, max_length=100, null=True, verbose_name='Masa Kerja Jabatan')),
                ('kode_eselon', models.BigIntegerField(blank=True, db_index=True, null=True, verbose_name='Kode Eselon')),
                ('nama_eselon', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nama Eselon')),
                ('id_opd', models.BigIntegerField(blank=True, db_index=True, null=True, verbose_name='ID OPD')),
                ('nm_opd', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nama OPD')),
                ('id_opd_urut', models.IntegerField(blank=True, db_index=True, null=True, verbose_name='Urutan OPD (A_12)')),
                ('is_opd_induk', models.BooleanField(db_index=True, default=False, verbose_name='Is OPD Induk')),
                ('id_sub_opd', models.BigIntegerField(blank=True, null=True, verbose_name='ID Sub OPD')),
                ('nm_sub_opd', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nama Sub OPD')),
                ('id_golongan', models.BigIntegerField(blank=True, db_index=True, null=True, verbose_name='ID Golongan')),
                ('nama_golongan', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nama Golongan')),
                ('nama_pangkat', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nama Pangkat')),
                ('kategori_pegawai', models.IntegerField(blank=True, db_index=True, null=True, verbose_name='Kategori Pegawai (1=CPNS, 2=PNS, 3=P3K)')),
                ('nama_kategori_pegawai', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nama Kategori Pegawai')),
                ('tmt_cpns', models.CharField(blank=True, max_length=50, null=True, verbose_name='TMT CPNS')),
                ('masa_kerja_tahun', models.IntegerField(blank=True, null=True, verbose_name='Masa Kerja (Tahun)')),
                ('masa_kerja_bulan', models.IntegerField(blank=True, null=True, verbose_name='Masa Kerja (Bulan)')),
                ('akhir_kerja_p3k', models.CharField(blank=True, max_length=50, null=True, verbose_name='Akhir Kerja P3K')),
                ('raw_data', models.JSONField(help_text='Full JSON response dari ESIMPEG API', verbose_name='Raw Data dari API')),
                ('snapshot_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Waktu Snapshot Diambil')),
                ('jenis_survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pegawai_snapshots', to='survey.jenissurvey', verbose_name='Jenis Survey')),
                ('periode_survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pegawai_snapshots', to='survey.periodesurvey', verbose_name='Periode Survey')),
                ('snapshot_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Snapshot Dibuat Oleh')),
            ],
            options={
                'verbose_name': 'Riwayat Data Pegawai (Snapshot)',
                'verbose_name_plural': 'Riwayat Data Pegawai (Snapshot)',
                'db_table': 'pegawai_riwayat_data',
                'ordering': ['-snapshot_at'],
                'unique_together': {('periode_survey', 'id_pegawai')},
            },
        ),
        migrations.AddIndex(
            model_name='pegawairiwayatdata',
            index=models.Index(fields=['periode_survey', 'nip_baru'], name='pegawai_riw_periode_idx'),
        ),
        migrations.AddIndex(
            model_name='pegawairiwayatdata',
            index=models.Index(fields=['jenis_survey', 'id_pegawai'], name='pegawai_riw_jenis_idx'),
        ),
        migrations.AddIndex(
            model_name='pegawairiwayatdata',
            index=models.Index(fields=['periode_survey', 'id_opd'], name='pegawai_riw_opd_idx'),
        ),
        migrations.AddIndex(
            model_name='pegawairiwayatdata',
            index=models.Index(fields=['periode_survey', 'kode_eselon'], name='pegawai_riw_eselon_idx'),
        ),
        migrations.AddIndex(
            model_name='pegawairiwayatdata',
            index=models.Index(fields=['snapshot_at'], name='pegawai_riw_snapshot_idx'),
        ),
    ]
