# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Lead(models.Model):
    _inherit = "crm.lead"

    tender_lead_id = fields.Many2one("tender.lead", string="Lead",
                                     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('crm_lead_id','=',False)]",
                                     check_company=True, copy=False)

    @api.constrains("tender_lead_id")
    def _check_tender_lead(self):
        if self.tender_lead_id:
            exists_lead = self.sudo().search([("id", "!=", self.id), ("tender_lead_id", "=", self.tender_lead_id.id)])
            if exists_lead:
                raise ValidationError(_("Lead must be unique, this one is already assigned to another lead."))

    @api.model
    def create(self, vals):
        res = super(Lead, self).create(vals)
        if vals.get("tender_lead_id", False):
            tender_lead = self.env["tender.lead"].sudo().browse(vals.get("tender_lead_id"))
            tender_lead.write({"crm_lead_id": res.id})
        return res

    def write(self, vals):
        if "tender_lead_id" in vals.keys():
            tender_lead_id = vals.get("tender_lead_id", False)

            # remove old tender lead
            if self.tender_lead_id:
                self.tender_lead_id.write({"crm_lead_id": False})

            # new tender lead
            if tender_lead_id:
                self.env["tender.lead"].sudo().browse(tender_lead_id).write({"crm_lead_id": self.id})

        res = super(Lead, self).write(vals)
        return res

    def generate_tender_lead(self):
        # create tender lead
        tender_lead_obj = self.env["tender.lead"]
        for crm_lead in self:
            if crm_lead.tender_lead_id:
                continue

            vals = {
                "name": crm_lead.name,
                "partner_id": crm_lead.partner_id.id
            }
            tender_lead = tender_lead_obj.create(vals)
            crm_lead.write({"tender_lead_id": tender_lead.id})

        return True

    def get_tender_lead(self):
        form = self.env.ref("contracts_management.view_tender_lead_form")

        return {
            "name": self.tender_lead_id.name,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            'view_id': form.id,
            "res_model": "tender.lead",
            "res_id": self.tender_lead_id.id,
        }
