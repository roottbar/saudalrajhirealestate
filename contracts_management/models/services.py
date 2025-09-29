# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang


class TenderServiceCategory(models.Model):
    _name = "tender.service.category"
    _description = "Tender Services Categories"
    _parent_store = True
    _rec_name = "complete_name"
    _order = "complete_name"

    name = fields.Char("Name", required=True, index=True, translate=True, copy=False)
    code = fields.Char("Code", copy=False)
    complete_name = fields.Char("Complete Name", compute="_compute_complete_name", store=True)
    parent_id = fields.Many2one("tender.service.category", "Parent Category", index=True, ondelete="cascade")
    child_id = fields.One2many("tender.service.category", "parent_id", "Child Services")
    parent_path = fields.Char(index=True)
    account_income_id = fields.Many2one("account.account", string="Income Account", copy=False,
                                        domain=[("deprecated", "=", False), ("internal_type", "=", "other"),
                                                ("is_off_balance", "=", False)])
    account_expense_id = fields.Many2one("account.account", string="Expense Account", copy=False,
                                         domain=[("deprecated", "=", False), ("internal_type", "=", "other"),
                                                 ("is_off_balance", "=", False)])

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for service in self:
            if service.parent_id:
                service.complete_name = "%s / %s" % (service.parent_id.complete_name, service.name)
            else:
                service.complete_name = service.name


class TenderServiceType(models.Model):
    _name = "tender.service.type"
    _description = "Tender Services Types"

    name = fields.Char("Name", required=True, index=True, translate=True, copy=False)
    code = fields.Char("Code", copy=False)
    service_category_id = fields.Many2one("tender.service.category", required=True, index=True, string="Category",
                                          copy=False, domain=[("parent_id", "!=", False)])
    products = fields.Many2many("product.product", string="Products")


class TenderServiceTemplate(models.Model):
    _name = "tender.service.template"
    _description = "Tender Services Template"
    _order = "sequence,id"

    name = fields.Char(string="Label", required=True, copy=False)
    sequence = fields.Integer(default=1, copy=False)
    service_product_id = fields.Many2one("product.product", string="Service", copy=False)
    service_type_id = fields.Many2one("tender.service.type", string="Service Type", copy=False)
    display_type = fields.Selection([
        ("line_section", "Section"),
        ("line_note", "Note")], default=False, string="Display Type", copy=False)
    price_unit = fields.Float(string="Unit Price", digits="Product Price", required=True, copy=False)
    total_price_unit = fields.Float(string="Total Unit Price", digits="Product Price", required=True, copy=False)
    quantity = fields.Float(string="Quantity", digits="Product Unit of Measure", default=1, required=True)
    discount = fields.Float(string="Discount (%)", digits="Discount", default=0.0, copy=False)
    tax_ids = fields.Many2many("account.tax", string="Taxes", copy=False,
                               domain=[("type_tax_use", "=", "sale"), "|", ("active", "=", False),
                                       ("active", "=", True)])
    branch_id = fields.Many2one("tender.branch", string="Branch", copy=False)
    tender_contract_id = fields.Many2one("tender.contract", string="Contract", ondelete="cascade", copy=False)
    tender_quotation_id = fields.Many2one("tender.quotation", string="Quotation", ondelete="cascade", copy=False)
    tender_lead_id = fields.Many2one("tender.lead", string="Lead", ondelete="cascade", copy=False)
    amount_untaxed = fields.Float(string="Subtotal", compute="_compute_amount", store=True, readonly=True)
    amount_discount = fields.Float(string="Amount Discount", compute="_compute_amount", store=True, readonly=True)
    amount_tax = fields.Float(string="Amount Tax", compute="_compute_amount", store=True, readonly=True)
    amount_total = fields.Float(string="Total", compute="_compute_amount", store=True, readonly=True)
    invoice_id = fields.Many2one("account.move", string="Invoice", copy=False)

    @api.depends("total_price_unit", "quantity", "discount", "tax_ids")
    def _compute_amount(self):
        for line in self:
            price_unit = line.total_price_unit
            amount_discount = 0
            if line.discount != 0:
                amount_discount = price_unit * line.discount / 100
                price_unit -= amount_discount

            taxes = line.tax_ids.compute_all(price_unit, quantity=line.quantity)
            amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            amount_untaxed = taxes['total_excluded']

            line.amount_untaxed = amount_untaxed
            line.amount_tax = amount_tax
            line.amount_total = amount_untaxed + amount_tax
            line.amount_discount = amount_discount * line.quantity

    @api.onchange('service_product_id')
    def onchange_service_product(self):
        if self.service_product_id:
            partner = self.tender_lead_id.partner_id or self.tender_quotation_id.partner_id or self.tender_contract_id.partner_id
            pricelist = self.tender_quotation_id.pricelist_id or self.tender_contract_id.pricelist_id
            product = self.service_product_id.with_context(
                lang=get_lang(self.env, partner.lang).code,
                partner=partner,
                pricelist=pricelist)

            price_unit = product.standard_price
            if pricelist:
                price_unit = product.with_context(pricelist=pricelist.id).price

            vals = {
                "name": product.get_product_multiline_description_sale(),
                "price_unit": price_unit
            }

            if product.taxes_id:
                vals.update({"tax_ids": [(4, tax.id) for tax in product.taxes_id]})

            self.update(vals)

    @api.onchange('price_unit')
    def onchange_price_unit(self):
        self.update({
            "total_price_unit": self.price_unit
        })

    def unlink(self):
        for template in self:
            if template.invoice_id:
                raise UserError(_("You cannot delete service %s which have invoice") % template.name)

        return super(TenderServiceTemplate, self).unlink()

    def _prepare_line(self):
        vals = {
            "name": self.name,
            "sequence": self.sequence,
            "service_product_id": self.service_product_id.id,
            "service_type_id": self.service_type_id.id,
            "display_type": self.display_type,
            "price_unit": self.price_unit,
            "total_price_unit": self.price_unit,
            "quantity": self.quantity,
            "discount": self.discount,
            "tax_ids": [(6, 0, self.tax_ids.ids)],
            "branch_id": self.branch_id.id
        }

        return vals


class TenderServiceManpower(models.Model):
    _name = "tender.service.manpower"
    _description = "Tender Services Manpower"
    _inherits = {"tender.service.template": "service_template_id"}

    service_template_id = fields.Many2one("tender.service.template", "Service Template", index=True,
                                          ondelete="cascade", required=True)
    profession_id = fields.Many2one("hr.job", string="Profession/Specialized", copy=False)
    nationality_id = fields.Many2one("res.country", "Nationality", copy=False)
    duration = fields.Float(string="Duration", copy=False)
    work_shifts = fields.Float("Work Shifts", copy=False)
    resource_calendar_id = fields.Many2one("resource.calendar", "Working hours & days", copy=False)
    accommodation_providing_amount = fields.Float(string="Accommodation Providing", digits="Account", copy=False)
    transportation_providing_amount = fields.Float(string="Transportation providing", digits="Account", copy=False)
    other_amount = fields.Float(string="Other", digits="Account", copy=False)

    @api.onchange("service_type_id")
    def _onchange_service_type(self):
        domain = []
        self.service_product_id = False

        if self.service_type_id:
            domain = [("id", "in", self.service_type_id.products.ids)]

        return {"domain": {"service_product_id": domain}}

    @api.onchange('service_product_id')
    def onchange_service_product(self):
        self.service_template_id.onchange_service_product()

    @api.onchange("price_unit", "quantity", "discount", "tax_ids", "accommodation_providing_amount",
                  "transportation_providing_amount", "other_amount")
    def onchange_price(self):
        # fixed problem calculate manpower form view and total price unit
        total_allowances = self.accommodation_providing_amount + self.transportation_providing_amount + self.other_amount

        self.update({
            "price_unit": self.price_unit,
            "total_price_unit": self.price_unit + total_allowances,
            "quantity": self.quantity,
            "discount": self.discount,
            "tax_ids": self.tax_ids
        })

    @api.onchange("resource_calendar_id")
    def onchange_resource_calendar(self):
        self.duration = self.resource_calendar_id.hours_per_day
        self.work_shifts = self.resource_calendar_id.hours_per_week

    def unlink(self):
        service_templates = self.mapped("service_template_id")
        res = super(TenderServiceManpower, self).unlink()

        # delete all service templates
        service_templates.unlink()
        self.clear_caches()
        return res

    def _prepare_line(self):
        vals = self.service_template_id._prepare_line()

        vals.update({
            "profession_id": self.profession_id.id,
            "nationality_id": self.nationality_id.id,
            "duration": self.duration,
            "resource_calendar_id": self.resource_calendar_id.id,
            "accommodation_providing_amount": self.accommodation_providing_amount,
            "transportation_providing_amount": self.transportation_providing_amount,
            "other_amount": self.other_amount,
            "work_shifts": self.work_shifts
        })
        return vals


class TenderServiceEquipments(models.Model):
    _name = "tender.service.equipments"
    _description = "Tender Services Equipments & tools"
    _inherits = {"tender.service.template": "service_template_id"}

    service_template_id = fields.Many2one("tender.service.template", "Service Template", index=True,
                                          ondelete="cascade", required=True)
    code = fields.Char("Code", copy=False)
    consumption_duration_monthly = fields.Integer(string="Duration/Month", default=1, required=True,
                                                  copy=False)

    @api.onchange("service_type_id")
    def _onchange_service_type(self):
        domain = []
        self.service_product_id = False

        if self.service_type_id:
            domain = [("id", "in", self.service_type_id.products.ids)]

        return {"domain": {"service_product_id": domain}}

    @api.onchange('service_product_id')
    def onchange_service_product(self):
        self.service_template_id.onchange_service_product()

    @api.onchange('price_unit')
    def onchange_price_unit(self):
        self.service_template_id.onchange_price_unit()

    def unlink(self):
        service_templates = self.mapped("service_template_id")
        res = super(TenderServiceEquipments, self).unlink()

        # delete all service templates
        service_templates.unlink()
        self.clear_caches()
        return res

    def _prepare_line(self):
        vals = self.service_template_id._prepare_line()

        vals.update({
            "code": self.code,
            "consumption_duration_monthly": self.consumption_duration_monthly
        })
        return vals


class TenderSpecialtyServicesRequest(models.Model):
    _name = "tender.specialty.services.request"
    _description = "Tender Specialty Services Request"
    _inherits = {"tender.service.template": "service_template_id"}

    service_template_id = fields.Many2one("tender.service.template", "Service Template", index=True,
                                          ondelete="cascade", required=True)
    visit_duration = fields.Float(string="Visit/hrs", default=1, required=True, copy=False)
    total_visits_monthly = fields.Integer(string="Visits Monthly", default=1, required=True, copy=False)
    details = fields.Char("Details", copy=False)

    @api.onchange("service_type_id")
    def _onchange_service_type(self):
        domain = []
        self.service_product_id = False

        if self.service_type_id:
            domain = [("id", "in", self.service_type_id.products.ids)]

        return {"domain": {"service_product_id": domain}}

    @api.onchange('service_product_id')
    def onchange_service_product(self):
        self.service_template_id.onchange_service_product()

    @api.onchange('price_unit')
    def onchange_price_unit(self):
        self.service_template_id.onchange_price_unit()

    def unlink(self):
        service_templates = self.mapped("service_template_id")
        res = super(TenderSpecialtyServicesRequest, self).unlink()

        # delete all service templates
        service_templates.unlink()
        self.clear_caches()
        return res

    def _prepare_line(self):
        vals = self.service_template_id._prepare_line()

        vals.update({
            "visit_duration": self.visit_duration,
            "total_visits_monthly": self.total_visits_monthly,
            "details": self.details
        })
        return vals
