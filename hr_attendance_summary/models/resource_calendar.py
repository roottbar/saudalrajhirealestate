# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    late_rule_ids = fields.Many2many('late.rule', string='Late Rules')
