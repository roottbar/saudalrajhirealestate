# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('review', 'Reviewed'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    def action_review(self):
        self.state = 'review'

    def _auto_create_asset(self):
        create_list = []
        invoice_list = []
        auto_validate = []
        for move in self:
            if not move.is_invoice():
                continue

            for move_line in move.line_ids.filtered(lambda line: not (move.move_type in ('out_invoice', 'out_refund') and line.account_id.user_type_id.internal_group == 'asset')):
                if (
                    move_line.account_id
                    and (move_line.account_id.can_create_asset)
                    and move_line.account_id.create_asset != "no"
                    and not move.reversed_entry_id
                    and not (move_line.currency_id or move.currency_id).is_zero(move_line.price_total)
                    and not move_line.asset_ids
                    and not move_line.tax_line_id
                    and move_line.price_total > 0
                ):
                    if not move_line.name:
                        raise UserError(_('Journal Items of {account} should have a label in order to generate an asset').format(account=move_line.account_id.display_name))
                    if move_line.account_id.multiple_assets_per_line:
                        # decimal quantities are not supported, quantities are rounded to the lower int
                        units_quantity = max(1, int(move_line.quantity))
                    else:
                        units_quantity = 1
                    vals = {
                        'name': move_line.name,
                        'company_id': move_line.company_id.id,
                        'currency_id': move_line.company_currency_id.id,
                        'account_analytic_id': move_line.analytic_account_id.id,
                        'analytic_tag_ids': [(6, False, move_line.analytic_tag_ids.ids)],
                        'original_move_line_ids': [(6, False, move_line.ids)],
                        'state': 'draft',
                    }
                    model_id = move_line.account_id.asset_model
                    if model_id:
                        vals.update({
                            'model_id': model_id.id,
                        })
                    auto_validate.extend([move_line.account_id.create_asset == 'validate'] * units_quantity)
                    invoice_list.extend([move] * units_quantity)
                    for i in range(1, units_quantity + 1):
                        if units_quantity > 1:
                            vals['name'] = move_line.name + _(" (%s of %s)", i, units_quantity)
                        create_list.extend([vals.copy()])

        assets = self.env['account.asset'].create(create_list)
        for asset, vals, invoice, validate in zip(assets, create_list, invoice_list, auto_validate):
            if 'model_id' in vals:
                asset._onchange_model_id()
                if validate:
                    asset.validate()
            if invoice:
                asset_name = {
                    'purchase': _('Asset'),
                    'sale': _('Deferred revenue'),
                    'expense': _('Deferred expense'),
                }[asset.asset_type]
                msg = _('%s created from invoice') % (asset_name)
                msg += ': <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>' % (invoice.id, invoice.name)
                asset.message_post(body=msg)
                #Abdulrhman Change
                asset.set_to_draft()
                asset.prorata_date = self.invoice_date
                asset.compute_depreciation_board()
                # asset.validate()
        return assets


    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            for line in rec.asset_ids:
                if rec.rent_sale_line_id:
                    if rec.rent_sale_line_id.sale_order_id.invoice_number:
                        # model_id = self.env['account.asset'].search([('asset_type', '=', 'sale'), ('state', '=', 'model'),('method_number', '=', rec.rent_sale_line_id.sale_order_id.invoice_number )])
                        for line in rec.asset_ids:
                            line.set_to_draft()
                            # line.model_id = model_id.id
                            # line._onchange_model_id()
                            date1 = datetime.strptime(str(rec.rent_sale_line_id.sale_order_id.fromdate)[:10], '%Y-%m-%d')
                            date2 = datetime.strptime(str(rec.rent_sale_line_id.sale_order_id.todate)[:10], '%Y-%m-%d')
                            difference = relativedelta(date2, date1)
                            months = difference.months + 12 * difference.years
                            if difference.days > 0:
                                months += 1

                            line.method_number = months / rec.rent_sale_line_id.sale_order_id.invoice_number
                            line.compute_depreciation_board()
                            line.validate()
                else:
                    for dep in line.depreciation_move_ids:
                        dep.button_draft()
                        dep.unlink()
                        line.set_to_running()
                        line.set_to_draft()
                        line.compute_depreciation_board()
                        line.validate()



        return res