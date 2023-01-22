#!/usr/bin/python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HRTravel(models.Model):
    _name = "hr.travel"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "الرحلات"
    _order = 'from_country'
    _rec_name = 'from_country'

    from_country = fields.Many2one('res.country', string='من', copy=False, tracking=True, required=True)
    to_country = fields.Many2one('res.country', string='الي', copy=False, tracking=True, required=True)
    value = fields.Float(string='القيمة', copy=False, tracking=True, required=True)
