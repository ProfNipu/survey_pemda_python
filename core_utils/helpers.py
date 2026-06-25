"""
Global Helpers
Dapat digunakan di semua apps dan modules
"""
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from django.utils import timezone


class URLHelper:
    """Helper untuk URL building dan validation"""
    
    @staticmethod
    def build_api_url(base_url: str, path: str, params: Optional[Dict] = None) -> Optional[str]:
        """
        Build API URL dengan base dan path
        
        Args:
            base_url: Base URL (e.g., 'https://api.example.com')
            path: Path endpoint (e.g., '/users/profile')
            params: Query parameters (optional)
            
        Returns:
            Full URL atau None jika data invalid
            
        Example:
            build_api_url('https://api.bkn.go.id', '/pns/data', {'nip': '123'})
            # Returns: 'https://api.bkn.go.id/pns/data?nip=123'
        """
        if not path:
            return None
            
        # Clean base_url (remove trailing slash)
        base = base_url.rstrip('/')
        
        # Clean path (ensure leading slash)
        clean_path = path if path.startswith('/') else f'/{path}'
        
        url = base + clean_path
        
        # Add query parameters if provided
        if params:
            query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            url = f'{url}?{query_string}'
            
        return url

    @staticmethod
    def validate_nip(nip: str) -> bool:
        """
        Validate NIP format (18 digits)
        
        Args:
            nip: NIP string
            
        Returns:
            True if valid NIP format
        """
        if not nip:
            return False
        return bool(re.match(r'^\d{18}$', str(nip)))


class DataHelper:
    """Helper untuk data processing dan formatting"""
    
    @staticmethod
    def format_response(data: Any, success: bool = True, message: str = '', errors: Optional[List] = None) -> Dict:
        """
        Format standard API response
        
        Args:
            data: Response data
            success: Success status
            message: Response message
            errors: Error list (optional)
            
        Returns:
            Standard response format
        """
        response = {
            'success': success,
            'message': message,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
        
        if errors:
            response['errors'] = errors
            
        return response

    @staticmethod
    def clean_dict(data: Dict, remove_none: bool = True, remove_empty: bool = False) -> Dict:
        """
        Clean dictionary dari values yang tidak diinginkan
        
        Args:
            data: Dictionary to clean
            remove_none: Remove None values
            remove_empty: Remove empty strings/lists
            
        Returns:
            Cleaned dictionary
        """
        if not isinstance(data, dict):
            return data
            
        cleaned = {}
        for key, value in data.items():
            if remove_none and value is None:
                continue
            if remove_empty and value in ('', [], {}):
                continue
            cleaned[key] = value
            
        return cleaned

    @staticmethod
    def format_date(date_obj: Any, format_str: str = '%Y-%m-%d') -> Optional[str]:
        """
        Format date object to string
        
        Args:
            date_obj: Date object (datetime, date, or string)
            format_str: Format string
            
        Returns:
            Formatted date string or None
        """
        if not date_obj:
            return None
            
        try:
            if isinstance(date_obj, str):
                # Try to parse string date
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            elif isinstance(date_obj, date) and not isinstance(date_obj, datetime):
                # Convert date to datetime
                date_obj = datetime.combine(date_obj, datetime.min.time())
                
            return date_obj.strftime(format_str)
        except (ValueError, AttributeError):
            return None


class ValidationHelper:
    """Helper untuk validasi data"""
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> List[str]:
        """
        Validate required fields in dictionary
        
        Args:
            data: Data dictionary
            required_fields: List of required field names
            
        Returns:
            List of missing field names
        """
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing.append(field)
        return missing

    @staticmethod
    def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input
        
        Args:
            text: Input string
            max_length: Maximum length (optional)
            
        Returns:
            Sanitized string
        """
        if not text:
            return ''
            
        # Basic sanitization
        clean_text = str(text).strip()
        
        # Remove dangerous characters (basic XSS prevention)
        dangerous_chars = ['<', '>', '"', "'", '&']
        for char in dangerous_chars:
            clean_text = clean_text.replace(char, '')
            
        # Limit length if specified
        if max_length and len(clean_text) > max_length:
            clean_text = clean_text[:max_length]
            
        return clean_text


class PegawaiHelper:
    """Helper khusus untuk data pegawai"""
    
    @staticmethod
    def format_nama_lengkap(gelar_depan: str = '', nama: str = '', gelar_belakang: str = '') -> str:
        """
        Format nama lengkap pegawai dengan gelar
        
        Args:
            gelar_depan: Gelar depan (e.g., 'Dr.')
            nama: Nama pegawai
            gelar_belakang: Gelar belakang (e.g., 'S.Kom, M.T.')
            
        Returns:
            Formatted full name
        """
        parts = []
        
        if gelar_depan:
            parts.append(gelar_depan.strip())
        if nama:
            parts.append(nama.strip())
        if gelar_belakang:
            parts.append(gelar_belakang.strip())
            
        return ' '.join(parts)

    @staticmethod
    def get_status_pegawai(kode_status: str) -> str:
        """
        Convert status code to readable status
        
        Args:
            kode_status: Status code ('1' = CPNS, '2' = PNS, etc.)
            
        Returns:
            Human readable status
        """
        status_mapping = {
            '1': 'CPNS',
            '2': 'PNS', 
            '3': 'PPPK',
            '4': 'Non ASN'
        }
        return status_mapping.get(kode_status, 'Unknown')

    @staticmethod
    def calculate_masa_kerja(tmt_date: date, end_date: Optional[date] = None) -> Dict[str, int]:
        """
        Calculate masa kerja (years, months, days)
        
        Args:
            tmt_date: TMT date
            end_date: End date (default: today)
            
        Returns:
            Dictionary with years, months, days
        """
        if not end_date:
            end_date = date.today()
            
        if tmt_date > end_date:
            return {'years': 0, 'months': 0, 'days': 0}
            
        years = end_date.year - tmt_date.year
        months = end_date.month - tmt_date.month
        days = end_date.day - tmt_date.day
        
        if days < 0:
            months -= 1
            days += 30  # Approximate
            
        if months < 0:
            years -= 1
            months += 12
            
        return {
            'years': max(0, years),
            'months': max(0, months), 
            'days': max(0, days)
        }


# Global utility functions (dapat digunakan langsung)
def format_currency(amount: float, currency: str = 'IDR') -> str:
    """Format currency amount"""
    if currency == 'IDR':
        return f'Rp {amount:,.0f}'.replace(',', '.')
    return f'{currency} {amount:,.2f}'


def get_current_jakarta_time() -> datetime:
    """Get current Jakarta time"""
    return timezone.now()


def is_weekend(date_obj: date) -> bool:
    """Check if date is weekend (Saturday or Sunday)"""
    return date_obj.weekday() >= 5  # 5 = Saturday, 6 = Sunday
