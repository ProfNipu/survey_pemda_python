from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Custom user manager untuk User model tanpa is_staff & is_superuser
    """
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create and save a regular user"""
        if not username:
            raise ValueError('Username harus diisi')
        
        # Remove is_staff & is_superuser jika ada
        extra_fields.pop('is_staff', None)
        extra_fields.pop('is_superuser', None)
        
        # Default values
        extra_fields.setdefault('is_active', True)
        
        if email:
            email = self.normalize_email(email)
        
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_active', True)
        
        # Remove is_staff & is_superuser jika ada
        extra_fields.pop('is_staff', None)
        extra_fields.pop('is_superuser', None)
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser):
    """
    Custom User model - sesuai struktur users table
    
    Struktur Laravel:
    - id (auto)
    - id_pegawai (integer)
    - user_id_opd (integer, nullable)
    - name (string 191)
    - email (string 191, unique) → Di Django jadi username (bisa email/NIP/custom)
    - email_verified_at (timestamp, nullable)
    - password (string 191)
    - image (string 150)
    - remember_token
    - id_status (integer, default 1)
    - created_at, updated_at
    
    CATATAN:
    - username field digunakan untuk login
    - username bisa berisi: Email, NIP, atau Username custom
    - email field jadi optional (tidak wajib)
    - Role/permission management menggunakan sistem custom
    """
    
    # Laravel: name field (CharField 191)
    name = models.CharField(
        'name',
        max_length=191,
        help_text='Nama lengkap user (match Laravel)'
    )
    
    # Laravel: email unique (nullable)
    email = models.EmailField(
        'email',
        max_length=191,
        unique=True,
        null=True,
        blank=True,
        help_text='Email user (unique, nullable, match Laravel)'
    )
    
    # Username untuk login (bisa email atau NIP)
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Username untuk login (bisa berisi email, NIP, atau custom username)'
    )
    
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active.'
    )
    
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    
    # Foreign key to pegawai (match Laravel)
    id_pegawai = models.IntegerField(
        null=True, 
        blank=True,
        help_text='FK ke ms_pegawai (match Laravel)'
    )
    
    # OPD user ID (match Laravel)
    user_id_opd = models.IntegerField(
        null=True, 
        blank=True,
        help_text='ID OPD user (nullable)'
    )
    
    
    # Laravel: image field (match Laravel - string 150)
    image = models.CharField(
        max_length=150,
        default='',
        help_text='Path to profile image'
    )
    
    # email_verified_at already handled by AbstractUser's email field
    # remember_token handled by Django session framework
    # password already in AbstractUser
    # created_at, updated_at will be added via date_joined and custom field
    
    updated_at = models.DateTimeField(auto_now=True)
    
    # Django compatibility: groups and permissions
    # Add these for compatibility with Django admin and permission system
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    
    # Required for authentication
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']  # Fields required when creating superuser (besides username & password) - email optional
    
    objects = CustomUserManager()
    
    class Meta:
        app_label = 'accounts'  # Just the app name, not the full path
        db_table = 'users'  # Match Laravel table name
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.name if self.name else self.username
    
    @property
    def pegawai(self):
        """Get related pegawai data"""
        if self.id_pegawai:
            try:
                # Import here to avoid circular import
                from apps.pegawai.models import MsPegawai
                return MsPegawai.objects.get(id_pegawai=self.id_pegawai)
            except Exception:
                return None
        return None
    
    def get_full_name(self):
        """Override to return name"""
        return self.name
    
    def get_short_name(self):
        """Override to return name or username"""
        return self.name or self.username
    
    def has_perm(self, perm, obj=None):
        """
        Override has_perm - permission di-handle oleh custom system
        """
        return self.is_active
    
    def has_module_perms(self, app_label):
        """
        Override has_module_perms - permission di-handle oleh custom system
        """
        return self.is_active
    
    @property
    def is_staff(self):
        """
        Property untuk kompatibilitas dengan Django
        Tidak digunakan untuk kontrol akses di aplikasi ini
        """
        return False
    
    @property
    def is_superuser(self):
        """
        Property untuk kompatibilitas dengan permission system
        Bisa dikustomisasi logic-nya, misalnya:
        - Check username == 'admin'
        - Check id_status tertentu
        - Check custom field
        
        Untuk sekarang: return False (semua user pakai custom permission)
        """
        # Option 1: Semua user bukan superuser (pakai custom permission)
        return False
        
        # Option 2: Username 'admin' adalah superuser
        # return self.username == 'admin'
        
        # Option 3: Check custom field atau id_status
        # return self.id_status == 99  # contoh
