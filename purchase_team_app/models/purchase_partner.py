# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResPartnerInherit(models.Model):
	_inherit = 'res.partner'

	team_id = fields.Many2one('purchase.team', string="Purchase Team")