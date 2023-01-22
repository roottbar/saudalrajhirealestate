# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TenderLead(models.Model):
    _name = "tender.lead"
    _description = "Tender Leads"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Name", required=True, index=True, translate=True, copy=False, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Customer", index=True, copy=False, check_company=True,
                                 tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    crm_lead_id = fields.Many2one("crm.lead", string="Lead", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", string="Company", index=True, tracking=True,
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one("res.currency", "Currency", required=True, copy=False, tracking=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    manpower_lines = fields.One2many("tender.service.manpower", "tender_lead_id", string="Manpower Lines")
    amount_untaxed_manpower = fields.Monetary(string="Untaxed Amount", store=True, readonly=True,
                                              compute='_compute_amount_manpower')
    amount_discount_manpower = fields.Monetary(string="Amount Discount", store=True, readonly=True,
                                               compute='_compute_amount_manpower')
    amount_tax_manpower = fields.Monetary(string="Tax", store=True, readonly=True, compute='_compute_amount_manpower')
    amount_total_manpower = fields.Monetary(string="Total", store=True, readonly=True,
                                            compute='_compute_amount_manpower')

    equipments_lines = fields.One2many("tender.service.equipments", "tender_lead_id", string="Equipments Lines")
    amount_untaxed_equipments = fields.Monetary(string="Untaxed Amount", store=True, readonly=True,
                                                compute='_compute_amount_equipments')
    amount_discount_equipments = fields.Monetary(string="Amount Discount", store=True, readonly=True,
                                                 compute='_compute_amount_equipments')
    amount_tax_equipments = fields.Monetary(string="Tax", store=True, readonly=True,
                                            compute='_compute_amount_equipments')
    amount_total_equipments = fields.Monetary(string="Total", store=True, readonly=True,
                                              compute='_compute_amount_equipments')

    specialty_services_lines = fields.One2many("tender.specialty.services.request", "tender_lead_id",
                                               string="specialty services request Lines")
    amount_discount_specialty_services = fields.Monetary(string="Amount Discount", store=True, readonly=True,
                                                         compute='_compute_amount_specialty_services')
    amount_untaxed_specialty_services = fields.Monetary(string="Untaxed Amount", store=True, readonly=True,
                                                        compute='_compute_amount_specialty_services')
    amount_tax_specialty_services = fields.Monetary(string="Tax", store=True, readonly=True,
                                                    compute='_compute_amount_specialty_services')
    amount_total_specialty_services = fields.Monetary(string="Total", store=True, readonly=True,
                                                      compute='_compute_amount_specialty_services')
    amount_untaxed = fields.Float(string="Subtotal", compute="_compute_amount", store=True, readonly=True)
    amount_discount = fields.Float(string="Amount Discount", compute="_compute_amount", store=True, readonly=True)
    amount_tax = fields.Float(string="Amount Tax", compute="_compute_amount", store=True, readonly=True)
    amount_total = fields.Float(string="Total", compute="_compute_amount", store=True, readonly=True)
    notes = fields.Text(string="Notes", copy=False)
    tender_quotations_count = fields.Integer(compute="_compute_tender_quotations_count",
                                             string="Tender Quotations Count")

    @api.depends('manpower_lines.amount_untaxed', 'manpower_lines.amount_tax')
    def _compute_amount_manpower(self):
        for lead in self:
            amount_untaxed = 0
            amount_discount = 0
            amount_tax = 0
            amount_total = 0

            for line in lead.manpower_lines:
                amount_untaxed += line.amount_untaxed
                amount_discount += line.amount_discount
                amount_tax += line.amount_tax
                amount_total += line.amount_total

            lead.amount_untaxed_manpower = amount_untaxed
            lead.amount_discount_manpower = amount_discount
            lead.amount_tax_manpower = amount_tax
            lead.amount_total_manpower = amount_total

    @api.depends('equipments_lines.amount_untaxed', 'equipments_lines.amount_tax')
    def _compute_amount_equipments(self):
        for lead in self:
            amount_untaxed = 0
            amount_discount = 0
            amount_tax = 0
            amount_total = 0

            for line in lead.equipments_lines:
                amount_untaxed += line.amount_untaxed
                amount_discount += line.amount_discount
                amount_tax += line.amount_tax
                amount_total += line.amount_total

            lead.amount_untaxed_equipments = amount_untaxed
            lead.amount_discount_equipments = amount_discount
            lead.amount_tax_equipments = amount_tax
            lead.amount_total_equipments = amount_total

    @api.depends('specialty_services_lines.amount_untaxed', 'specialty_services_lines.amount_tax')
    def _compute_amount_specialty_services(self):
        for lead in self:
            amount_untaxed = 0
            amount_discount = 0
            amount_tax = 0
            amount_total = 0

            for line in lead.specialty_services_lines:
                amount_untaxed += line.amount_untaxed
                amount_discount += line.amount_discount
                amount_tax += line.amount_tax
                amount_total += line.amount_total

            lead.amount_untaxed_specialty_services = amount_untaxed
            lead.amount_discount_specialty_services = amount_discount
            lead.amount_tax_specialty_services = amount_tax
            lead.amount_total_specialty_services = amount_total

    @api.depends("amount_untaxed_manpower", "amount_discount_manpower", "amount_tax_manpower", "amount_total_manpower",
                 "amount_untaxed_equipments", "amount_discount_equipments", "amount_tax_equipments",
                 "amount_total_equipments", "amount_untaxed_specialty_services", "amount_discount_specialty_services",
                 "amount_tax_specialty_services", "amount_total_specialty_services")
    def _compute_amount(self):
        for lead in self:
            lead.amount_untaxed = lead.amount_untaxed_manpower + lead.amount_untaxed_equipments + lead.amount_untaxed_specialty_services
            lead.amount_discount = lead.amount_discount_manpower + lead.amount_discount_equipments + lead.amount_discount_specialty_services
            lead.amount_tax = lead.amount_tax_manpower + lead.amount_tax_equipments + lead.amount_tax_specialty_services
            lead.amount_total = lead.amount_total_manpower + lead.amount_total_equipments + lead.amount_total_specialty_services

    def _compute_tender_quotations_count(self):
        tender_quotation_obj = self.env["tender.quotation"].sudo()
        for lead in self:
            lead.tender_quotations_count = tender_quotation_obj.search_count([("tender_lead_id", "=", lead.id)])

    def unlink(self):
        for tender_lead in self:
            if tender_lead.crm_lead_id:
                raise UserError(_("You cannot delete tender lead %s related to Lead") % tender_lead.name)

        return super(TenderLead, self).unlink()

    def generate_crm_lead(self):
        # create crm lead
        crm_lead_obj = self.env["crm.lead"]
        for tender_lead in self:
            if tender_lead.crm_lead_id:
                continue

            vals = {
                "name": tender_lead.name,
                "partner_id": tender_lead.partner_id.id,
                "tender_lead_id": tender_lead.id
            }
            crm_lead_obj.create(vals)

        return True

    def get_crm_lead(self):
        form = self.env.ref("crm.crm_lead_view_form")

        return {
            "name": self.crm_lead_id.name,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            'view_id': form.id,
            "res_model": "crm.lead",
            "res_id": self.crm_lead_id.id,
        }

    def action_create_quotation(self):
        # create tender quotation
        if self.tender_quotations_count != 0:
            return

        # manpower lines
        manpower_lines = []
        for line in self.manpower_lines:
            manpower_lines.append([0, 0, line._prepare_line()])

        # equipments lines
        equipments_lines = []
        for line in self.equipments_lines:
            equipments_lines.append([0, 0, line._prepare_line()])

        # specialty services lines
        specialty_services_lines = []
        for line in self.specialty_services_lines:
            specialty_services_lines.append([0, 0, line._prepare_line()])

        context = self._context.copy()
        context.update({
            "default_tender_lead_id": self.id,
            "default_origin": self.name,
            "default_partner_id": self.partner_id.id,
            "default_company_id": self.company_id.id,
            "default_currency_id": self.currency_id.id,
            "default_manpower_lines": manpower_lines,
            "default_equipments_lines": equipments_lines,
            "default_specialty_services_lines": specialty_services_lines,
            "default_notes": self.notes,
        })

        form = self.env.ref("contracts_management.view_tender_quotation_form")
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            'view_id': form.id,
            "res_model": "tender.quotation",
            "context": context
        }

    def get_tender_quotation(self):
        # get tender quotation of lead
        tender_quotation = self.env["tender.quotation"].search([("tender_lead_id", "=", self.id)], limit=1)
        if not tender_quotation:
            return

        form = self.env.ref("contracts_management.view_tender_quotation_form")
        return {
            "name": tender_quotation.name,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            'view_id': form.id,
            "res_model": "tender.quotation",
            "res_id": tender_quotation.id,
        }
