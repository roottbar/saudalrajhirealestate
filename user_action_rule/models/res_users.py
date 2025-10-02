# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    action_rule_id = fields.Many2one('user.action.rule', string='Action Rule', copy=False)
