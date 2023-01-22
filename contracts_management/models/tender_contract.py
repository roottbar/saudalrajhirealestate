# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval


class TenderContractType(models.Model):
    _name = "tender.contract.type"
    _description = "Tender & Contract Types"

    name = fields.Char("Name", required=True, index=True, translate=True, copy=False)
    code = fields.Char("Code", copy=False)


class TenderContractCategory(models.Model):
    _name = "tender.contract.category"
    _description = "Tender Contract Category"
    _parent_store = True
    _rec_name = "complete_name"
    _order = "complete_name"

    name = fields.Char("Name", required=True, index=True, translate=True, copy=False)
    complete_name = fields.Char("Complete Name", compute="_compute_complete_name", store=True)
    parent_id = fields.Many2one("tender.contract.category", "Parent Category", index=True, ondelete="cascade")
    child_id = fields.One2many("tender.contract.category", "parent_id", "Child Categories")
    parent_path = fields.Char(index=True)

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = "%s / %s" % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class TenderContract(models.Model):
    _name = "tender.contract"
    _description = "Tender Contracts"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Name", required=True, index=True, translate=True, copy=False, tracking=True)
    ref = fields.Char(string="Reference", copy=False, tracking=True)
    partner_id = fields.Many2one("res.partner", required=True, string="Customer", index=True, copy=False,
                                 check_company=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    tender_project_id = fields.Many2one("tender.project", string="Project", index=True, tracking=True,
                                        check_company=True, copy=True)
    start_date = fields.Date("Start Date", default=fields.Date.today, required=True, copy=False)
    end_date = fields.Date("End Date", copy=False)
    state = fields.Selection([
        ("open", "Open"),
        ("in progress", "In Progress"),
        ("closed", "Closed")], string="Status", index=True, readonly=True, default="open", copy=False, tracking=True)
    type_id = fields.Many2one("tender.contract.type", string="Type", required=True, index=True, tracking=True,
                              copy=True)
    analytic_account_id = fields.Many2one("account.analytic.account", string="Analytic Account", index=True,
                                          tracking=True, copy=False)
    analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Analytic Tags")
    currency_id = fields.Many2one("res.currency", "Currency", required=True, copy=False, tracking=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one("res.company", "Company", required=True, index=True, copy=False, tracking=True,
                                 default=lambda self: self.env.user.company_id.id)
    auto_generated_reference = fields.Boolean("Auto Generated Reference", copy=False)
    auto_generated_analytic_account = fields.Boolean("Auto Generated Analytic Account", copy=False)
    auto_generated_project = fields.Boolean("Auto Generated Project", copy=False)
    project_id = fields.Many2one("project.project", string="Project", tracking=True, copy=True,
                                 check_company=True)
    category_id = fields.Many2one("tender.contract.category", "Category", required=True, index=True, copy=False,
                                  tracking=True)
    worker_ids = fields.Many2many("hr.employee", string="Workers", domain=[("is_worker", "=", True)])
    select_tender_project = fields.Boolean("Select Project", copy=False)
    pricelist_id = fields.Many2one("product.pricelist", "Pricelist", check_company=True, copy=False,
                                   domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    expected_value = fields.Monetary(string="Expected Value", digits="Account", required=True)
    actual_value = fields.Monetary(string="Actual Value", compute="_compute_actual_value")
    actual_net_profit = fields.Monetary(string="Actual Net Profit", compute="_compute_actual_value")
    notes = fields.Text(string="Notes", copy=False)
    manpower_lines = fields.One2many("tender.service.manpower", "tender_contract_id", string="Manpower Lines")
    amount_untaxed_manpower = fields.Monetary(string="Untaxed Amount", store=True, readonly=True,
                                              compute='_compute_amount_manpower')
    amount_discount_manpower = fields.Monetary(string="Amount Discount", store=True, readonly=True,
                                               compute='_compute_amount_manpower')
    amount_tax_manpower = fields.Monetary(string="Tax", store=True, readonly=True, compute='_compute_amount_manpower')
    amount_total_manpower = fields.Monetary(string="Total", store=True, readonly=True,
                                            compute='_compute_amount_manpower')

    equipments_lines = fields.One2many("tender.service.equipments", "tender_contract_id", string="Equipments Lines")
    amount_untaxed_equipments = fields.Monetary(string="Untaxed Amount", store=True, readonly=True,
                                                compute='_compute_amount_equipments')
    amount_discount_equipments = fields.Monetary(string="Amount Discount", store=True, readonly=True,
                                                 compute='_compute_amount_equipments')
    amount_tax_equipments = fields.Monetary(string="Tax", store=True, readonly=True,
                                            compute='_compute_amount_equipments')
    amount_total_equipments = fields.Monetary(string="Total", store=True, readonly=True,
                                              compute='_compute_amount_equipments')

    specialty_services_lines = fields.One2many("tender.specialty.services.request", "tender_contract_id",
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

    documents_count = fields.Integer(compute="_compute_documents_count", string="Document Count")
    has_invoices_service = fields.Boolean(compute="_compute_has_invoices_service", string="Has Invoices Service")
    create_invoice = fields.Boolean(compute="_compute_has_invoices_service", string="Create Invoice")
    tender_quotation_id = fields.Many2one("tender.quotation", string="Quotation", tracking=True, copy=False)

    @api.constrains("expected_value")
    def _check_expected_value(self):
        if self.expected_value < 0:
            raise ValidationError(_("Expected Value must be greater than or equal to zero"))

    @api.constrains("start_date", "end_date")
    def _check_date(self):
        if self.end_date and self.start_date >= self.end_date:
            raise ValidationError(_("End date must be greater than start date"))

    def _compute_actual_value(self):
        account_analytic_line_obj = self.env["account.analytic.line"]
        for contract in self:
            account_analytic_lines = account_analytic_line_obj.search(
                [("account_id", "=", contract.analytic_account_id.id)])
            contract.actual_value = sum(
                account_analytic_line.amount for account_analytic_line in account_analytic_lines)
            contract.actual_net_profit = contract.expected_value - contract.actual_value

    def _compute_documents_count(self):
        attachment_obj = self.env["ir.attachment"]
        for contract in self:
            contract.documents_count = attachment_obj.search_count(
                [("res_model", "=", "tender.contract"), ("res_id", "=", contract.id)])

    def _compute_has_invoices_service(self):
        service_template_obj = self.env["tender.service.template"]
        for contract in self:
            contract.has_invoices_service = service_template_obj.search_count(
                [("invoice_id", "!=", False), ("tender_contract_id", "=", contract.id)]) != 0 and True or False
            contract.create_invoice = service_template_obj.search_count(
                [("invoice_id", "=", False), ("tender_contract_id", "=", contract.id)]) != 0 and True or False

    @api.depends('manpower_lines.amount_untaxed', 'manpower_lines.amount_tax')
    def _compute_amount_manpower(self):
        for contract in self:
            amount_untaxed = 0
            amount_discount = 0
            amount_tax = 0
            amount_total = 0

            for line in contract.manpower_lines:
                amount_untaxed += line.amount_untaxed
                amount_discount += line.amount_discount
                amount_tax += line.amount_tax
                amount_total += line.amount_total

            contract.amount_untaxed_manpower = amount_untaxed
            contract.amount_discount_manpower = amount_discount
            contract.amount_tax_manpower = amount_tax
            contract.amount_total_manpower = amount_total

    @api.depends('equipments_lines.amount_untaxed', 'equipments_lines.amount_tax')
    def _compute_amount_equipments(self):
        for contract in self:
            amount_untaxed = 0
            amount_discount = 0
            amount_tax = 0
            amount_total = 0

            for line in contract.equipments_lines:
                amount_untaxed += line.amount_untaxed
                amount_discount += line.amount_discount
                amount_tax += line.amount_tax
                amount_total += line.amount_total

            contract.amount_untaxed_equipments = amount_untaxed
            contract.amount_discount_equipments = amount_discount
            contract.amount_tax_equipments = amount_tax
            contract.amount_total_equipments = amount_total

    @api.depends('specialty_services_lines.amount_untaxed', 'specialty_services_lines.amount_tax')
    def _compute_amount_specialty_services(self):
        for contract in self:
            amount_untaxed = 0
            amount_discount = 0
            amount_tax = 0
            amount_total = 0

            for line in contract.specialty_services_lines:
                amount_untaxed += line.amount_untaxed
                amount_discount += line.amount_discount
                amount_tax += line.amount_tax
                amount_total += line.amount_total

            contract.amount_untaxed_specialty_services = amount_untaxed
            contract.amount_discount_specialty_services = amount_discount
            contract.amount_tax_specialty_services = amount_tax
            contract.amount_total_specialty_services = amount_total

    @api.depends("amount_untaxed_manpower", "amount_discount_manpower", "amount_tax_manpower", "amount_total_manpower",
                 "amount_untaxed_equipments", "amount_discount_equipments", "amount_tax_equipments",
                 "amount_total_equipments", "amount_untaxed_specialty_services", "amount_discount_specialty_services",
                 "amount_tax_specialty_services", "amount_total_specialty_services")
    def _compute_amount(self):
        for contract in self:
            contract.amount_untaxed = contract.amount_untaxed_manpower + contract.amount_untaxed_equipments + contract.amount_untaxed_specialty_services
            contract.amount_discount = contract.amount_discount_manpower + contract.amount_discount_equipments + contract.amount_discount_specialty_services
            contract.amount_tax = contract.amount_tax_manpower + contract.amount_tax_equipments + contract.amount_tax_specialty_services
            contract.amount_total = contract.amount_total_manpower + contract.amount_total_equipments + contract.amount_total_specialty_services

    @api.onchange("tender_project_id")
    def _onchange_tender_project(self):
        if self.tender_project_id:
            self.partner_id = self.tender_project_id.partner_id

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if args is None:
            args = []
        domain = args + ["|", ("name", operator, name), ("ref", operator, name)]
        return self._search(domain, limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        res = dict(super(TenderContract, self).name_get())
        for contract in self:
            if contract.tender_project_id:
                res[contract.id] = "%s/%s" % (contract.tender_project_id.name, contract.name)
        return list(res.items())

    @api.model
    def create(self, vals):
        res = super(TenderContract, self).create(vals)
        if res.tender_quotation_id and res.tender_quotation_id.tender_lead_id and res.tender_quotation_id.tender_lead_id.crm_lead_id:
            crm_lead = res.tender_quotation_id.tender_lead_id.crm_lead_id
            crm_lead.message_post(partner_ids=crm_lead.message_partner_ids.ids, body=_("Contract created"),
                                  subtype_xmlid='mail.mt_comment')
        return res

    def unlink(self):
        for contract in self:
            if contract.state != "open":
                raise UserError(_("You cannot delete contract %s which is not open") % contract.name)

        return super(TenderContract, self).unlink()

    @api.model
    def default_get(self, default_fields):
        # get  default select tender project from settings
        select_tender_project = self.env["ir.config_parameter"].sudo().get_param(
            "contracts_management.select_tender_project")

        contextual_self = self.with_context(default_select_tender_project=select_tender_project)
        return super(TenderContract, contextual_self).default_get(default_fields)

    def generate_analytic_account(self):
        # create analytic account
        analytic_account_obj = self.env["account.analytic.account"]
        for contract in self:
            if contract.auto_generated_analytic_account or contract.state != "open":
                continue

            analytic_accounts = analytic_account_obj.search([("name", "=", self.name), ("code", "=", self.ref)])
            if analytic_accounts:
                raise ValidationError(_("Analytic Account with same name and reference already exists !"))

            analytic_account = analytic_account_obj.create({
                "name": self.name,
                "code": self.ref,
                "partner_id": self.partner_id.id
            })

            contract.write({"analytic_account_id": analytic_account.id, "auto_generated_analytic_account": True})
        return True

    def generate_project(self):
        # create project
        for contract in self:
            if contract.auto_generated_project or contract.state != "open":
                continue

            name = self.name
            if self.ref:
                name += "/" + self.ref

            project = self.env["project.project"].create({
                "name": name,
                "partner_id": self.partner_id.id,
                "analytic_account_id": self.analytic_account_id.id
            })
            contract.write({"project_id": project.id, "auto_generated_project": True})
        return True

    def generate_reference(self):
        sequence_obj = self.env["ir.sequence"]
        for contract in self:
            if contract.auto_generated_reference or contract.state != "open":
                continue

            contract.write({
                "ref": sequence_obj.next_by_code("tender.contract"),
                "auto_generated_reference": True
            })
        return True

    def action_open(self):
        for contract in self:
            if contract.state != "open":
                continue

            if not contract.analytic_account_id:
                raise UserError(_("Auto generate or select analytic account for contract %s before open"))

            if not contract.ref:
                raise UserError(_("Auto generate or write reference for contract %s before open"))

            contract.write({"state": "in progress"})
        return True

    @api.model
    def _prepare_customer_invoice(self, partner_id, journal_id, invoice_lines):
        vals = {
            "ref": self.name + "/" + self.ref,
            "move_type": "out_invoice",
            "journal_id": journal_id,
            "invoice_date": self.start_date,
            "invoice_date_due": self.end_date,
            "currency_id": self.currency_id.id,
            "invoice_user_id": self.create_uid.id,
            "partner_id": partner_id,
            "invoice_origin": self.ref,
            "narration": self.notes,
            "invoice_line_ids": invoice_lines,
            "company_id": self.company_id.id,
            "tender_contract_id": self.id,
        }
        return vals

    def _prepare_invoice_line(self, line, partner_id):
        service_category_id = line.service_type_id.service_category_id
        account_id = service_category_id.account_income_id or service_category_id.parent_id.account_income_id

        if not account_id:
            raise ValidationError(_("Service Category %s not have income account" % service_category_id.display_name))

        res = {
            "partner_id": partner_id,
            "date_maturity": self.end_date,
            "currency_id": self.currency_id,
            "display_type": line.display_type,
            "sequence": line.sequence,
            "name": line.name,
            "product_id": line.service_product_id.id,
            "quantity": line.quantity,
            "price_unit": line.total_price_unit,
            "discount": line.discount,
            "tax_ids": [(6, 0, line.tax_ids.ids)],
            "account_id": account_id.id,
            "analytic_account_id": self.analytic_account_id.id,
            "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)],
            "service_type_id": line.service_type_id.id,
            "branch_id": line.branch_id.id
        }
        return res

    def create_customer_invoice(self, manpower_lines, equipments_lines, specialty_services_lines):
        journal_id = self.env["ir.config_parameter"].sudo().get_param(
            "contracts_management.tender_contract_journal_id", False)
        if not journal_id:
            raise ValidationError(_("Please select journal of invoice in settings"))

        invoice_lines = []
        partner_invoice_id = self.partner_id.address_get(["invoice"])["invoice"]

        # manpower services
        for line in manpower_lines:
            invoice_lines.append([0, 0, self._prepare_invoice_line(line, partner_invoice_id)])

        # equipments services
        for line in equipments_lines:
            invoice_lines.append([0, 0, self._prepare_invoice_line(line, partner_invoice_id)])

        # specialty services
        for line in specialty_services_lines:
            invoice_lines.append([0, 0, self._prepare_invoice_line(line, partner_invoice_id)])

        vals = self._prepare_customer_invoice(partner_invoice_id, eval(journal_id), invoice_lines)
        invoice = self.env['account.move'].create(vals)
        invoice.action_post()
        return invoice

    def action_create_invoice(self):
        # create invoice if there services not have invoice
        manpower_lines = self.manpower_lines.filtered(lambda l: not l.display_type and not l.invoice_id)
        equipments_lines = self.equipments_lines.filtered(lambda l: not l.display_type and not l.invoice_id)
        specialty_services_lines = self.specialty_services_lines.filtered(
            lambda l: not l.display_type and not l.invoice_id)

        if manpower_lines or equipments_lines or specialty_services_lines:
            invoice = self.create_customer_invoice(manpower_lines, equipments_lines, specialty_services_lines)

            # update services
            manpower_lines.write({"invoice_id": invoice.id})
            equipments_lines.write({"invoice_id": invoice.id})
            specialty_services_lines.write({"invoice_id": invoice.id})

        return True

    def action_close(self):
        for contract in self:
            if contract.state != "in progress":
                continue

            # create invoice or not
            self.action_create_invoice()

            # update contract
            contract.write({"state": "closed"})
        return True

    def get_documents(self):
        action = self.sudo().env.ref("base.action_attachment")
        result = action.read()[0]
        result["domain"] = [("res_model", "=", "tender.contract"), ("res_id", "=", self.id)]
        result["context"] = {"default_res_model": "tender.contract", "default_res_id": self.id}
        return result

    def get_workers(self):
        action = self.sudo().env.ref("contracts_management.action_tender_workers")
        result = action.read()[0]
        result["domain"] = [("id", "in", self.worker_ids.ids)]
        return result

    def get_tasks(self):
        action = self.sudo().env.ref("project.action_view_task", False)
        result = action.read()[0]

        if self.state == "in progress":
            ctx = safe_eval(result["context"])
            ctx.update({"default_tender_contract_id": self.id, "default_project_id": self.project_id.id})
            result["context"] = ctx

        result["domain"] = [("tender_contract_id", "=", self.id)]
        return result

    def get_timesheets(self):
        tasks = self.sudo().env["project.task"].search([("tender_contract_id", "=", self.id)])
        action = self.sudo().env.ref("sale_timesheet.timesheet_action_from_sales_order", False)
        result = action.read()[0]
        result["domain"] = [("task_id", "in", tasks.ids)]
        return result

    def get_cost_analytic_account(self):
        action = self.sudo().env.ref("analytic.account_analytic_line_action", False)
        result = action.read()[0]
        result["context"] = {"search_default_group_date": 1, "default_account_id": self.analytic_account_id.id,
                             "default_partner_id": self.partner_id.id}
        result["domain"] = [("account_id", "=", self.analytic_account_id.id)]
        return result

    def get_invoices(self):
        action = self.sudo().env.ref("account.action_move_out_invoice_type", False)
        result = action.read()[0]

        if self.state == "in progress":
            ctx = safe_eval(result["context"])
            ctx.update({"default_tender_contract_id": self.id, "default_partner_id": self.partner_id.id})
            result["context"] = ctx

        result["domain"] = [("move_type", "in", ["out_invoice", "out_refund", "in_invoice", "in_refund"]),
                            ("tender_contract_id", "=", self.id)]
        return result

    def get_purchases(self):
        action = self.sudo().env.ref("purchase.purchase_rfq", False)
        result = action.read()[0]

        if self.state == "in progress":
            ctx = safe_eval(result["context"])
            ctx.update({"default_tender_contract_id": self.id, "default_partner_id": self.partner_id.id})
            result["context"] = ctx

        result["domain"] = [("tender_contract_id", "=", self.id)]
        return result

    def get_sales(self):
        action = self.sudo().env.ref("sale.action_orders", False)
        result = action.read()[0]

        if self.state == "in progress":
            ctx = safe_eval(result["context"])
            ctx.update({"default_tender_contract_id": self.id, "default_partner_id": self.partner_id.id})
            result["context"] = ctx

        result["domain"] = [("tender_contract_id", "=", self.id)]
        return result

    def get_payments(self):
        action = self.sudo().env.ref("account.action_account_payments", False)
        result = action.read()[0]

        if self.state == "in progress":
            ctx = safe_eval(result["context"])
            ctx.update({"default_tender_contract_id": self.id, "default_partner_id": self.partner_id.id,
                        "search_default_inbound_filter": 0})
            result["context"] = ctx

        result["domain"] = [("tender_contract_id", "=", self.id)]
        return result

    def get_moves(self):
        action = self.sudo().env.ref("stock.stock_move_action", False)
        result = action.read()[0]
        result["domain"] = [("tender_contract_id", "=", self.id)]

        return result

    def print_customer_invoice(self):
        # print customer invoice report or open popup if there more than one invoice
        invoices = self.env["tender.service.template"].search([("tender_contract_id", "=", self.id)]).mapped(
            "invoice_id")
        if len(invoices) > 1:
            action = self.sudo().env.ref("contracts_management.action_tender_contract_invoice_report_wizard", False)
            result = action.read()[0]
            result["context"] = {"invoice_service_ids": invoices.ids}

            return result

        return self.env.ref("contracts_management.action_report_invoice_tender_contract").report_action(invoices)

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'in progress':
            return self.env.ref('contracts_management.mt_tender_contract_in_progress')
        elif 'state' in init_values and self.state == 'closed':
            return self.env.ref('contracts_management.mt_tender_contract_close')
        return super(TenderContract, self)._track_subtype(init_values)
