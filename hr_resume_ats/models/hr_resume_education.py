# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrResumeEducation(models.Model):
    _name = 'hr.resume.education'
    _description = 'Resume Education Analysis'
    _order = 'graduation_year desc, education_level desc'

    resume_analysis_id = fields.Many2one('hr.resume.analysis', 'Resume Analysis', required=True, ondelete='cascade')
    
    # Education details
    degree_name = fields.Char('Degree/Certificate Name')
    field_of_study = fields.Char('Field of Study/Major')
    institution_name = fields.Char('Institution Name')
    location = fields.Char('Location')
    
    # Dates
    start_year = fields.Integer('Start Year')
    graduation_year = fields.Integer('Graduation Year')
    is_ongoing = fields.Boolean('Currently Studying', default=False)
    
    # Education level
    education_level = fields.Selection([
        ('high_school', 'High School'),
        ('diploma', 'Diploma/Certificate'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor Degree'),
        ('master', 'Master Degree'),
        ('phd', 'PhD/Doctorate'),
        ('professional', 'Professional Certification'),
        ('other', 'Other')
    ], 'Education Level', required=True)
    
    # Academic performance
    gpa = fields.Float('GPA/Grade')
    gpa_scale = fields.Char('GPA Scale', default='4.0')
    honors = fields.Char('Honors/Awards')
    
    # Relevance analysis
    relevance_score = fields.Float('Relevance Score (%)', default=0.0)
    is_relevant = fields.Boolean('Relevant to Job', default=False)
    
    # Additional details
    coursework = fields.Text('Relevant Coursework')
    projects = fields.Text('Academic Projects')
    thesis_topic = fields.Char('Thesis/Dissertation Topic')
    
    # Verification status
    is_verified = fields.Boolean('Verified', default=False)
    verification_notes = fields.Text('Verification Notes')
    
    @api.onchange('graduation_year', 'is_ongoing')
    def _onchange_ongoing_education(self):
        if self.is_ongoing:
            self.graduation_year = False
    
    def name_get(self):
        result = []
        for record in self:
            name_parts = []
            
            if record.degree_name:
                name_parts.append(record.degree_name)
            elif record.education_level:
                level_dict = dict(record._fields['education_level'].selection)
                name_parts.append(level_dict.get(record.education_level, record.education_level))
            
            if record.field_of_study:
                name_parts.append(f"in {record.field_of_study}")
            
            if record.institution_name:
                name_parts.append(f"from {record.institution_name}")
            
            if record.graduation_year:
                name_parts.append(f"({record.graduation_year})")
            elif record.is_ongoing:
                name_parts.append("(Ongoing)")
            
            name = ' '.join(name_parts) if name_parts else f"Education #{record.id}"
            result.append((record.id, name))
        return result
    
    def analyze_education_relevance(self, target_job_position):
        """Analyze how relevant this education is to the target job"""
        if not target_job_position:
            return 0
        
        score = 0
        max_score = 100
        
        # Education level match (40 points)
        if target_job_position.required_education_level:
            education_hierarchy = {
                'high_school': 1,
                'diploma': 2,
                'associate': 3,
                'bachelor': 4,
                'master': 5,
                'phd': 6,
                'professional': 3,  # Equivalent to associate for scoring
                'other': 2
            }
            
            required_level = education_hierarchy.get(target_job_position.required_education_level, 0)
            candidate_level = education_hierarchy.get(self.education_level, 0)
            
            if candidate_level >= required_level:
                score += 40
            elif candidate_level >= required_level - 1:
                score += 25  # Close match
            elif candidate_level >= required_level - 2:
                score += 10  # Partial match
        else:
            # If no specific requirement, give points for having education
            score += 30
        
        # Field of study relevance (30 points)
        if self.field_of_study and target_job_position.name:
            # Simple keyword matching - in real implementation, you might use more sophisticated matching
            study_keywords = set(self.field_of_study.lower().split())
            job_keywords = set(target_job_position.name.lower().split())
            
            # Check for direct field matches
            relevant_fields = {
                'computer', 'software', 'information', 'technology', 'engineering',
                'business', 'management', 'marketing', 'finance', 'accounting',
                'science', 'mathematics', 'statistics', 'data', 'analytics'
            }
            
            field_matches = study_keywords.intersection(job_keywords)
            relevant_matches = study_keywords.intersection(relevant_fields)
            
            if field_matches:
                score += 30
            elif relevant_matches:
                score += 20
            else:
                score += 10  # General education value
        
        # Academic performance (15 points)
        if self.gpa:
            try:
                gpa_value = float(self.gpa)
                if '4.0' in (self.gpa_scale or '4.0'):
                    if gpa_value >= 3.5:
                        score += 15
                    elif gpa_value >= 3.0:
                        score += 10
                    elif gpa_value >= 2.5:
                        score += 5
                elif '100' in (self.gpa_scale or '100'):
                    if gpa_value >= 85:
                        score += 15
                    elif gpa_value >= 75:
                        score += 10
                    elif gpa_value >= 65:
                        score += 5
            except (ValueError, TypeError):
                pass
        
        # Honors and awards (10 points)
        if self.honors:
            score += 10
        
        # Recent graduation bonus (5 points)
        if self.graduation_year:
            current_year = fields.Date.today().year
            years_since_graduation = current_year - self.graduation_year
            if years_since_graduation <= 5:
                score += 5
        elif self.is_ongoing:
            score += 5  # Currently studying
        
        self.relevance_score = min(max_score, score)
        self.is_relevant = self.relevance_score >= 60
        
        return self.relevance_score
    
    def get_education_summary(self):
        """Get a formatted summary of this education record"""
        summary_parts = []
        
        if self.degree_name:
            summary_parts.append(self.degree_name)
        
        if self.field_of_study:
            summary_parts.append(f"Major: {self.field_of_study}")
        
        if self.institution_name:
            summary_parts.append(f"Institution: {self.institution_name}")
        
        if self.gpa:
            gpa_text = f"GPA: {self.gpa}"
            if self.gpa_scale:
                gpa_text += f"/{self.gpa_scale}"
            summary_parts.append(gpa_text)
        
        if self.graduation_year:
            summary_parts.append(f"Graduated: {self.graduation_year}")
        elif self.is_ongoing:
            summary_parts.append("Status: Ongoing")
        
        if self.honors:
            summary_parts.append(f"Honors: {self.honors}")
        
        return ' | '.join(summary_parts)