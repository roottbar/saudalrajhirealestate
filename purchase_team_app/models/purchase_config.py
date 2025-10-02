# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	purchase_team = fields.Boolean(string="Purchase Team", group='base.group_user', implied_group='purchase_team_app.group_purchase_team')

	@api.model
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		pur_sudo = self.env['ir.config_parameter'].sudo()
		purchase_team = pur_sudo.get_param('purchase_team_app.purchase_team')
		res.update(
			purchase_team = purchase_team,
			)
		return res

	def set_values(self):
		super(ResConfigSettings, self).set_values()
		purchase_sudo = self.env['ir.config_parameter'].sudo()
		purchase_sudo.set_param('purchase_team_app.purchase_team',self.purchase_team)