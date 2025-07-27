# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.depends('production_ids')
    def _compute_production_count(self):
        for project in self:
            project.production_count = len(project.production_ids)

    production_ids = fields.One2many(
        'mrp.production', 'project_id', string='Manufacturing Orders')
    production_count = fields.Integer(
        string='Manufacturing Count', compute='_compute_production_count')
    automatic_creation = fields.Boolean('Automatic Creation')