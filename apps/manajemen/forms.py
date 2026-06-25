from django import forms
from .models import MenuItem, MenuCategory
from django.contrib.auth import get_user_model

from apps.common.forms import select_search_attrs


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            'name',
            'icon',
            'type',
            'parent',
            'order',
            'category',
            'is_active',
            'permission_key',
            'url_name',
            'external_url',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25'}),
            'icon': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25', 'placeholder': 'fas fa-folder'}),
            'type': forms.Select(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25'}),
            'parent': forms.Select(attrs={
                **select_search_attrs('Cari parent...', base_class='w-full px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25'),
                'data-disabled-label': '— Tidak perlu Parent —',
            }),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200'}),
            'category': forms.Select(attrs={
                **select_search_attrs(None, base_class='w-full px-4 py-3 rounded-lg border-2 border-gray-200 bg-white text-gray-800 focus:border-primary focus:ring-2 focus:ring-primary/25'),
                'data-disabled-label': '— Mengikuti Kategori Parent —',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary'}),
            'permission_key': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200', 'placeholder': 'module.control.function'}),
            'url_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200', 'placeholder': 'namespace:view_name'}),
            'external_url': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200', 'placeholder': 'https://... or /path/'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Provide choices for 'type' since model has no explicit choices
        self.fields['type'].widget.choices = (
            ('module', 'module'),
            ('menuItem', 'menuItem'),
        )
        # Normalize initial 'type' from instance (case-insensitive)
        try:
            if getattr(self, 'instance', None) and getattr(self.instance, 'pk', None):
                cur = (self.instance.type or '').strip()
                lv = cur.lower()
                if lv == 'menuitem':
                    self.initial['type'] = 'menuItem'
                elif lv == 'module':
                    self.initial['type'] = 'module'
                elif cur:
                    self.initial['type'] = cur
        except Exception:
            pass
        # Dynamic category choices
        default_categories = [
            (1, 'SUPER ADMIN'),
            (2, 'Data Pegawai'),
            (3, 'Laporan Data'),
            (4, 'Manajemen Integrasi'),
            (0, 'Menu Lainnya'),
        ]
        try:
            cats = list(MenuCategory.objects.filter(is_active=True).order_by('order','name').values_list('code','name'))
        except Exception:
            cats = []
        choices = cats if cats else default_categories
        self.fields['category'].widget.choices = choices
        # Category is optional at form level; validation handled in clean()
        try:
            self.fields['category'].required = False
        except Exception:
            pass
        # For edit: if current item is a child (menuItem), reflect parent's category
        try:
            if getattr(self, 'instance', None) and getattr(self.instance, 'pk', None):
                if (getattr(self.instance, 'type', '') or '').lower() == 'menuitem' and getattr(self.instance, 'parent', None):
                    self.initial['category'] = getattr(self.instance.parent, 'category', self.initial.get('category', 0))
        except Exception:
            pass

    def clean(self):
        cleaned = super().clean()
        url_name = cleaned.get('url_name')
        external_url = cleaned.get('external_url')
        if url_name and external_url:
            self.add_error('external_url', 'Hanya pilih salah satu: url_name atau external_url')

        # Normalize and enforce type-parent rules
        t_raw = (cleaned.get('type') or '').strip()
        t_low = str(t_raw).lower()
        t_norm = 'menuItem' if t_low == 'menuitem' else ('module' if t_low == 'module' else (t_raw or 'module'))
        cleaned['type'] = t_norm

        parent = cleaned.get('parent')
        if t_norm == 'module':
            # Module boleh punya parent (opsional). Jika ada parent, ikuti kategori parent.
            if parent:
                try:
                    cleaned['category'] = getattr(parent, 'category', 0)
                except Exception:
                    cleaned['category'] = 0
            else:
                # Tanpa parent, wajib pilih category secara eksplisit
                cat = cleaned.get('category')
                if cat in (None, ''):
                    self.add_error('category', 'Category harus diisi untuk tipe module')
        elif t_norm == 'menuItem':
            if not parent:
                self.add_error('parent', 'Parent wajib dipilih untuk type menuItem')
            else:
                try:
                    cleaned['category'] = getattr(parent, 'category', 0)
                except Exception:
                    cleaned['category'] = 0

        return cleaned


class MenuCategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['code'].error_messages['required'] = 'Kode harus diisi.'
            self.fields['code'].error_messages['unique'] = 'Kode sudah digunakan.'
            self.fields['code'].error_messages.setdefault('invalid', 'Kode tidak valid.')
        except Exception:
            pass
        try:
            self.fields['name'].error_messages['required'] = 'Nama harus diisi.'
            self.fields['name'].error_messages.setdefault('invalid', 'Nama tidak valid.')
        except Exception:
            pass
        try:
            self.fields['order'].error_messages.setdefault('invalid', 'Order tidak valid.')
        except Exception:
            pass
    class Meta:
        model = MenuCategory
        fields = ['code', 'name', 'order', 'is_active']
        widgets = {
            'code': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary'}),
        }
        error_messages = {
            'code': {
                'required': 'Kode harus diisi.',
                'unique': 'Kode sudah digunakan.',
                'invalid': 'Kode tidak valid.'
            },
            'name': {
                'required': 'Nama harus diisi.',
                'invalid': 'Nama tidak valid.'
            },
            'order': {
                'invalid': 'Order tidak valid.'
            },
        }


# ==================== USER FORMS ====================
User = get_user_model()


class UserCreateForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        error_messages={'required': 'Username Harus Diisi.'},
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25', 'placeholder': 'e.g: johndoe'})
    )
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False, error_messages={'invalid': 'Format email tidak valid.'})
    password = forms.CharField(
        required=True,
        min_length=8,
        error_messages={'required': 'Password Harus Diisi.', 'min_length': 'Password minimal 8 karakter.'},
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200', 'placeholder': 'Minimal 8 karakter'})
    )
    is_active = forms.BooleanField(required=False, initial=True)

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        if ' ' in username or not username:
            raise forms.ValidationError('Username tidak boleh mengandung spasi.')
        if username != username.lower():
            raise forms.ValidationError('Username harus huruf kecil semua (lowercase).')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username sudah digunakan.')
        return username

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            return ''
        # Ensure uniqueness (MySQL collation might be case-insensitive, but be explicit)
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email sudah digunakan.')
        return email


class UserEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    username = forms.CharField(
        max_length=150,
        required=True,
        error_messages={'required': 'Username Harus Diisi.'},
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/25', 'placeholder': 'e.g: johndoe'})
    )
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False, error_messages={'invalid': 'Format email tidak valid.'})
    password = forms.CharField(required=False, min_length=8, widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border-2 border-gray-200', 'placeholder': 'Minimal 8 karakter'}))
    is_active = forms.BooleanField(required=False)

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        # Empty is allowed on edit
        if pwd is None or pwd == '':
            return ''
        if len(pwd) < 8:
            raise forms.ValidationError('Password minimal 8 karakter.')
        return pwd

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            return ''
        qs = User.objects.filter(email__iexact=email)
        if self.user is not None:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError('Email sudah digunakan.')
        return email

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        if ' ' in username or not username:
            raise forms.ValidationError('Username tidak boleh mengandung spasi.')
        if username != username.lower():
            raise forms.ValidationError('Username harus huruf kecil semua (lowercase).')
        # Skip uniqueness check if unchanged (case-insensitive compare)
        current = ''
        if getattr(self, 'user', None) is not None and getattr(self.user, 'username', None):
            current = (self.user.username or '').strip().lower()
        if username.lower() == current:
            return username
        qs = User.objects.filter(username__iexact=username)
        if self.user is not None:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError('Username sudah digunakan.')
        return username
