# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrResumeSkill(models.Model):
    _name = 'hr.resume.skill'
    _description = 'Resume Skill Analysis'
    _order = 'relevance_score desc, skill_name'

    resume_analysis_id = fields.Many2one('hr.resume.analysis', 'Resume Analysis', required=True, ondelete='cascade')
    skill_name = fields.Char('Skill Name', required=True)
    is_found = fields.Boolean('Found in Resume', default=False)
    relevance_score = fields.Float('Relevance Score (%)', default=0.0)
    skill_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ], 'Detected Skill Level')
    
    # Skill categorization
    skill_category = fields.Selection([
        ('technical', 'Technical'),
        ('soft', 'Soft Skills'),
        ('language', 'Language'),
        ('certification', 'Certification'),
        ('tool', 'Tool/Software'),
        ('other', 'Other')
    ], 'Skill Category', default='technical')
    
    # Analysis details
    mentions_count = fields.Integer('Mentions in Resume', default=0)
    context_snippets = fields.Text('Context Snippets')
    importance_weight = fields.Float('Importance Weight', default=1.0,
                                   help="Weight of this skill for the job position")
    
    # Computed fields
    weighted_score = fields.Float('Weighted Score', compute='_compute_weighted_score', store=True)
    
    @api.depends('relevance_score', 'importance_weight')
    def _compute_weighted_score(self):
        for record in self:
            record.weighted_score = record.relevance_score * record.importance_weight
    
    def name_get(self):
        result = []
        for record in self:
            name = record.skill_name
            if record.is_found:
                name += f" ✓ ({record.relevance_score:.0f}%)"
            else:
                name += " ✗ (Missing)"
            result.append((record.id, name))
        return result