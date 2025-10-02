# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	team_id = fields.Many2one('purchase.team', string="Purchase Team")
