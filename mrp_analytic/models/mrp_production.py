# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        domain="[('company_id', '=', company_id)]",
        help="Analytic account to which this production order is linked for analytical purposes."
    )
    
    partner_id = fields.Many2one(
        'res.partner', 
        string='Customer',
        compute='_compute_partner_id',
        store=True,
        help="Customer from the related sales order"
    )
    
    @api.depends('origin')
    def _compute_partner_id(self):
        for production in self:
            partner_id = False
            if production.origin:
                # البحث عن أمر البيع المرتبط
                sale_order = self.env['sale.order'].search([
                    ('name', '=', production.origin)
                ], limit=1)
                if sale_order:
                    partner_id = sale_order.partner_id.id
            production.partner_id = partner_id

    def _prepare_analytic_line_values(self, account_id, amount, unit_amount, description):
        return {
            'name': description,
            'amount': amount,
            'unit_amount': unit_amount,
            'account_id': account_id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'user_id': self.env.user.id,
            'date': fields.Date.today(),
            'company_id': self.company_id.id,
        }
