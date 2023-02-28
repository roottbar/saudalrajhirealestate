# -*- coding: utf-8 -*-

from odoo import models, fields, _


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    name = fields.Char('Department Name', required=True, translate=True)
