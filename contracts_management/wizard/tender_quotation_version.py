# -*- coding: utf-8 -*-

from odoo import fields, models


class TenderQuotationVersionWizard(models.TransientModel):
    _name = "tender.quotation.version.wizard"
    _description = "Tender Quotation Version"

    services = fields.Selection([
        ("with_services", "With"),
        ("without_services", "Without")], required=True, string="Services", default="with_services")

    def _prepare_quotation(self, quotation):
        version_number = quotation.version + 1
        vals = {
            "name": quotation.name,
            "parent_quotation_id": quotation.id,
            "origin": quotation.origin,
            "date": quotation.date,
            "expiration_date": quotation.expiration_date,
            "version": version_number,
            "version_number": " - %s" % version_number,
            "customer_reference": quotation.customer_reference,
            "partner_id": quotation.partner_id.id,
            "partner_invoice_id": quotation.partner_invoice_id.id,
            "partner_shipping_id": quotation.partner_shipping_id.id,
            "company_id": quotation.company_id.id,
            "currency_id": quotation.currency_id.id,
            "pricelist_id": quotation.pricelist_id.id,
            "payment_term_id": quotation.payment_term_id.id,
            "user_id": quotation.user_id.id,
            "team_id": quotation.team_id.id,
            "require_signature": quotation.require_signature,
            "require_payment": quotation.require_payment,
            "fiscal_position_id": quotation.fiscal_position_id.id,
            "analytic_account_id": quotation.analytic_account_id.id,
            "commitment_date": quotation.commitment_date,
            "campaign_id": quotation.campaign_id.id,
            "medium_id": quotation.medium_id.id,
            "source_id": quotation.source_id.id,
            "signature": quotation.signature,
            "signed_by": quotation.signed_by,
            "signed_on": quotation.signed_on,
            "incoterm": quotation.incoterm.id,
            "picking_policy": quotation.picking_policy,
            "warehouse_id": quotation.warehouse_id.id,
            "terms_conditions_id": quotation.terms_conditions_id.id,
            "terms_and_conditions": quotation.terms_and_conditions
        }

        if self.services == "with_services":
            # manpower lines
            manpower_lines = []
            for line in quotation.manpower_lines:
                manpower_lines.append([0, 0, line._prepare_line()])

            # equipments lines
            equipments_lines = []
            for line in quotation.equipments_lines:
                equipments_lines.append([0, 0, line._prepare_line()])

            # specialty services lines
            specialty_services_lines = []
            for line in quotation.specialty_services_lines:
                specialty_services_lines.append([0, 0, line._prepare_line()])

            vals.update({
                "manpower_lines": manpower_lines,
                "equipments_lines": equipments_lines,
                "specialty_services_lines": specialty_services_lines
            })
        return vals

    def action_new_version(self):
        tender_quotation_obj = self.env["tender.quotation"]
        quotation = tender_quotation_obj.search([("id", "=", self._context["active_id"])])

        if quotation.state != "in progress":
            return

        tender_quotation_obj.create(self._prepare_quotation(quotation))
        return quotation.write({"state": "cancel", "has_version": True})
