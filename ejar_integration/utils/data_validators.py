# -*- coding: utf-8 -*-

import re
import logging
from datetime import datetime, date

from odoo import _, fields
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class EjarDataValidators:
    """Data validators for Ejar integration"""

    @staticmethod
    def validate_property_data(property_data):
        """Validate property data before sending to Ejar"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'property_type', 'area', 'monthly_rent', 'address', 'city']
        for field in required_fields:
            if not property_data.get(field):
                errors.append(_("Property %s is required") % field)
        
        # Validate property type
        valid_types = ['apartment', 'villa', 'office', 'shop', 'warehouse', 'land', 'building']
        if property_data.get('property_type') and property_data['property_type'] not in valid_types:
            errors.append(_("Invalid property type: %s") % property_data['property_type'])
        
        # Validate numeric fields
        numeric_fields = ['area', 'built_area', 'monthly_rent', 'security_deposit', 'broker_commission_rate']
        for field in numeric_fields:
            value = property_data.get(field)
            if value is not None:
                try:
                    float_value = float(value)
                    if float_value < 0:
                        errors.append(_("Property %s must be positive") % field)
                except (ValueError, TypeError):
                    errors.append(_("Property %s must be a valid number") % field)
        
        # Validate integer fields
        integer_fields = ['bedrooms', 'bathrooms', 'parking_spaces', 'floor_number', 'total_floors', 'construction_year']
        for field in integer_fields:
            value = property_data.get(field)
            if value is not None:
                try:
                    int_value = int(value)
                    if int_value < 0:
                        errors.append(_("Property %s must be positive") % field)
                except (ValueError, TypeError):
                    errors.append(_("Property %s must be a valid integer") % field)
        
        # Validate construction year
        if property_data.get('construction_year'):
            current_year = datetime.now().year
            construction_year = int(property_data['construction_year'])
            if construction_year < 1900 or construction_year > current_year + 5:
                errors.append(_("Invalid construction year: %s") % construction_year)
        
        # Validate coordinates
        if property_data.get('latitude'):
            try:
                lat = float(property_data['latitude'])
                if not (-90 <= lat <= 90):
                    errors.append(_("Latitude must be between -90 and 90"))
            except (ValueError, TypeError):
                errors.append(_("Invalid latitude format"))
        
        if property_data.get('longitude'):
            try:
                lng = float(property_data['longitude'])
                if not (-180 <= lng <= 180):
                    errors.append(_("Longitude must be between -180 and 180"))
            except (ValueError, TypeError):
                errors.append(_("Invalid longitude format"))
        
        # Validate status
        valid_statuses = ['available', 'rented', 'maintenance', 'unavailable']
        if property_data.get('status') and property_data['status'] not in valid_statuses:
            errors.append(_("Invalid property status: %s") % property_data['status'])
        
        # Validate furnishing status
        valid_furnishing = ['furnished', 'semi_furnished', 'unfurnished']
        if property_data.get('furnishing_status') and property_data['furnishing_status'] not in valid_furnishing:
            errors.append(_("Invalid furnishing status: %s") % property_data['furnishing_status'])
        
        # Validate property condition
        valid_conditions = ['excellent', 'very_good', 'good', 'fair', 'poor']
        if property_data.get('property_condition') and property_data['property_condition'] not in valid_conditions:
            errors.append(_("Invalid property condition: %s") % property_data['property_condition'])
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return True
    
    @staticmethod
    def validate_contract_data(contract_data):
        """Validate contract data before sending to Ejar"""
        errors = []
        
        # Required fields
        required_fields = ['property_id', 'tenant_id', 'landlord_id', 'start_date', 'end_date', 'monthly_rent']
        for field in required_fields:
            if not contract_data.get(field):
                errors.append(_("Contract %s is required") % field)
        
        # Validate dates
        if contract_data.get('start_date') and contract_data.get('end_date'):
            start_date = contract_data['start_date']
            end_date = contract_data['end_date']
            
            if isinstance(start_date, str):
                start_date = fields.Date.from_string(start_date)
            if isinstance(end_date, str):
                end_date = fields.Date.from_string(end_date)
            
            if start_date >= end_date:
                errors.append(_("Contract end date must be after start date"))
            
            # Check if contract duration is reasonable (minimum 1 month, maximum 10 years)
            duration_days = (end_date - start_date).days
            if duration_days < 30:
                errors.append(_("Contract duration must be at least 1 month"))
            elif duration_days > 3650:  # 10 years
                errors.append(_("Contract duration cannot exceed 10 years"))
        
        # Validate numeric fields
        numeric_fields = ['monthly_rent', 'annual_rent', 'security_deposit', 'broker_commission', 'late_fee_percentage']
        for field in numeric_fields:
            value = contract_data.get(field)
            if value is not None:
                try:
                    float_value = float(value)
                    if float_value < 0:
                        errors.append(_("Contract %s must be positive") % field)
                except (ValueError, TypeError):
                    errors.append(_("Contract %s must be a valid number") % field)
        
        # Validate integer fields
        integer_fields = ['duration_months', 'advance_payment_months', 'renewal_notice_days']
        for field in integer_fields:
            value = contract_data.get(field)
            if value is not None:
                try:
                    int_value = int(value)
                    if int_value < 0:
                        errors.append(_("Contract %s must be positive") % field)
                except (ValueError, TypeError):
                    errors.append(_("Contract %s must be a valid integer") % field)
        
        # Validate payment frequency
        valid_frequencies = ['monthly', 'quarterly', 'semi_annual', 'annual']
        if contract_data.get('payment_frequency') and contract_data['payment_frequency'] not in valid_frequencies:
            errors.append(_("Invalid payment frequency: %s") % contract_data['payment_frequency'])
        
        # Validate status
        valid_statuses = ['draft', 'active', 'expired', 'terminated', 'cancelled']
        if contract_data.get('status') and contract_data['status'] not in valid_statuses:
            errors.append(_("Invalid contract status: %s") % contract_data['status'])
        
        # Validate late fee percentage (should be reasonable)
        if contract_data.get('late_fee_percentage'):
            late_fee = float(contract_data['late_fee_percentage'])
            if late_fee > 10:  # More than 10% seems unreasonable
                errors.append(_("Late fee percentage seems too high: %s%%") % late_fee)
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return True
    
    @staticmethod
    def validate_tenant_data(tenant_data):
        """Validate tenant data before sending to Ejar"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'national_id', 'phone', 'email']
        for field in required_fields:
            if not tenant_data.get(field):
                errors.append(_("Tenant %s is required") % field)
        
        # Validate national ID
        if tenant_data.get('national_id'):
            from .ejar_helpers import EjarHelpers
            if not EjarHelpers.validate_saudi_national_id(tenant_data['national_id']):
                errors.append(_("Invalid Saudi National ID: %s") % tenant_data['national_id'])
        
        # Validate phone
        if tenant_data.get('phone'):
            from .ejar_helpers import EjarHelpers
            if not EjarHelpers.validate_saudi_phone(tenant_data['phone']):
                errors.append(_("Invalid Saudi phone number: %s") % tenant_data['phone'])
        
        # Validate email
        if tenant_data.get('email'):
            from .ejar_helpers import EjarHelpers
            if not EjarHelpers.validate_email(tenant_data['email']):
                errors.append(_("Invalid email format: %s") % tenant_data['email'])
        
        # Validate IBAN if provided
        if tenant_data.get('iban'):
            from .ejar_helpers import EjarHelpers
            if not EjarHelpers.validate_iban(tenant_data['iban']):
                errors.append(_("Invalid IBAN: %s") % tenant_data['iban'])
        
        # Validate birth date
        if tenant_data.get('birth_date'):
            birth_date = tenant_data['birth_date']
            if isinstance(birth_date, str):
                try:
                    birth_date = fields.Date.from_string(birth_date)
                except ValueError:
                    errors.append(_("Invalid birth date format"))
            
            if isinstance(birth_date, date):
                today = fields.Date.today()
                age = (today - birth_date).days / 365.25
                if age < 18:
                    errors.append(_("Tenant must be at least 18 years old"))
                elif age > 120:
                    errors.append(_("Invalid birth date - age cannot exceed 120 years"))
        
        # Validate gender
        if tenant_data.get('gender') and tenant_data['gender'] not in ['male', 'female']:
            errors.append(_("Invalid gender: %s") % tenant_data['gender'])
        
        # Validate marital status
        valid_marital_statuses = ['single', 'married', 'divorced', 'widowed']
        if tenant_data.get('marital_status') and tenant_data['marital_status'] not in valid_marital_statuses:
            errors.append(_("Invalid marital status: %s") % tenant_data['marital_status'])
        
        # Validate employment status
        valid_employment_statuses = ['employed', 'self_employed', 'unemployed', 'retired', 'student']
        if tenant_data.get('employment_status') and tenant_data['employment_status'] not in valid_employment_statuses:
            errors.append(_("Invalid employment status: %s") % tenant_data['employment_status'])
        
        # Validate monthly income
        if tenant_data.get('monthly_income'):
            try:
                income = float(tenant_data['monthly_income'])
                if income < 0:
                    errors.append(_("Monthly income must be positive"))
            except (ValueError, TypeError):
                errors.append(_("Invalid monthly income format"))
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return True
    
    @staticmethod
    def validate_landlord_data(landlord_data):
        """Validate landlord data before sending to Ejar"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'national_id', 'phone', 'email']
        for field in required_fields:
            if not landlord_data.get(field):
                errors.append(_("Landlord %s is required") % field)
        
        # Validate national ID
        if landlord_data.get('national_id'):
            from .ejar_helpers import EjarHelpers
            if not EjarHelpers.validate_saudi_national_id(landlord_data['national_id']):
                errors.append(_("Invalid Saudi National ID: %s") % landlord_data['national_id'])
        
        # Validate phone
        if landlord_data.get('phone'):
            from .ejar_helpers import EjarHelpers
            if not EjarHelpers.validate_saudi_phone(landlord_data['phone']):
                errors.append(_("Invalid Saudi phone number: %s") % landlord_data['phone'])
        
        # Validate email
        if landlord_data.get('email'):
            from .ejar_helpers import EjarHelpers
            if not EjarHelpers.validate_email(landlord_data['email']):
                errors.append(_("Invalid email format: %s") % landlord_data['email'])
        
        # Validate IBAN if provided
        if landlord_data.get('iban'):
            from .ejar_helpers import EjarHelpers
            if not EjarHelpers.validate_iban(landlord_data['iban']):
                errors.append(_("Invalid IBAN: %s") % landlord_data['iban'])
        
        # Validate commercial registration if provided
        if landlord_data.get('commercial_registration'):
            cr_number = landlord_data['commercial_registration']
            if not re.match(r'^\d{10}$', cr_number):
                errors.append(_("Commercial registration must be 10 digits"))
        
        # Validate tax number if provided
        if landlord_data.get('tax_number'):
            tax_number = landlord_data['tax_number']
            if not re.match(r'^\d{15}$', tax_number):
                errors.append(_("Tax number must be 15 digits"))
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return True
    
    @staticmethod
    def validate_broker_data(broker_data):
        """Validate broker data before sending to Ejar"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'license_number', 'phone', 'email']
        for field in required_fields:
            if not broker_data.get(field):
                errors.append(_("Broker %s is required") % field)
        
        # Validate license number
        if broker_data.get('license_number'):
            license_number = broker_data['license_number']
            if not re.match(r'^[A-Z0-9]{8,20}$', license_number):
                errors.append(_("Invalid broker license number format"))
        
        # Validate phone
        if broker_data.get('phone'):
            from .ejar_helpers import EjarHelpers
            if not EjarHelpers.validate_saudi_phone(broker_data['phone']):
                errors.append(_("Invalid Saudi phone number: %s") % broker_data['phone'])
        
        # Validate email
        if broker_data.get('email'):
            from .ejar_helpers import EjarHelpers
            if not EjarHelpers.validate_email(broker_data['email']):
                errors.append(_("Invalid email format: %s") % broker_data['email'])
        
        # Validate commission rate
        if broker_data.get('commission_rate'):
            try:
                commission = float(broker_data['commission_rate'])
                if commission < 0 or commission > 10:
                    errors.append(_("Broker commission rate must be between 0% and 10%"))
            except (ValueError, TypeError):
                errors.append(_("Invalid commission rate format"))
        
        # Validate license expiry date
        if broker_data.get('license_expiry_date'):
            expiry_date = broker_data['license_expiry_date']
            if isinstance(expiry_date, str):
                try:
                    expiry_date = fields.Date.from_string(expiry_date)
                except ValueError:
                    errors.append(_("Invalid license expiry date format"))
            
            if isinstance(expiry_date, date):
                if expiry_date <= fields.Date.today():
                    errors.append(_("Broker license has expired"))
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return True
    
    @staticmethod
    def validate_payment_data(payment_data):
        """Validate payment data before sending to Ejar"""
        errors = []
        
        # Required fields
        required_fields = ['contract_id', 'amount', 'payment_date', 'payment_method']
        for field in required_fields:
            if not payment_data.get(field):
                errors.append(_("Payment %s is required") % field)
        
        # Validate amount
        if payment_data.get('amount'):
            try:
                amount = float(payment_data['amount'])
                if amount <= 0:
                    errors.append(_("Payment amount must be positive"))
            except (ValueError, TypeError):
                errors.append(_("Invalid payment amount format"))
        
        # Validate payment date
        if payment_data.get('payment_date'):
            payment_date = payment_data['payment_date']
            if isinstance(payment_date, str):
                try:
                    payment_date = fields.Date.from_string(payment_date)
                except ValueError:
                    errors.append(_("Invalid payment date format"))
            
            if isinstance(payment_date, date):
                # Payment date should not be too far in the future
                max_future_date = fields.Date.today() + timedelta(days=30)
                if payment_date > max_future_date:
                    errors.append(_("Payment date cannot be more than 30 days in the future"))
        
        # Validate payment method
        valid_methods = ['cash', 'bank_transfer', 'check', 'credit_card', 'online_payment']
        if payment_data.get('payment_method') and payment_data['payment_method'] not in valid_methods:
            errors.append(_("Invalid payment method: %s") % payment_data['payment_method'])
        
        # Validate reference number if provided
        if payment_data.get('reference'):
            reference = payment_data['reference']
            if len(reference) > 50:
                errors.append(_("Payment reference number is too long"))
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return True
    
    @staticmethod
    def validate_notification_data(notification_data):
        """Validate notification data before sending to Ejar"""
        errors = []
        
        # Required fields
        required_fields = ['title', 'message', 'notification_type']
        for field in required_fields:
            if not notification_data.get(field):
                errors.append(_("Notification %s is required") % field)
        
        # Validate notification type
        valid_types = ['contract', 'payment', 'property', 'compliance', 'general']
        if notification_data.get('notification_type') and notification_data['notification_type'] not in valid_types:
            errors.append(_("Invalid notification type: %s") % notification_data['notification_type'])
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if notification_data.get('priority') and notification_data['priority'] not in valid_priorities:
            errors.append(_("Invalid notification priority: %s") % notification_data['priority'])
        
        # Validate delivery methods
        if notification_data.get('delivery_methods'):
            valid_methods = ['email', 'sms', 'push', 'system']
            delivery_methods = notification_data['delivery_methods']
            if isinstance(delivery_methods, str):
                delivery_methods = [delivery_methods]
            
            for method in delivery_methods:
                if method not in valid_methods:
                    errors.append(_("Invalid delivery method: %s") % method)
        
        # Validate scheduled date
        if notification_data.get('scheduled_date'):
            scheduled_date = notification_data['scheduled_date']
            if isinstance(scheduled_date, str):
                try:
                    scheduled_date = fields.Datetime.from_string(scheduled_date)
                except ValueError:
                    errors.append(_("Invalid scheduled date format"))
            
            if isinstance(scheduled_date, datetime):
                if scheduled_date <= fields.Datetime.now():
                    errors.append(_("Scheduled date must be in the future"))
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return True
    
    @staticmethod
    def validate_document_data(document_data):
        """Validate document data before sending to Ejar"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'document_type']
        for field in required_fields:
            if not document_data.get(field):
                errors.append(_("Document %s is required") % field)
        
        # Validate document type
        valid_types = ['contract', 'identity', 'property_deed', 'insurance', 'other']
        if document_data.get('document_type') and document_data['document_type'] not in valid_types:
            errors.append(_("Invalid document type: %s") % document_data['document_type'])
        
        # Validate file size if provided
        if document_data.get('file_size'):
            try:
                file_size = int(document_data['file_size'])
                max_size = 10 * 1024 * 1024  # 10 MB
                if file_size > max_size:
                    errors.append(_("File size exceeds maximum limit of 10 MB"))
            except (ValueError, TypeError):
                errors.append(_("Invalid file size format"))
        
        # Validate MIME type if provided
        if document_data.get('mime_type'):
            valid_mime_types = [
                'application/pdf',
                'image/jpeg',
                'image/png',
                'image/gif',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            if document_data['mime_type'] not in valid_mime_types:
                errors.append(_("Unsupported file type: %s") % document_data['mime_type'])
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return True