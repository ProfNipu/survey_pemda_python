from django import forms
from django.forms import inlineformset_factory
from .models_survey_config import SurveyConfiguration, SurveyAspek, SurveyResponse, SurveyResponseDetail


class SurveyConfigurationForm(forms.ModelForm):
    """Form untuk konfigurasi survey oleh Super Admin"""
    
    class Meta:
        model = SurveyConfiguration
        fields = [
            'nama_survey', 'deskripsi', 'tahun', 'periode_mulai', 'periode_selesai',
            'show_pegawai_penilai', 'show_foto_pegawai', 'is_active'
        ]
        widgets = {
            'nama_survey': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Survey 360° - Penilaian Kinerja Pegawai'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Deskripsi survey...'
            }),
            'tahun': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2020,
                'max': 2030
            }),
            'periode_mulai': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'periode_selesai': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'show_pegawai_penilai': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_foto_pegawai': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class SurveyAspekForm(forms.ModelForm):
    """Form untuk aspek penilaian"""
    
    class Meta:
        model = SurveyAspek
        fields = [
            'nama_aspek', 'deskripsi', 'urutan', 'skala_min', 'skala_max',
            'label_min', 'label_max', 'is_required', 'is_active'
        ]
        widgets = {
            'nama_aspek': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Berorientasi Pelayanan'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Sejauh mana pegawai mampu memberikan pelayanan yang cepat, ramah, dan solutif...'
            }),
            'urutan': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'skala_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5
            }),
            'skala_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2,
                'max': 10
            }),
            'label_min': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sangat Kurang'
            }),
            'label_max': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sangat Baik'
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


# Inline formset untuk mengelola aspek dalam satu form
SurveyAspekFormSet = inlineformset_factory(
    SurveyConfiguration,
    SurveyAspek,
    form=SurveyAspekForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class DynamicSurveyResponseForm(forms.ModelForm):
    """Form dinamis untuk response survey berdasarkan konfigurasi"""
    
    def __init__(self, survey_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.survey_config = survey_config
        
        # Tambahkan field untuk setiap aspek
        for aspek in survey_config.aspek_penilaian.filter(is_active=True).order_by('urutan'):
            field_name = f'aspek_{aspek.id}'
            self.fields[field_name] = forms.IntegerField(
                label=aspek.nama_aspek,
                help_text=aspek.deskripsi,
                min_value=aspek.skala_min,
                max_value=aspek.skala_max,
                required=aspek.is_required,
                widget=forms.HiddenInput()  # Will be replaced by slider in template
            )
    
    class Meta:
        model = SurveyResponse
        fields = [
            'nip_dinilai', 'nama_dinilai', 'jabatan_dinilai', 'unit_kerja_dinilai',
            'komentar', 'saran'
        ]
        widgets = {
            'nip_dinilai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'NIP Pegawai yang Dinilai'
            }),
            'nama_dinilai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Pegawai yang Dinilai'
            }),
            'jabatan_dinilai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jabatan Pegawai yang Dinilai'
            }),
            'unit_kerja_dinilai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unit Kerja Pegawai yang Dinilai'
            }),
            'komentar': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Komentar (opsional)'
            }),
            'saran': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Saran (opsional)'
            }),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.survey_config = self.survey_config
        
        if commit:
            instance.save()
            
            # Simpan detail jawaban
            for field_name, value in self.cleaned_data.items():
                if field_name.startswith('aspek_') and value is not None:
                    aspek_id = field_name.replace('aspek_', '')
                    aspek = SurveyAspek.objects.get(id=aspek_id)
                    
                    SurveyResponseDetail.objects.update_or_create(
                        response=instance,
                        aspek=aspek,
                        defaults={'nilai': value}
                    )
        
        return instance