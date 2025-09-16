# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # OpenAI Settings
    openai_api_key = fields.Char(
        string='OpenAI API Key',
        config_parameter='hr_resume_ats.openai_api_key',
        help='Your OpenAI API key for AI-powered resume analysis'
    )
    openai_model = fields.Selection([
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ('gpt-4', 'GPT-4'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
    ], string='OpenAI Model',
        config_parameter='hr_resume_ats.openai_model',
        default='gpt-3.5-turbo',
        help='Choose the OpenAI model for resume analysis'
    )
    openai_max_tokens = fields.Integer(
        string='Max Tokens',
        config_parameter='hr_resume_ats.openai_max_tokens',
        default=2000,
        help='Maximum number of tokens for OpenAI responses'
    )
    openai_temperature = fields.Float(
        string='Temperature',
        config_parameter='hr_resume_ats.openai_temperature',
        default=0.3,
        help='Controls randomness in AI responses (0.0 to 1.0)'
    )
    
    # Analysis Settings
    enable_ai_analysis = fields.Boolean(
        string='Enable AI Analysis',
        config_parameter='hr_resume_ats.enable_ai_analysis',
        default=True,
        help='Enable AI-powered resume analysis'
    )
    auto_extract_info = fields.Boolean(
        string='Auto Extract Basic Info',
        config_parameter='hr_resume_ats.auto_extract_info',
        default=True,
        help='Automatically extract candidate information from resume'
    )
    detailed_skill_analysis = fields.Boolean(
        string='Detailed Skill Analysis',
        config_parameter='hr_resume_ats.detailed_skill_analysis',
        default=True,
        help='Perform detailed analysis of candidate skills'
    )
    experience_relevance_check = fields.Boolean(
        string='Experience Relevance Check',
        config_parameter='hr_resume_ats.experience_relevance_check',
        default=True,
        help='Check relevance of candidate experience to job position'
    )
    education_verification = fields.Boolean(
        string='Education Verification',
        config_parameter='hr_resume_ats.education_verification',
        default=False,
        help='Enable education verification (requires additional setup)'
    )
    
    # Scoring Settings
    ats_weight = fields.Float(
        string='ATS Score Weight (%)',
        config_parameter='hr_resume_ats.ats_weight',
        default=25.0,
        help='Weight of ATS compatibility score in overall score'
    )
    skills_weight = fields.Float(
        string='Skills Score Weight (%)',
        config_parameter='hr_resume_ats.skills_weight',
        default=35.0,
        help='Weight of skills match score in overall score'
    )
    experience_weight = fields.Float(
        string='Experience Score Weight (%)',
        config_parameter='hr_resume_ats.experience_weight',
        default=25.0,
        help='Weight of experience score in overall score'
    )
    education_weight = fields.Float(
        string='Education Score Weight (%)',
        config_parameter='hr_resume_ats.education_weight',
        default=15.0,
        help='Weight of education score in overall score'
    )
    
    # Notification Settings
    notify_on_analysis_complete = fields.Boolean(
        string='Notify on Analysis Complete',
        config_parameter='hr_resume_ats.notify_on_analysis_complete',
        default=True,
        help='Send notification when resume analysis is completed'
    )
    notify_hr_managers = fields.Boolean(
        string='Notify HR Managers',
        config_parameter='hr_resume_ats.notify_hr_managers',
        default=False,
        help='Notify HR managers of new resume analyses'
    )
    
    # File Processing Settings
    max_file_size_mb = fields.Integer(
        string='Max File Size (MB)',
        config_parameter='hr_resume_ats.max_file_size_mb',
        default=10,
        help='Maximum allowed resume file size in MB'
    )
    allowed_file_types = fields.Char(
        string='Allowed File Types',
        config_parameter='hr_resume_ats.allowed_file_types',
        default='pdf,doc,docx',
        help='Comma-separated list of allowed file extensions'
    )
    
    # Language Settings
    analysis_language = fields.Selection([
        ('en', 'English'),
        ('ar', 'Arabic'),
        ('fr', 'French'),
        ('es', 'Spanish'),
        ('de', 'German'),
    ], string='Analysis Language',
        config_parameter='hr_resume_ats.analysis_language',
        default='en',
        help='Language for AI analysis and reports'
    )
    
    @api.constrains('ats_weight', 'skills_weight', 'experience_weight', 'education_weight')
    def _check_weights_total(self):
        """Ensure that all weights sum to 100%"""
        for record in self:
            total_weight = record.ats_weight + record.skills_weight + record.experience_weight + record.education_weight
            if abs(total_weight - 100.0) > 0.1:  # Allow small floating point differences
                raise ValidationError(
                    'The sum of all score weights must equal 100%. '
                    f'Current total: {total_weight}%'
                )
    
    @api.constrains('openai_temperature')
    def _check_temperature_range(self):
        """Ensure temperature is within valid range"""
        for record in self:
            if not (0.0 <= record.openai_temperature <= 1.0):
                raise ValidationError(
                    'Temperature must be between 0.0 and 1.0'
                )
    
    @api.constrains('openai_max_tokens')
    def _check_max_tokens(self):
        """Ensure max tokens is reasonable"""
        for record in self:
            if record.openai_max_tokens < 100 or record.openai_max_tokens > 8000:
                raise ValidationError(
                    'Max tokens must be between 100 and 8000'
                )
    
    @api.constrains('max_file_size_mb')
    def _check_file_size(self):
        """Ensure file size limit is reasonable"""
        for record in self:
            if record.max_file_size_mb < 1 or record.max_file_size_mb > 50:
                raise ValidationError(
                    'Max file size must be between 1 and 50 MB'
                )
    
    def action_test_openai_connection(self):
        """Test OpenAI API connection"""
        try:
            # Import here to avoid dependency issues if not installed
            import openai
            
            if not self.openai_api_key:
                raise UserError('Please configure OpenAI API key first')
            
            openai.api_key = self.openai_api_key
            
            # Test with a simple completion
            response = openai.ChatCompletion.create(
                model=self.openai_model or 'gpt-3.5-turbo',
                messages=[
                    {"role": "user", "content": "Test connection. Reply with 'OK'"}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            if response and response.choices:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success!',
                        'message': 'OpenAI connection test successful',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError('Invalid response from OpenAI API')
                
        except ImportError:
            raise UserError(
                'OpenAI library not installed. Please install it using: '
                'pip install openai'
            )
        except Exception as e:
            raise UserError(f'OpenAI connection failed: {str(e)}')
    
    def action_reset_weights_to_default(self):
        """Reset scoring weights to default values"""
        self.write({
            'ats_weight': 25.0,
            'skills_weight': 35.0,
            'experience_weight': 25.0,
            'education_weight': 15.0,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Reset Complete',
                'message': 'Scoring weights have been reset to default values',
                'type': 'info',
                'sticky': False,
            }
        }