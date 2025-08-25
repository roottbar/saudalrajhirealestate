# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from odoo import models, fields, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from dateutil.relativedelta import relativedelta

from hijri_converter import Gregorian, convert

class RentalOrder(models.TransientModel):
    _inherit = 'rental.order.wizard'

    def apply(self):
        res = super(RentalOrder, self).apply()
        for rec in self:
            if rec.status == 'return':
                rec.order_id.state = 'termination'
                for line in rec.order_id.order_line:
                    line.product_id.unit_rented = False
                rec.order_id.rental_status = 'returned'
            if rec.status == 'pickup':
                rec.order_id.state = 'occupied'
                for line in rec.order_id.order_line:
                    line.product_id.unit_rented = True
                rec.order_id.rental_status = 'pickup'
        return res


class RentLog(models.Model):
    _name = "rent.log"
    order_id = fields.Many2one('sale.order')
    rent_id = fields.Many2one('sale.order')
    fromdate = fields.Date('From Date')
    todate = fields.Date('To Date')
    amount = fields.Float('Amount')

class SaleOrder(models.Model):
    _inherit = "sale.order"
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Acceptance'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('occupied', 'Occupied'),
        ('termination', 'Termination'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    apartment_insurance = fields.Float('Apartment Insurance')
    refund_insurance = fields.Boolean('Refund Insurance')
    damage_amount = fields.Float('Damage Amount')
    refund_amount = fields.Float('Refund Amount')
    context_order = fields.Many2one('sale.order')
    old_rent_ids = fields.One2many(comodel_name='rent.log', inverse_name='order_id', string='Old Rents')


    transfer_context_order = fields.Many2one('sale.order')
    new_rental_id = fields.Many2one('sale.order', copy=False)
    transfer_customer_id = fields.Many2one('res.partner', 'Customer To Transfer')
    transfer_date = fields.Date('Transfer Date')
    transferred = fields.Boolean('Transferred ?')
    annual_increase = fields.Boolean('Annual Increase ?')
    annual_amount = fields.Float("Annual Amount")


    def get_date_hijri(self, date):
        day = date.day
        month = date.month
        year = date.year
        hijri_date = Gregorian(year, month, day).to_hijri()
        war_start = '2011-01-03'
        war = datetime.strptime(war_start, '%Y-%m-%d')
        war1 = convert.Gregorian.fromdate(war).to_hijri()
        return hijri_date

    def renew_contract(self):
        new_contract_id = self.copy()
        fmt = '%Y-%m-%d'
        start_date = self.fromdate
        end_date = self.todate
        d1 = datetime.strptime(str(start_date)[:10], fmt)
        d2 = datetime.strptime(str(end_date)[:10], fmt)
        date_difference = d2 - d1
        new_contract_id.fromdate = self.todate
        new_contract_id.todate = new_contract_id.fromdate +   relativedelta(days=date_difference.days)
        new_contract_id.invoice_number = self.invoice_number
        new_contract_id.is_rental_order = self.is_rental_order
        new_contract_id.partner_id = self.partner_id
        lines = []
        for line in self.order_line:
            line = self.env['sale.order.line'].create({
                'order_id': new_contract_id.id,
                'property_number': line.property_number.id,
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit if self.annual_increase != True else ((line.price_unit * self.annual_amount/100) + line.price_unit),
                'tax_id': [(6,0, line.tax_id.ids)],
                'insurance_value': line.insurance_value,
                'is_rental': line.is_rental,
                'contract_admin_fees': line.contract_admin_fees,
                'contract_service_fees': line.contract_admin_sub_fees,
                'contract_admin_sub_fees': line.contract_service_sub_fees,
            })
            lines.append(line.id)
        new_contract_id.order_line = [(6, 0, lines)]
        form_view_id = self.env.ref('sale_renting.rental_order_primary_form_view').ids
        for rent in self.old_rent_ids:
            self.env['rent.log'].create({
                'order_id' : new_contract_id.id,
                'rent_id' : rent.rent_id.id,
                'fromdate' : rent.fromdate,
                'todate' : rent.todate,
                'amount' : rent.amount,
            })
        self.env['rent.log'].create({
            'order_id': new_contract_id.id,
            'rent_id': self.id,
            'fromdate': self.fromdate,
            'todate': self.todate,
            'amount': self.amount_total,
        })
        return {
                'type': 'ir.actions.act_window',
                'name': 'Renew Contract',
                'target': 'current',
                'res_model': 'sale.order',
                'res_id': new_contract_id.id,
                'view_id': form_view_id,
                'view_type': 'form',
                'views':[(form_view_id, 'form')],
            }

    @api.onchange('damage_amount', 'apartment_insurance')
    def change_damage_amount(self):
        self.refund_amount = self.apartment_insurance - self.damage_amount
        
    def action_termination(self):
        self.write({
            "rental_status": "returned",
            "state": "termination",
        })

    def action_refund_insurance(self):
        action = self.env.ref("rent_customize.refund_insurance_action").read()[0]
        self.context_order = self.id
        self.apartment_insurance = self.apartment_insurance
        self.refund_amount = self.apartment_insurance
        self.state = self.state
        self.partner_invoice_id = self.partner_invoice_id.id
        self.partner_id = self.partner_id.id
        action["res_id"] = self.id
        return action

    def action_view_transfer(self):
        return {
            'name': _('Renting Order'),
            'view_mode': 'form',
            'view_id': self.env.ref('sale_renting.rental_order_primary_form_view').id,
            'res_model': 'sale.order',
            'create': False,
            'type': 'ir.actions.act_window',
            'res_id': self.new_rental_id.id,
        }

    def action_transfer(self):
        for rec in self:
            uninvoiced = len(rec.order_contract_invoice.filtered(lambda ll: ll.status == 'uninvoiced').ids)
            if uninvoiced <1:
                raise ValidationError(_("There is no draft invoice to be invoiced or transferred"))
            form_view_id = self.env.ref('rent_customize.transfer_view_form').ids
            return {
                'name': 'Transfer Apartment',
                'views': [(form_view_id, 'form')],
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': self.id,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    def do_transfer(self):
        for rec in self:
            uninvoiced = len(rec.order_contract_invoice.filtered(lambda ll: ll.status == 'uninvoiced').ids)
            new_rental_id = rec.copy({
                'pricelist_id' : rec.pricelist_id.id,
                'apartment_insurance' : rec.pricelist_id.id,
                'fromdate' : rec.transfer_date,
                'todate' : rec.todate,
                'date_order' : fields.Date.today(),
                'invoice_number' : uninvoiced if uninvoiced > 0 else rec.invoice_number,
                'is_rental_order' : True,
                'new_rental_id' : False,
            })
            rec.new_rental_id = new_rental_id.id
            rec.transferred = True

    def do_transfer_and_print(self):
        for rec in self:
            rec.do_transfer()
            rec.print_transfer()
            
    def _prepare_refund_invoice_line(self):
        self.ensure_one()
        product_tmp_id = self.env['ir.config_parameter'].sudo().get_param('renting.insurance_value')
        product_id = self.env['product.product'].search([
            ('product_tmpl_id', '=', int(product_tmp_id))
        ])
        res = {
            'display_type': False,
            'name': product_id.name,
            'product_id': product_id.id,
            'product_uom_id': product_id.uom_id.id,
            'quantity': 1,
            'discount': 0,
            'price_unit': abs(self.refund_amount),
            'tax_ids': [(6, 0, [])],
            'sale_line_ids': [(4, self.context_order.order_line[0].id)],
            'analytic_account_id': False,
            'exclude_from_invoice_tab': False,
        }
        return res
