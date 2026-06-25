# Generated manually to add nama_kategori_pegawai field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_simpeg', '0006_add_kategori_pegawai_and_rename_no_urut'),
    ]

    operations = [
        migrations.AddField(
            model_name='pegawai',
            name='nama_kategori_pegawai',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Nama Kategori Pegawai'),
        ),
    ]
