# -*- coding: utf-8 -*-

from odoo import models, api


class ReportInvoiceTenderContract(models.AbstractModel):
    _name = "report.contracts_management.report_invoice_tender_contract"

    @api.model
    def get_data_level1(self, filter_invoice_lines):
        cr = self.env.cr

        sql = """SELECT aml.parent_service_category_id,sc.name,SUM(aml.price_subtotal) AS price_subtotal, 
                 SUM(aml.price_total) AS price_total,SUM(aml.price_total - aml.price_subtotal) AS price_tax
                 FROM account_move_line AS aml, tender_service_category AS sc
                 WHERE %s AND aml.parent_service_category_id = sc.id
                 GROUP BY aml.parent_service_category_id,sc.name""" % filter_invoice_lines
        cr.execute(sql)
        result = cr.dictfetchall()

        return {"categories": result}

    @api.model
    def get_data_level3(self, filter_invoice_lines):
        data = []
        tender_branch_obj = self.env["tender.branch"]
        cr = self.env.cr
        cr.execute(
            "SELECT aml.branch_id FROM account_move_line AS aml where %s AND aml.branch_id IS NOT NULL GROUP BY aml.branch_id" % filter_invoice_lines)

        sql = """SELECT aml.name,aml.quantity,aml.parent_service_category_id 
                 FROM account_move_line AS aml WHERE %s""" % filter_invoice_lines

        for row in cr.dictfetchall():
            branch_id = row["branch_id"]
            cr.execute(sql + " AND aml.branch_id = %s" % branch_id)
            result = cr.dictfetchall()
            data.append({
                "branch_name": tender_branch_obj.browse(branch_id).name,
                "lines": result,
            })

        return data

    def sum_amount_discount(self, invoice_line_ids):
        amount_discount = 0
        for line in invoice_line_ids:
            amount_discount += line.price_unit * (line.discount or 0.0) / 100.0

        return amount_discount

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["account.move"].browse(docids).sudo()
        invoice_line_ids = docs[0].invoice_line_ids.filtered(lambda l: not l.display_type)

        filter_invoice_lines = 0
        if len(invoice_line_ids) != 0:
            filter_invoice_lines = len(invoice_line_ids) > 1 and "aml.id IN %s" % str(tuple(
                invoice_line_ids.ids)) or "aml.id = %s" % str(invoice_line_ids.id)

        # default service categories
        cleaning_service_category = self.env.ref('contracts_management.cleaning_tender_service_category')
        hospitality_service_category = self.env.ref('contracts_management.hospitality_tender_service_category')
        maintenance_service_category = self.env.ref('contracts_management.maintenance_tender_service_category')
        pest_control_service_category = self.env.ref('contracts_management.pest_control_tender_service_category')

        # default children categories
        cleaning_labour_cost_service_category = self.env.ref(
            'contracts_management.cleaning_labour_cost_tender_service_category')
        cleaning_materials_service_category = self.env.ref(
            'contracts_management.cleaning_materials_tender_service_category')
        hospitality_labour_cost_service_category = self.env.ref(
            'contracts_management.hospitality_labour_cost_tender_service_category')
        hospitality_materials_service_category = self.env.ref(
            'contracts_management.hospitality_materials_tender_service_category')
        maintenance_spare_parts_service_category = self.env.ref(
            'contracts_management.maintenance_spare_parts_tender_service_category')
        maintenance_service_charge_service_category = self.env.ref(
            'contracts_management.maintenance_service_charge_tender_service_category')
        pest_control_service_charge_service_category = self.env.ref(
            'contracts_management.pest_control_service_charge_tender_service_category')

        # data level 1
        data_level1 = self.get_data_level1(filter_invoice_lines)

        # data level 3
        data_level3 = self.get_data_level3(filter_invoice_lines)

        return {
            "doc_ids": docids,
            "doc_model": "account.move",
            "docs": docs,
            "data_level1": data_level1,
            "data_level3": data_level3,
            "amount_discount": self.sum_amount_discount(invoice_line_ids),
            "cleaning_service_category_id": cleaning_service_category.id,
            "hospitality_service_category_id": hospitality_service_category.id,
            "maintenance_service_category_id": maintenance_service_category.id,
            "pest_control_service_category_id": pest_control_service_category.id,
            "cleaning_labour_cost_service_category_id": cleaning_labour_cost_service_category.id,
            "cleaning_materials_service_category_id": cleaning_materials_service_category.id,
            "hospitality_labour_cost_service_category_id": hospitality_labour_cost_service_category.id,
            "hospitality_materials_service_category_id": hospitality_materials_service_category.id,
            "maintenance_spare_parts_service_category_id": maintenance_spare_parts_service_category.id,
            "maintenance_service_charge_service_category_id": maintenance_service_charge_service_category.id,
            "pest_control_service_charge_service_category_id": pest_control_service_charge_service_category.id
        }
