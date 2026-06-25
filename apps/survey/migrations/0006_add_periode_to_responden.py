# Generated migration for adding periode and jenis_survey to RespondenSurvey

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0005_add_judul_field_to_pertanyaan'),
    ]

    operations = [
        # Add jenis_survey field
        migrations.AddField(
            model_name='respondensurvey',
            name='jenis_survey',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='responden',
                to='survey.jenissurvey',
                verbose_name='Jenis Survey'
            ),
        ),
        
        # Add periode field
        migrations.AddField(
            model_name='respondensurvey',
            name='periode',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='responden',
                to='survey.periodesurvey',
                verbose_name='Periode Survey'
            ),
        ),
    ]
