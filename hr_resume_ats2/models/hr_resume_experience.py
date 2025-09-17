# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

class HrResumeExperience(models.Model):
    _name = 'hr.resume.experience'
    _description = 'Resume Experience Analysis'
    _order = 'start_date desc'

    resume_analysis_id = fields.Many2one('hr.resume.analysis', 'Resume Analysis', required=True, ondelete='cascade')
    
    # Experience details
    job_title = fields.Char('Job Title')
    company_name = fields.Char('Company Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    is_current = fields.Boolean('Current Position', default=False)
    
    # Duration calculation
    duration_months = fields.Float('Duration (Months)', compute='_compute_duration', store=True)
    duration_years = fields.Float('Duration (Years)', compute='_compute_duration', store=True)
    
    # Experience analysis
    job_description = fields.Text('Job Description')
    responsibilities = fields.Text('Key Responsibilities')
    achievements = fields.Text('Achievements')
    
    # Relevance scoring
    relevance_score = fields.Float('Relevance Score (%)', default=0.0,
                                 help="How relevant this experience is to the target job")
    
    # Skills and technologies used
    technologies_used = fields.Text('Technologies/Tools Used')
    skills_demonstrated = fields.Text('Skills Demonstrated')
    
    # Industry and role matching
    industry = fields.Char('Industry')
    role_level = fields.Selection([
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead/Principal'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('executive', 'Executive')
    ], 'Role Level')
    
    # Analysis flags
    is_relevant = fields.Boolean('Relevant Experience', default=False)
    has_leadership = fields.Boolean('Leadership Experience', default=False)
    has_team_management = fields.Boolean('Team Management', default=False)
    
    @api.depends('start_date', 'end_date', 'is_current')
    def _compute_duration(self):
        for record in self:
            if record.start_date:
                end_date = record.end_date if not record.is_current else fields.Date.today()
                if end_date:
                    delta = end_date - record.start_date
                    record.duration_months = delta.days / 30.44  # Average days per month
                    record.duration_years = record.duration_months / 12
                else:
                    record.duration_months = 0
                    record.duration_years = 0
            else:
                record.duration_months = 0
                record.duration_years = 0
    
    @api.onchange('end_date', 'is_current')
    def _onchange_current_position(self):
        if self.is_current:
            self.end_date = False
    
    def name_get(self):
        result = []
        for record in self:
            name_parts = []
            if record.job_title:
                name_parts.append(record.job_title)
            if record.company_name:
                name_parts.append(f"at {record.company_name}")
            if record.duration_years:
                name_parts.append(f"({record.duration_years:.1f} years)")
            
            name = ' '.join(name_parts) if name_parts else f"Experience #{record.id}"
            result.append((record.id, name))
        return result
    
    def analyze_experience_relevance(self, target_job_position):
        """Analyze how relevant this experience is to the target job"""
        if not target_job_position:
            return 0
        
        score = 0
        max_score = 100
        
        # Job title similarity (30 points)
        if self.job_title and target_job_position.name:
            title_words = set(self.job_title.lower().split())
            target_words = set(target_job_position.name.lower().split())
            common_words = title_words.intersection(target_words)
            if common_words:
                score += min(30, len(common_words) * 10)
        
        # Skills match (40 points)
        if self.skills_demonstrated and target_job_position.required_skills:
            experience_skills = set(skill.strip().lower() for skill in self.skills_demonstrated.split(','))
            required_skills = set(skill.strip().lower() for skill in target_job_position.required_skills.split(','))
            matching_skills = experience_skills.intersection(required_skills)
            if required_skills:
                skills_match_ratio = len(matching_skills) / len(required_skills)
                score += skills_match_ratio * 40
        
        # Experience level (20 points)
        if self.duration_years >= (target_job_position.required_experience_years or 0):
            score += 20
        elif self.duration_years >= (target_job_position.required_experience_years or 0) * 0.5:
            score += 10
        
        # Industry relevance (10 points)
        if self.industry and target_job_position.department_id:
            # This is a simplified check - in real implementation, you might have industry mapping
            score += 10
        
        self.relevance_score = min(max_score, score)
        self.is_relevant = self.relevance_score >= 50
        
        return self.relevance_score