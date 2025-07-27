# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    partner_id = fields.Many2one(
        comodel_name='res.partner', 
        string='Customer',
        help='Customer for this manufacturing order'
    )
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account', 
        string='Analytic Account'
    )
