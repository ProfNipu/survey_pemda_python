"""
Custom Password Hashers untuk support Laravel bcrypt hash
"""
from django.contrib.auth.hashers import BCryptSHA256PasswordHasher
import bcrypt


class LaravelBcryptPasswordHasher(BCryptSHA256PasswordHasher):
    """
    Custom hasher untuk support Laravel bcrypt format
    
    Laravel format: $2y$10$salt+hash (60 chars)
    Django bcrypt: bcrypt_sha256$$2b$12$salt+hash
    
    Hasher ini akan:
    1. Verify password dari Laravel (format $2y$)
    2. Create new password dalam format Django (format bcrypt$)
    """
    
    algorithm = "laravel_bcrypt"
    
    def verify(self, password, encoded):
        """
        Verify password - support both Laravel and Django format
        """
        # Extract hash part after algorithm prefix (laravel_bcrypt$hash)
        if '$' in encoded:
            parts = encoded.split('$', 1)
            if len(parts) > 1:
                hash_part = parts[1]  # Get part after first $
            else:
                hash_part = encoded
        else:
            hash_part = encoded
        
        # Verify raw Laravel bcrypt hash
        if hash_part.startswith(('$2y$', '$2b$', '$2a$')):
            # Laravel uses $2y$ but Python bcrypt only supports $2b$
            # Convert $2y$ to $2b$ (they are compatible)
            hash_for_check = hash_part.replace('$2y$', '$2b$')
            
            # Direct bcrypt verify (Laravel format)
            password_bytes = password.encode('utf-8')
            hash_bytes = hash_for_check.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        
        # Fallback to Django format
        return super().verify(password, encoded)
    
    def encode(self, password, salt):
        """
        Encode password menggunakan plain bcrypt (compatible dengan Laravel)
        
        Returns format: laravel_bcrypt$$2b$12$salt+hash
        
        Note: Tidak menggunakan SHA256 seperti BCryptSHA256PasswordHasher
        karena Laravel menggunakan plain bcrypt
        """
        # Generate bcrypt hash (plain, no SHA256)
        password_bytes = password.encode('utf-8')
        
        # Use bcrypt with default rounds (12)
        bcrypt_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
        
        # Return Django format: algorithm$hash
        return f"{self.algorithm}${bcrypt_hash.decode('utf-8')}"
    
    def safe_summary(self, encoded):
        """Return a summary of the password hash"""
        algorithm, empty, data = encoded.partition('$')
        assert algorithm == self.algorithm
        
        # Handle Laravel format
        if data.startswith(('2y$', '2b$', '2a$')):
            cost, salt_hash = data.split('$', 1)
            return {
                'algorithm': algorithm,
                'cost': cost,
                'salt': salt_hash[:22] if len(salt_hash) > 22 else salt_hash,
            }
        
        return super().safe_summary(encoded)


class LaravelCompatibleBcryptHasher(BCryptSHA256PasswordHasher):
    """
    Simple bcrypt hasher that accepts Laravel $2y$ format
    """
    algorithm = "bcrypt"
    
    def verify(self, password, encoded):
        """
        Verify - accept both Laravel ($2y$) and Django (bcrypt$) format
        """
        # Strip Django prefix if exists
        if encoded.startswith('bcrypt$'):
            encoded = encoded[7:]  # Remove "bcrypt$" prefix
        
        # Strip bcrypt_sha256 prefix if exists  
        if encoded.startswith('bcrypt_sha256$'):
            encoded = encoded[14:]
        
        # Convert Laravel $2y$ to Python-compatible $2b$
        encoded = encoded.replace('$2y$', '$2b$')
        
        # Now encoded should be raw bcrypt hash
        try:
            password_bytes = password.encode('utf-8')
            encoded_bytes = encoded.encode('utf-8')
            return bcrypt.checkpw(password_bytes, encoded_bytes)
        except Exception:
            return False
    
    def encode(self, password, salt):
        """Encode using bcrypt"""
        return super().encode(password, salt)
