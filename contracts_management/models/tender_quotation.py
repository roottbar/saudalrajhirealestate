# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TenderQuotationTermCondition(models.Model):
    _name = "tender.quotation.term.condition"
    _description = "Tender Quotation Terms & Conditions"

    name = fields.Char("Name", required=True, index=True, translate=True, copy=False)
    code = fields.Char("Code", copy=False)
    description = fields.Text(string="Description", translate=True, required=True, copy=False)


class TenderQuotation(models.Model):
    _name = "tender.quotation"
    _description = "Tender Quotations"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _rec_name = "complete_number"
    _order = "date desc, id desc"

    @api.model
    def _get_default_team(self):
        return self.env["crm.team"]._get_default_team_id()

    def _get_default_require_signature(self):
        return self.env.company.portal_confirmation_sign

    def _get_default_require_payment(self):
        return self.env.company.portal_confirmation_pay

    @api.model
    def _default_warehouse_id(self):
        return self.env["stock.warehouse"].search([("company_id", "=", self.env.company.id)], limit=1)

    name = fields.Char("Number", readonly=True, index=True, copy=False, tracking=True, default="/")
    complete_number = fields.Char("Complete Name", compute="_compute_complete_number", store=True, readonly=True)
    origin = fields.Char(string='Source Document', tracking=True, copy=False)
    date = fields.Datetime("Date", default=fields.Datetime.now, required=True, tracking=True, index=True, copy=False)
    expiration_date = fields.Date(string="Expiration", tracking=True, copy=False)
    state = fields.Selection([
        ("draft", "Draft"),
        ("in progress", "In Progress"),
        ("done", "Contract"),
        ("cancel", "Cancelled")], string="Status", index=True, readonly=True, default="draft", copy=False,
        tracking=True)
    version = fields.Integer(string="Version", default=0, copy=False)
    parent_quotation_id = fields.Many2one("tender.quotation", string="Parent Quotation", copy=False)
    version_number = fields.Char("Version Number", readonly=True, copy=False)
    has_version = fields.Boolean("Has Version", copy=False)

    manpower_lines = fields.One2many("tender.service.manpower", "tender_quotation_id", string="Manpower Lines")
    amount_untaxed_manpower = fields.Monetary(string="Untaxed Amount", store=True, readonly=True,
                                              compute='_compute_amount_manpower')
    amount_discount_manpower = fields.Monetary(string="Amount Discount", store=True, readonly=True,
                                               compute='_compute_amount_manpower')
    amount_tax_manpower = fields.Monetary(string="Tax", store=True, readonly=True, compute='_compute_amount_manpower')
    amount_total_manpower = fields.Monetary(string="Total", store=True, readonly=True,
                                            compute='_compute_amount_manpower')

    equipments_lines = fields.One2many("tender.service.equipments", "tender_quotation_id", string="Equipments Lines")
    amount_untaxed_equipments = fields.Monetary(string="Untaxed Amount", store=True, readonly=True,
                                                compute='_compute_amount_equipments')
    amount_discount_equipments = fields.Monetary(string="Amount Discount", store=True, readonly=True,
                                                 compute='_compute_amount_equipments')
    amount_tax_equipments = fields.Monetary(string="Tax", store=True, readonly=True,
                                            compute='_compute_amount_equipments')
    amount_total_equipments = fields.Monetary(string="Total", store=True, readonly=True,
                                              compute='_compute_amount_equipments')

    specialty_services_lines = fields.One2many("tender.specialty.services.request", "tender_quotation_id",
                                               string="specialty services request Lines")
    amount_untaxed_specialty_services = fields.Monetary(string="Untaxed Amount", store=True, readonly=True,
                                                        compute='_compute_amount_specialty_services')
    amount_discount_specialty_services = fields.Monetary(string="Amount Discount", store=True, readonly=True,
                                                         compute='_compute_amount_specialty_services')
    amount_tax_specialty_services = fields.Monetary(string="Tax", store=True, readonly=True,
                                                    compute='_compute_amount_specialty_services')
    amount_total_specialty_services = fields.Monetary(string="Total", store=True, readonly=True,
                                                      compute='_compute_amount_specialty_services')
    amount_untaxed = fields.Float(string="Subtotal", compute="_compute_amount", store=True, readonly=True)
    amount_discount = fields.Float(string="Amount Discount", compute="_compute_amount", store=True, readonly=True)
    amount_tax = fields.Float(string="Amount Tax", compute="_compute_amount", store=True, readonly=True)
    amount_total = fields.Float(string="Total", compute="_compute_amount", store=True, readonly=True)

    customer_reference = fields.Char(string='Customer Reference', copy=False)
    partner_id = fields.Many2one("res.partner", string="Customer", required=True, index=True, copy=False,
                                 check_company=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_invoice_id = fields.Many2one("res.partner", string="Invoice Address", required=True, copy=False,
                                         check_company=True,
                                         domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_shipping_id = fields.Many2one("res.partner", string="Delivery Address", required=True, copy=False,
                                          check_company=True,
                                          domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    company_id = fields.Many2one("res.company", string="Company", index=True, tracking=True,
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one("res.currency", "Currency", required=True, copy=False, tracking=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    pricelist_id = fields.Many2one("product.pricelist", "Pricelist", check_company=True, tracking=True,
                                   domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                   copy=False)
    payment_term_id = fields.Many2one("account.payment.term", "Payment Terms", check_company=True, tracking=True,
                                      domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                      copy=False)
    user_id = fields.Many2one("res.users", "Salesperson", index=True, tracking=True, default=lambda self: self.env.user,
                              domain=lambda self: [
                                  ("groups_id", "in", self.env.ref("sales_team.group_sale_salesman").id)], copy=False)
    team_id = fields.Many2one("crm.team", "Sales Team", default=_get_default_team, check_company=True, tracking=True,
                              copy=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    require_signature = fields.Boolean("Online Signature", default=_get_default_require_signature, tracking=True,
                                       copy=False)
    require_payment = fields.Boolean("Online Payment", default=_get_default_require_payment, tracking=True, copy=False)
    fiscal_position_id = fields.Many2one("account.fiscal.position", "Fiscal Position", check_company=True,
                                         tracking=True, copy=False,
                                         domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    analytic_account_id = fields.Many2one("account.analytic.account", string="Analytic Account", index=True,
                                          tracking=True, copy=False)
    commitment_date = fields.Datetime("Delivery Date", tracking=True, copy=False)
    signature = fields.Image("Signature", copy=False, attachment=True, max_width=1024, max_height=1024)
    signed_by = fields.Char("Signed By", copy=False)
    signed_on = fields.Datetime("Signed On", copy=False)
    incoterm = fields.Many2one("account.incoterms", "Incoterm", copy=False)
    picking_policy = fields.Selection([
        ("direct", "As soon as possible"),
        ("one", "When all products are ready")], string="Shipping Policy", required=True, default="direct",
        tracking=True, copy=False)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", check_company=True, required=True,
                                   tracking=True, copy=False, default=_default_warehouse_id)
    tender_contracts_count = fields.Integer(compute="_compute_tender_contracts_count", string="Tender Contracts Count")
    tender_contract_number = fields.Char(compute="_compute_tender_contract_number", string="Contract Number")
    tender_lead_id = fields.Many2one("tender.lead", string="Lead", tracking=True, copy=False)
    notes = fields.Text(string="Notes", copy=False)
    terms_conditions_id = fields.Many2one("tender.quotation.term.condition", string="Terms & Conditions", index=True,
                                          tracking=True, copy=False)
    terms_and_conditions = fields.Text(string="Terms & Conditions", copy=False)

    @api.depends("name", "version_number")
    def _compute_complete_number(self):
        for quotation in self:
            complete_number = quotation.name
            if quotation.version_number:
                complete_number += quotation.version_number

            quotation.complete_number = complete_number

    def _compute_tender_contracts_count(self):
        tender_contract_obj = self.env["tender.contract"].sudo()
        for quotation in self:
            quotation.tender_contracts_count = tender_contract_obj.search_count(
                [("tender_quotation_id", "=", quotation.id)])

    def _compute_tender_contract_number(self):
        tender_contract_obj = self.env["tender.contract"].sudo()
        for quotation in self:
            tender_contract = tender_contract_obj.search_read([("tender_quotation_id", "=", quotation.id)], ["ref"],
                                                              limit=1)
            quotation.tender_contract_number = tender_contract and tender_contract[0]["ref"] or False

    @api.depends('manpower_lines.amount_untaxed', 'manpower_lines.amount_tax')
    def _compute_amount_manpower(self):
        for quotation in self:
            amount_untaxed = 0
            amount_discount = 0
            amount_tax = 0
            amount_total = 0

            for line in quotation.manpower_lines:
                amount_untaxed += line.amount_untaxed
                amount_discount += line.amount_discount
                amount_tax += line.amount_tax
                amount_total += line.amount_total

            quotation.amount_untaxed_manpower = amount_untaxed
            quotation.amount_discount_manpower = amount_discount
            quotation.amount_tax_manpower = amount_tax
            quotation.amount_total_manpower = amount_total

    @api.depends('equipments_lines.amount_untaxed', 'equipments_lines.amount_tax')
    def _compute_amount_equipments(self):
        for quotation in self:
            amount_untaxed = 0
            amount_discount = 0
            amount_tax = 0
            amount_total = 0

            for line in quotation.equipments_lines:
                amount_untaxed += line.amount_untaxed
                amount_discount += line.amount_discount
                amount_tax += line.amount_tax
                amount_total += line.amount_total

            quotation.amount_untaxed_equipments = amount_untaxed
            quotation.amount_discount_equipments = amount_discount
            quotation.amount_tax_equipments = amount_tax
            quotation.amount_total_equipments = amount_total

    @api.depends('specialty_services_lines.amount_untaxed', 'specialty_services_lines.amount_tax')
    def _compute_amount_specialty_services(self):
        for quotation in self:
            amount_untaxed = 0
            amount_discount = 0
            amount_tax = 0
            amount_total = 0

            for line in quotation.specialty_services_lines:
                amount_untaxed += line.amount_untaxed
                amount_discount += line.amount_discount
                amount_tax += line.amount_tax
                amount_total += line.amount_total

            quotation.amount_untaxed_specialty_services = amount_untaxed
            quotation.amount_discount_specialty_services = amount_discount
            quotation.amount_tax_specialty_services = amount_tax
            quotation.amount_total_specialty_services = amount_total

    @api.depends("amount_untaxed_manpower", "amount_discount_manpower", "amount_tax_manpower", "amount_total_manpower",
                 "amount_untaxed_equipments", "amount_discount_equipments", "amount_tax_equipments",
                 "amount_total_equipments", "amount_untaxed_specialty_services", "amount_discount_specialty_services",
                 "amount_tax_specialty_services", "amount_total_specialty_services")
    def _compute_amount(self):
        for quotation in self:
            quotation.amount_untaxed = quotation.amount_untaxed_manpower + quotation.amount_untaxed_equipments + quotation.amount_untaxed_specialty_services
            quotation.amount_discount = quotation.amount_discount_manpower + quotation.amount_discount_equipments + quotation.amount_discount_specialty_services
            quotation.amount_tax = quotation.amount_tax_manpower + quotation.amount_tax_equipments + quotation.amount_tax_specialty_services
            quotation.amount_total = quotation.amount_total_manpower + quotation.amount_total_equipments + quotation.amount_total_specialty_services

    @api.onchange('partner_shipping_id', 'partner_id')
    def onchange_partner_shipping_id(self):
        self.fiscal_position_id = self.env["account.fiscal.position"].with_context(
            force_company=self.company_id.id).get_fiscal_position(self.partner_id.id, self.partner_shipping_id.id)

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        values = {
            "pricelist_id": self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            "payment_term_id": self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            "partner_invoice_id": False,
            "partner_shipping_id": False,
        }

        if self.partner_id:
            address = self.partner_id.address_get(["delivery", "invoice"])
            values["partner_invoice_id"] = address["invoice"]
            values["partner_shipping_id"] = address["delivery"]

            user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id or self.env.user
            if self.user_id != user:
                values['user_id'] = user.id

            if not self.team_id:
                values["team_id"] = self.env["crm.team"]._get_default_team_id(user_id=user.id)

        self.update(values)

    @api.onchange("user_id")
    def onchange_user_id(self):
        if self.user_id:
            self.team_id = self.env["crm.team"]._get_default_team_id(user_id=self.user_id.id)

    @api.onchange("company_id")
    def onchange_company_id(self):
        self.warehouse_id = self.env["stock.warehouse"].search([("company_id", "=", self.company_id.id)], limit=1)

    @api.onchange("terms_conditions_id")
    def onchange_terms_conditions(self):
        if self.terms_conditions_id:
            self.terms_and_conditions = self.terms_conditions_id.description

    @api.model
    def create(self, vals):
        res = super(TenderQuotation, self).create(vals)
        if res.tender_lead_id and res.tender_lead_id.crm_lead_id:
            crm_lead = res.tender_lead_id.crm_lead_id
            crm_lead.message_post(partner_ids=crm_lead.message_partner_ids.ids, body=_("Quotation created"),
                                  subtype_xmlid='mail.mt_comment')
        return res

    def unlink(self):
        for quotation in self:
            if quotation.state == "done":
                raise UserError(_("You cannot delete quotation %s which is done") % quotation.name)

            if quotation.has_version:
                raise UserError(_("You cannot delete quotation %s which have other version") % quotation.name)

            if quotation.parent_quotation_id:
                raise UserError(
                    _("You cannot delete quotation %s which is version for other quotation") % quotation.name)

        return super(TenderQuotation, self).unlink()

    def action_send_email(self):
        self.ensure_one()

        form = self.env.ref("mail.email_compose_message_wizard_form")

        ctx = {
            "default_model": "tender.quotation",
            "default_res_id": self.id,
            "default_composition_mode": "comment",
            "default_mark_so_as_sent": True,
            "custom_layout": "mail.mail_notification_paynow",
            "proforma": self.env.context.get('proforma', False),
            "force_email": True
        }

        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(form.id, "form")],
            "view_id": form.id,
            "target": "new",
            "context": ctx,
        }

    def action_draft(self):
        if self.state in ["in progress", "done"] or self.has_version:
            return

        return self.write({"state": "draft"})

    def action_confirm(self):
        if self.state != "draft":
            return

        vals = {"state": "in progress"}
        if self.name == "/":
            vals.update({"name": self.env["ir.sequence"].next_by_code("tender.quotation")})

        return self.write(vals)

    def action_done(self):
        if self.state != "in progress":
            return

        self.write({"state": "done"})

        return self.action_create_contract()

    def action_new_version(self):
        if self.state != "in progress":
            return

        action = self.sudo().env.ref("contracts_management.action_tender_quotation_version_wizard", False)
        result = action.read()[0]
        return result

    def action_cancel(self):
        if self.state != "in progress":
            return

        return self.write({"state": "cancel"})

    def action_create_contract(self):
        # create tender contract
        if self.tender_contracts_count != 0:
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
            "default_tender_quotation_id": self.id,
            "default_name": self.name,
            "default_ref": self.name,
            "default_partner_id": self.partner_id.id,
            "default_analytic_account_id": self.analytic_account_id.id,
            "default_pricelist_id": self.pricelist_id.id,
            "default_company_id": self.company_id.id,
            "default_currency_id": self.currency_id.id,
            "default_manpower_lines": manpower_lines,
            "default_equipments_lines": equipments_lines,
            "default_specialty_services_lines": specialty_services_lines,
            "default_notes": self.notes,
        })

        form = self.env.ref("contracts_management.view_tender_contract_form")
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            'view_id': form.id,
            "res_model": "tender.contract",
            "context": context
        }

    def get_tender_contract(self):
        # get tender contract of quotation
        tender_contract = self.env["tender.contract"].search([("tender_quotation_id", "=", self.id)], limit=1)
        if not tender_contract:
            return

        form = self.env.ref("contracts_management.view_tender_contract_form")
        return {
            "name": tender_contract.name,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            'view_id': form.id,
            "res_model": "tender.contract",
            "res_id": tender_contract.id,
        }

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return self.env.ref('contracts_management.mt_tender_quotation_reset_draft')
        elif 'state' in init_values and self.state == 'in progress':
            return self.env.ref('contracts_management.mt_tender_quotation_in_progress')
        elif 'state' in init_values and self.state == 'done':
            return self.env.ref('contracts_management.mt_tender_quotation_done')
        elif 'state' in init_values and self.state == 'cancel':
            return self.env.ref('contracts_management.mt_tender_quotation_cancel')

        return super(TenderQuotation, self)._track_subtype(init_values)
