# -*- coding: utf-8 -*-

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
        if order.tender_contract_id:
            invoice_vals.update({
                "tender_contract_id": order.tender_contract_id.id
            })
        return invoice_vals
