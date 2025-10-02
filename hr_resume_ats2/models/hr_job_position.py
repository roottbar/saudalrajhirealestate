# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrJobPosition(models.Model):
    _name = 'hr.job.position'
    _description = 'Job Position for Resume Analysis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Basic Information
    name = fields.Char('Job Title', required=True, tracking=True)
    code = fields.Char('Job Code', tracking=True)
    description = fields.Html('Job Description', tracking=True)
    department_id = fields.Many2one('hr.department', 'Department', tracking=True)
    
    # Requirements
    required_skills = fields.Text('Required Skills (comma separated)', 
                                help="Enter skills separated by commas, e.g., Python, SQL, Project Management",
                                tracking=True)
    preferred_skills = fields.Text('Preferred Skills (comma separated)',
                                 help="Enter preferred skills separated by commas",
                                 tracking=True)
    
    required_experience_years = fields.Float('Required Experience (Years)', tracking=True)
    preferred_experience_years = fields.Float('Preferred Experience (Years)', tracking=True)
    
    required_education_level = fields.Selection([
        ('high_school', 'High School'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor Degree'),
        ('master', 'Master Degree'),
        ('phd', 'PhD')
    ], 'Required Education Level', tracking=True)
    
    preferred_education_level = fields.Selection([
        ('high_school', 'High School'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor Degree'),
        ('master', 'Master Degree'),
        ('phd', 'PhD')
    ], 'Preferred Education Level', tracking=True)
    
    # Keywords for ATS optimization
    keywords = fields.Text('Important Keywords (comma separated)',
                         help="Keywords that should appear in resume for better ATS scoring",
                         tracking=True)
    
    # Job Details
    employment_type = fields.Selection([
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance')
    ], 'Employment Type', default='full_time', tracking=True)
    
    location = fields.Char('Job Location', tracking=True)
    remote_work = fields.Boolean('Remote Work Available', tracking=True)
    
    # Salary Information
    salary_min = fields.Float('Minimum Salary', tracking=True)
    salary_max = fields.Float('Maximum Salary', tracking=True)
    currency_id = fields.Many2one('res.currency', 'Currency', 
                                default=lambda self: self.env.company.currency_id)
    
    # Status
    active = fields.Boolean('Active', default=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed')
    ], 'Status', default='draft', tracking=True)
    
    # Statistics
    resume_analysis_count = fields.Integer('Resume Analyses', compute='_compute_resume_analysis_count')
    average_score = fields.Float('Average Resume Score', compute='_compute_average_score')
    
    # Relations
    resume_analysis_ids = fields.One2many('hr.resume.analysis', 'job_position_id', 'Resume Analyses')
    
    # Company
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    
    @api.depends('resume_analysis_ids')
    def _compute_resume_analysis_count(self):
        for record in self:
            record.resume_analysis_count = len(record.resume_analysis_ids)
    
    @api.depends('resume_analysis_ids.overall_score')
    def _compute_average_score(self):
        for record in self:
            completed_analyses = record.resume_analysis_ids.filtered(lambda x: x.state == 'completed')
            if completed_analyses:
                record.average_score = sum(completed_analyses.mapped('overall_score')) / len(completed_analyses)
            else:
                record.average_score = 0.0
    
    @api.constrains('salary_min', 'salary_max')
    def _check_salary_range(self):
        for record in self:
            if record.salary_min and record.salary_max and record.salary_min > record.salary_max:
                raise ValidationError(_("Minimum salary cannot be greater than maximum salary."))
    
    @api.constrains('required_experience_years', 'preferred_experience_years')
    def _check_experience_years(self):
        for record in self:
            if (record.required_experience_years and record.preferred_experience_years and 
                record.required_experience_years > record.preferred_experience_years):
                raise ValidationError(_("Required experience cannot be greater than preferred experience."))
    
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            if record.department_id:
                name = f"{name} - {record.department_id.name}"
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Search in name, code, and department
            domain = ['|', '|', 
                     ('name', operator, name),
                     ('code', operator, name),
                     ('department_id.name', operator, name)]
            return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return super(HrJobPosition, self)._name_search(name, args, operator, limit, name_get_uid)
    
    def action_publish(self):
        """Publish job position"""
        self.state = 'published'
        self.message_post(body=_("Job position has been published."))
    
    def action_close(self):
        """Close job position"""
        self.state = 'closed'
        self.message_post(body=_("Job position has been closed."))
    
    def action_reset_to_draft(self):
        """Reset to draft state"""
        self.state = 'draft'
        self.message_post(body=_("Job position has been reset to draft."))
    
    def action_view_resume_analyses(self):
        """View all resume analyses for this job position"""
        return {
            'name': _('Resume Analyses'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.resume.analysis',
            'view_mode': 'tree,form',
            'domain': [('job_position_id', '=', self.id)],
            'context': {
                'default_job_position_id': self.id,
                'search_default_job_position_id': self.id,
            },
        }
    
    def get_skills_list(self):
        """Get list of required skills"""
        if self.required_skills:
            return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]
        return []
    
    def get_keywords_list(self):
        """Get list of important keywords"""
        if self.keywords:
            return [keyword.strip() for keyword in self.keywords.split(',') if keyword.strip()]
        return []
    
    def get_job_requirements_summary(self):
        """Get formatted summary of job requirements"""
        summary = []
        
        if self.required_experience_years:
            summary.append(f"Experience: {self.required_experience_years} years")
        
        if self.required_education_level:
            education_dict = dict(self._fields['required_education_level'].selection)
            summary.append(f"Education: {education_dict.get(self.required_education_level)}")
        
        if self.required_skills:
            skills = self.get_skills_list()
            if len(skills) <= 3:
                summary.append(f"Skills: {', '.join(skills)}")
            else:
                summary.append(f"Skills: {', '.join(skills[:3])} and {len(skills)-3} more")
        
        return ' | '.join(summary) if summary else 'No specific requirements defined'
    
    @api.model
    def create_sample_positions(self):
        """Create sample job positions for demo purposes"""
        sample_positions = [
            {
                'name': 'Software Developer',
                'code': 'SD001',
                'description': '<p>We are looking for a skilled Software Developer to join our team.</p>',
                'required_skills': 'Python, JavaScript, SQL, Git, REST APIs',
                'preferred_skills': 'React, Django, PostgreSQL, Docker',
                'required_experience_years': 2.0,
                'preferred_experience_years': 4.0,
                'required_education_level': 'bachelor',
                'keywords': 'software development, programming, coding, web development, backend, frontend',
                'employment_type': 'full_time',
                'location': 'Remote',
                'remote_work': True,
                'state': 'published'
            },
            {
                'name': 'Data Analyst',
                'code': 'DA001',
                'description': '<p>Join our data team as a Data Analyst to help drive business decisions.</p>',
                'required_skills': 'SQL, Excel, Python, Statistics, Data Visualization',
                'preferred_skills': 'Tableau, Power BI, R, Machine Learning',
                'required_experience_years': 1.0,
                'preferred_experience_years': 3.0,
                'required_education_level': 'bachelor',
                'keywords': 'data analysis, statistics, reporting, business intelligence, analytics',
                'employment_type': 'full_time',
                'location': 'New York',
                'remote_work': False,
                'state': 'published'
            },
            {
                'name': 'Project Manager',
                'code': 'PM001',
                'description': '<p>Experienced Project Manager needed to lead cross-functional teams.</p>',
                'required_skills': 'Project Management, Leadership, Communication, Risk Management',
                'preferred_skills': 'PMP Certification, Agile, Scrum, JIRA, MS Project',
                'required_experience_years': 5.0,
                'preferred_experience_years': 8.0,
                'required_education_level': 'bachelor',
                'preferred_education_level': 'master',
                'keywords': 'project management, leadership, planning, coordination, delivery',
                'employment_type': 'full_time',
                'location': 'San Francisco',
                'remote_work': True,
                'state': 'published'
            }
        ]
        
        for position_data in sample_positions:
            existing = self.search([('code', '=', position_data['code'])], limit=1)
            if not existing:
                self.create(position_data)
        
        return True