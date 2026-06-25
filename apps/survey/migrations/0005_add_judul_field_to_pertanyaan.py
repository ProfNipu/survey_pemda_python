# Generated migration for adding judul field to PertanyaanSurvey

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_surveyconfiguration_surveyaspek_surveyresponse_and_more'),
    ]

    operations = [
        # Step 1: Add new field 'judul' (nullable first)
        migrations.AddField(
            model_name='pertanyaansurvey',
            name='judul',
            field=models.CharField(max_length=200, null=True, blank=True, verbose_name='Judul Aspek'),
        ),
        
        # Step 2: Copy data from 'pertanyaan' to 'judul'
        migrations.RunSQL(
            sql="UPDATE survey_pertanyaan SET judul = pertanyaan WHERE judul IS NULL;",
            reverse_sql="UPDATE survey_pertanyaan SET judul = NULL;",
        ),
        
        # Step 3: Make 'judul' non-nullable
        migrations.AlterField(
            model_name='pertanyaansurvey',
            name='judul',
            field=models.CharField(max_length=200, verbose_name='Judul Aspek'),
        ),
        
        # Step 4: Change 'pertanyaan' to allow longer text and make it nullable temporarily
        migrations.AlterField(
            model_name='pertanyaansurvey',
            name='pertanyaan',
            field=models.TextField(null=True, blank=True, verbose_name='Pertanyaan Lengkap'),
        ),
        
        # Step 5: Clear old data from 'pertanyaan' field (optional - bisa di-skip kalau mau keep data)
        migrations.RunSQL(
            sql="UPDATE survey_pertanyaan SET pertanyaan = NULL;",
            reverse_sql="UPDATE survey_pertanyaan SET pertanyaan = judul;",
        ),
    ]
