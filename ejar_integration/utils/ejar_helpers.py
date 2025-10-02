# -*- coding: utf-8 -*-

import re
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class EjarHelpers:
    """Helper functions for Ejar integration"""

    @staticmethod
    def validate_saudi_national_id(national_id):
        """Validate Saudi National ID format and checksum"""
        if not national_id:
            return False
        
        # Remove any non-digit characters
        national_id = re.sub(r'\D', '', national_id)
        
        # Check length
        if len(national_id) != 10:
            return False
        
        # Check if it starts with 1 or 2
        if not national_id.startswith(('1', '2')):
            return False
        
        # Calculate checksum
        total = 0
        for i in range(9):
            digit = int(national_id[i])
            if i % 2 == 0:
                total += digit
            else:
                doubled = digit * 2
                total += doubled if doubled < 10 else doubled - 9
        
        checksum = (10 - (total % 10)) % 10
        return checksum == int(national_id[9])
    
    @staticmethod
    def validate_saudi_iqama(iqama_number):
        """Validate Saudi Iqama number format"""
        if not iqama_number:
            return False
        
        # Remove any non-digit characters
        iqama_number = re.sub(r'\D', '', iqama_number)
        
        # Check length
        if len(iqama_number) != 10:
            return False
        
        # Check if it starts with 1 or 2
        if not iqama_number.startswith(('1', '2')):
            return False
        
        return True
    
    @staticmethod
    def validate_saudi_phone(phone):
        """Validate Saudi phone number format"""
        if not phone:
            return False
        
        # Remove any non-digit characters and country code
        phone = re.sub(r'\D', '', phone)
        
        # Remove country code if present
        if phone.startswith('966'):
            phone = phone[3:]
        elif phone.startswith('00966'):
            phone = phone[5:]
        
        # Check if it's a valid Saudi mobile number
        if len(phone) == 9 and phone.startswith('5'):
            return True
        
        # Check if it's a valid Saudi landline number
        if len(phone) == 8 and phone[0] in ['1', '2', '3', '4', '6', '7']:
            return True
        
        return False
    
    @staticmethod
    def format_saudi_phone(phone):
        """Format Saudi phone number to standard format"""
        if not phone:
            return phone
        
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', phone)
        
        # Remove country code if present
        if phone.startswith('966'):
            phone = phone[3:]
        elif phone.startswith('00966'):
            phone = phone[5:]
        
        # Add country code
        if len(phone) in [8, 9]:
            return f"+966{phone}"
        
        return phone
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_iban(iban):
        """Validate IBAN format"""
        if not iban:
            return False
        
        # Remove spaces and convert to uppercase
        iban = re.sub(r'\s', '', iban.upper())
        
        # Check length (Saudi IBAN should be 24 characters)
        if len(iban) != 24:
            return False
        
        # Check if it starts with SA
        if not iban.startswith('SA'):
            return False
        
        # Move first 4 characters to end
        rearranged = iban[4:] + iban[:4]
        
        # Replace letters with numbers (A=10, B=11, ..., Z=35)
        numeric_string = ''
        for char in rearranged:
            if char.isalpha():
                numeric_string += str(ord(char) - ord('A') + 10)
            else:
                numeric_string += char
        
        # Check mod 97
        return int(numeric_string) % 97 == 1
    
    @staticmethod
    def generate_contract_number(prefix='EJAR'):
        """Generate unique contract number"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{prefix}-{timestamp}"
    
    @staticmethod
    def calculate_rental_duration(start_date, end_date):
        """Calculate rental duration in months"""
        if not start_date or not end_date:
            return 0
        
        if isinstance(start_date, str):
            start_date = fields.Date.from_string(start_date)
        if isinstance(end_date, str):
            end_date = fields.Date.from_string(end_date)
        
        delta = relativedelta(end_date, start_date)
        return delta.years * 12 + delta.months + (1 if delta.days > 0 else 0)
    
    @staticmethod
    def calculate_annual_rent(monthly_rent):
        """Calculate annual rent from monthly rent"""
        return monthly_rent * 12 if monthly_rent else 0
    
    @staticmethod
    def calculate_broker_commission(rent_amount, commission_rate=2.5):
        """Calculate broker commission"""
        return (rent_amount * commission_rate) / 100 if rent_amount else 0
    
    @staticmethod
    def calculate_late_fee(amount, days_late, late_fee_percentage=1.0):
        """Calculate late payment fee"""
        if not amount or days_late <= 0:
            return 0
        
        # Calculate daily rate
        daily_rate = late_fee_percentage / 100 / 30  # Monthly rate to daily
        return amount * daily_rate * days_late
    
    @staticmethod
    def get_hijri_date(gregorian_date=None):
        """Convert Gregorian date to Hijri (approximate)"""
        if not gregorian_date:
            gregorian_date = datetime.now().date()
        
        if isinstance(gregorian_date, str):
            gregorian_date = fields.Date.from_string(gregorian_date)
        
        # Approximate conversion (for display purposes only)
        # This is a simplified conversion and should be replaced with proper Hijri calendar library
        hijri_year = gregorian_date.year - 579
        hijri_month = gregorian_date.month
        hijri_day = gregorian_date.day
        
        return f"{hijri_day:02d}/{hijri_month:02d}/{hijri_year}"
    
    @staticmethod
    def format_currency(amount, currency='SAR'):
        """Format currency amount"""
        if not amount:
            return f"0.00 {currency}"
        
        return f"{amount:,.2f} {currency}"
    
    @staticmethod
    def parse_ejar_date(date_string):
        """Parse date string from Ejar API"""
        if not date_string:
            return None
        
        # Common date formats from Ejar API
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%d/%m/%Y',
            '%d-%m-%Y',
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_string, fmt)
                return parsed_date.date() if hasattr(parsed_date, 'date') else parsed_date
            except ValueError:
                continue
        
        _logger.warning(f"Could not parse date string: {date_string}")
        return None
    
    @staticmethod
    def format_ejar_date(date_obj):
        """Format date for Ejar API"""
        if not date_obj:
            return None
        
        if isinstance(date_obj, str):
            return date_obj
        
        return date_obj.strftime('%Y-%m-%d')
    
    @staticmethod
    def clean_arabic_text(text):
        """Clean Arabic text for API transmission"""
        if not text:
            return text
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\w\s\-\.\,\(\)]', '', text)
        
        return text
    
    @staticmethod
    def generate_reference_number(prefix='REF', length=8):
        """Generate reference number"""
        import random
        import string
        
        timestamp = datetime.now().strftime('%y%m%d')
        random_part = ''.join(random.choices(string.digits, k=length-6))
        
        return f"{prefix}{timestamp}{random_part}"
    
    @staticmethod
    def mask_sensitive_data(data, fields_to_mask=None):
        """Mask sensitive data for logging"""
        if not fields_to_mask:
            fields_to_mask = ['password', 'secret', 'key', 'token', 'national_id', 'iban']
        
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if any(field in key.lower() for field in fields_to_mask):
                    masked_data[key] = '*' * len(str(value)) if value else value
                elif isinstance(value, (dict, list)):
                    masked_data[key] = EjarHelpers.mask_sensitive_data(value, fields_to_mask)
                else:
                    masked_data[key] = value
            return masked_data
        elif isinstance(data, list):
            return [EjarHelpers.mask_sensitive_data(item, fields_to_mask) for item in data]
        else:
            return data
    
    @staticmethod
    def get_property_type_mapping():
        """Get property type mapping between Odoo and Ejar"""
        return {
            'apartment': 'apartment',
            'villa': 'villa',
            'office': 'commercial',
            'shop': 'commercial',
            'warehouse': 'commercial',
            'land': 'land',
            'building': 'building',
        }
    
    @staticmethod
    def get_contract_status_mapping():
        """Get contract status mapping between Odoo and Ejar"""
        return {
            'draft': 'draft',
            'active': 'active',
            'expired': 'expired',
            'terminated': 'terminated',
            'cancelled': 'cancelled',
        }
    
    @staticmethod
    def get_payment_method_mapping():
        """Get payment method mapping between Odoo and Ejar"""
        return {
            'cash': 'cash',
            'bank_transfer': 'bank_transfer',
            'check': 'check',
            'credit_card': 'credit_card',
            'online': 'online_payment',
        }
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validate required fields in data"""
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(_("Missing required fields: %s") % ', '.join(missing_fields))
        
        return True
    
    @staticmethod
    def safe_float(value, default=0.0):
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value, default=0):
        """Safely convert value to integer"""
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_bool(value, default=False):
        """Safely convert value to boolean"""
        if value is None:
            return default
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        
        return bool(value)
    
    @staticmethod
    def chunk_list(lst, chunk_size):
        """Split list into chunks of specified size"""
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]
    
    @staticmethod
    def retry_on_failure(func, max_retries=3, delay=1):
        """Retry function on failure with exponential backoff"""
        import time
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = delay * (2 ** attempt)
                _logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    @staticmethod
    def get_next_business_day(date_obj=None, days_ahead=1):
        """Get next business day (excluding Friday and Saturday in Saudi Arabia)"""
        if not date_obj:
            date_obj = datetime.now().date()
        
        if isinstance(date_obj, str):
            date_obj = fields.Date.from_string(date_obj)
        
        next_date = date_obj + timedelta(days=days_ahead)
        
        # In Saudi Arabia, weekend is Friday (4) and Saturday (5)
        while next_date.weekday() in [4, 5]:
            next_date += timedelta(days=1)
        
        return next_date
    
    @staticmethod
    def calculate_due_date(start_date, payment_frequency='monthly'):
        """Calculate next payment due date"""
        if not start_date:
            return None
        
        if isinstance(start_date, str):
            start_date = fields.Date.from_string(start_date)
        
        if payment_frequency == 'monthly':
            return start_date + relativedelta(months=1)
        elif payment_frequency == 'quarterly':
            return start_date + relativedelta(months=3)
        elif payment_frequency == 'semi_annual':
            return start_date + relativedelta(months=6)
        elif payment_frequency == 'annual':
            return start_date + relativedelta(years=1)
        else:
            return start_date + relativedelta(months=1)  # Default to monthly