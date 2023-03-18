# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from odoo import models, fields, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from dateutil.relativedelta import relativedelta


class RentalOrder(models.Model):
    _inherit = 'account.move'

    def action_view_renting_order(self):
        action = self.env.ref("sale_renting.rental_order_action").sudo().read()[0]
        sale_id = self.env['sale.order'].search([('name', '=', self.invoice_origin)])
        # action["domain"] = [("id", "in", [sale_id.id])]
        # action["target"] = 'new'
        # return action

        return {
            'name': _('Renting Order'),
            'view_mode': 'form',
            'view_id': self.env.ref('sale_renting.rental_order_primary_form_view').id,
            'res_model': 'sale.order',
            'create': False,
            'type': 'ir.actions.act_window',
            'res_id': sale_id.id,
        }