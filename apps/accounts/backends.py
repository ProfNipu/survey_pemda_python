from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class FlexibleAuthBackend(ModelBackend):
    """
    Custom authentication backend yang support login dengan:
    1. Username (custom username)
    2. NIP (dari id_pegawai / B_02B)
    3. Email
    
    User bisa login dengan salah satu dari ketiganya
    
    PENTING: Backend ini juga akan mencoba mendapatkan token ESIMPEG
    untuk user yang berhasil login, agar bisa melakukan API calls ke ESIMPEG
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Cari user berdasarkan username, email, atau NIP
            # Query: username field ATAU email field bisa match dengan input
            user = User.objects.get(
                Q(username__iexact=username) |  # Match username (case insensitive)
                Q(email__iexact=username)       # Match email (case insensitive)
            )
            
            # Validasi password
            # Django akan otomatis detect Laravel bcrypt format dan verify
            if user.check_password(password):
                # Password valid!
                
                # Coba dapatkan token ESIMPEG untuk user ini
                # Ini penting agar user bisa melakukan sinkronisasi data pegawai
                if request:
                    self._try_get_esimpeg_token(request, username, password)
                
                # Jika password valid dan masih format Laravel ($2y$),
                # Django akan otomatis re-hash ke format Django di next request
                return user
                
        except User.DoesNotExist:
            # User tidak ditemukan
            return None
        except User.MultipleObjectsReturned:
            # Multiple users found (shouldn't happen with proper constraints)
            return None
        
        return None
    
    def _try_get_esimpeg_token(self, request, username, password):
        """
        Mencoba mendapatkan token ESIMPEG untuk user yang login
        Jika berhasil, simpan token ke session
        Jika gagal, tidak masalah (user tetap bisa login, tapi tidak bisa sync)
        """
        try:
            from apps.accounts.services import EsimpegAPIService
            import logging
            
            logger = logging.getLogger(__name__)
            
            api_service = EsimpegAPIService()
            login_result = api_service.login(username, password)
            
            if login_result and 'access_token' in login_result:
                # Berhasil dapat token, simpan ke session
                request.session['esimpeg_access_token'] = login_result.get('access_token')
                request.session['esimpeg_refresh_token'] = login_result.get('refresh_token')
                request.session['esimpeg_token_expires_in'] = login_result.get('expires_in', 86400)
                logger.info(f"ESIMPEG token obtained for user: {username}")
            else:
                logger.info(f"Could not get ESIMPEG token for user: {username} (user may not exist in ESIMPEG)")
        except Exception as e:
            # Gagal dapat token, tapi tidak masalah
            # User tetap bisa login, hanya tidak bisa melakukan sinkronisasi
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to get ESIMPEG token for user {username}: {str(e)}")
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class EsimpegAPIAuthBackend(ModelBackend):
    """
    Fallback authentication backend yang login via ESIMPEG API
    
    Flow:
    1. Coba login ke ESIMPEG API
    2. Jika berhasil, create/update user di database lokal
    3. Return user object untuk login
    
    Backend ini akan dipanggil jika FlexibleAuthBackend gagal (user tidak ada di database lokal)
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        # Import di sini untuk avoid circular import
        from apps.accounts.services import EsimpegAPIService
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # 1. Login via ESIMPEG API
            api_service = EsimpegAPIService()
            login_result = api_service.login(username, password)
            
            if not login_result:
                logger.info(f"ESIMPEG API login failed for user: {username}")
                return None
            
            # 2. Extract user data dari API response
            user_data = login_result.get('user', {})
            if not user_data:
                logger.error("ESIMPEG API login success but no user data returned")
                return None
            
            # 3. Create or update user di database lokal
            user_username = user_data.get('username')
            user_email = user_data.get('email')
            user_name = user_data.get('name', '')
            id_pegawai = user_data.get('id_pegawai')
            user_id_opd = user_data.get('user_id_opd')
            is_active = user_data.get('is_active', True)
            
            if not user_username:
                logger.error("ESIMPEG API returned user without username")
                return None
            
            # Create or update user
            user, created = User.objects.update_or_create(
                username=user_username,
                defaults={
                    'email': user_email or '',
                    'name': user_name,
                    'id_pegawai': id_pegawai,
                    'user_id_opd': user_id_opd,
                    'is_active': is_active,
                }
            )
            
            # Set date_joined only for new users
            if created:
                user.date_joined = timezone.now()
            
            # Set password (hashed) - kita tidak tahu password hash dari API,
            # jadi set password yang baru diinput (Django akan hash otomatis)
            user.set_password(password)
            user.save()
            
            # 4. Store ESIMPEG token di session untuk API calls
            if request:
                request.session['esimpeg_access_token'] = login_result.get('access_token')
                request.session['esimpeg_refresh_token'] = login_result.get('refresh_token')
                request.session['esimpeg_token_expires_in'] = login_result.get('expires_in', 86400)
            
            action = 'created' if created else 'updated'
            logger.info(f"User {action} from ESIMPEG API: {user_username}")
            
            return user if user.is_active else None
            
        except Exception as e:
            logger.error(f"ESIMPEG API authentication error: {str(e)}", exc_info=True)
            return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
