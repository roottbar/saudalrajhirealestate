# -*- coding: utf-8 -*-
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    tender_contract_id = fields.Many2one("tender.contract", string="Contract", domain=[("state", "=", "in progress")],
                                         copy=False)
    apply_assign_analytic = fields.Boolean("Apply Assign Analytic", copy=False)

    def button_validate(self):
        # check there tender contracts or not

        if "check_assign_analytic_account" not in self._context.keys() and self.tender_contract_id and not self.apply_assign_analytic:
            product_categories = self.move_ids_without_package.mapped("product_id.categ_id").filtered(
                lambda c: c.property_valuation == "real_time")
            if product_categories:
                action = self.sudo().env.ref("contracts_management.action_tender_contract_validate_stock_picking",
                                             False)
                result = action.read()[0]
                return result

        return super(StockPicking, self).button_validate()


class StockMove(models.Model):
    _inherit = "stock.move"

    tender_contract_id = fields.Many2one(related="picking_id.tender_contract_id", string="Contract", store=True,
                                         readonly=True)

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id,
                                       credit_account_id, description):
        aml_vals = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value,
                                                                         debit_account_id, credit_account_id,
                                                                         description)

        if self.picking_id.apply_assign_analytic:
            # account types that allow to append analytic account and tags in journal items
            account_type_ids = [self.env.ref('account.data_account_type_expenses').id,
                                self.env.ref('account.data_account_type_direct_costs').id,
                                self.env.ref('account.data_account_type_revenue').id,
                                self.env.ref('account.data_account_type_other_income').id]

            account_ids = []
            product_template = self.product_id.product_tmpl_id
            stock_account_input_id = self.location_id.valuation_out_account_id and self.location_id.valuation_out_account_id or product_template.categ_id.property_stock_account_input_categ_id

            if stock_account_input_id.user_type_id.id in account_type_ids:
                account_ids.append(stock_account_input_id.id)

            stock_account_output_id = self.location_id.valuation_in_account_id and self.location_id.valuation_in_account_id or product_template.categ_id.property_stock_account_output_categ_id
            if stock_account_output_id.user_type_id.id in account_type_ids:
                account_ids.append(stock_account_output_id.id)

            if account_ids:
                analytic_account_id = self.tender_contract_id.analytic_account_id.id
                analytic_tag_ids = [(6, 0, self.tender_contract_id.analytic_tag_ids.ids)]
                if aml_vals["credit_line_vals"]["account_id"] in account_ids:
                    aml_vals["credit_line_vals"]["analytic_account_id"] = analytic_account_id
                    aml_vals["credit_line_vals"]["analytic_tag_ids"] = analytic_tag_ids

                if aml_vals["debit_line_vals"]["account_id"] in account_ids:
                    aml_vals["debit_line_vals"]["analytic_account_id"] = analytic_account_id
                    aml_vals["debit_line_vals"]["analytic_tag_ids"] = analytic_tag_ids

        return aml_vals
