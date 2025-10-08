# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Purchase Request"

    name = fields.Char(string="Name", copy=False, readonly=True, index=True, default=_("Draft Purchase Request"),
                       tracking=True)
    request_by = fields.Many2one("res.users", string="Request By", copy=False, default=lambda self: self.env.user.id,
                                 tracking=True, required=True)
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department_id', 
                                    store=True, readonly=False)
    allow_approve = fields.Boolean(string="Allow Approve", copy=False, compute="_compute_allow_users")
    check_products = fields.Boolean(string="Chick Purchased", copy=False, compute="_compute_check_products")
    ref = fields.Char(string="Reference", copy=False, tracking=True)
    date = fields.Datetime(string="Date", copy=False, default=datetime.today())
    notes = fields.Text(string="Notes", copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    is_it = fields.Boolean(string="IT", copy=False)
    pr_product = fields.Boolean(string="PR Product", copy=False, default=True)

    state = fields.Selection([
        ("draft", "Draft"),
        ("to_approve", "To be approved"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("done", "Done"),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, digits="Account",
                                     compute='_amount_all')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, digits="Account", compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, digits="Account", compute='_amount_all')
    line_ids = fields.One2many("purchase.request.line", "purchase_request_id", "Lines", copy=True)
    deadline_date = fields.Date(string="Deadline Date", copy=False, tracking=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High')], string='Priority', index=True, tracking=True, copy=False, )
    action_rule_id = fields.Many2one('user.action.rule', string='Action Rule', copy=False)
    manager_ids = fields.Many2many('res.users', string='Managers', copy=False, )
    apply_approval_it = fields.Boolean("Apply Approval IT", copy=False)
    purchase_order_count = fields.Integer(string="Purchase Order Count", compute="_compute_purchase_order_count")

    def _compute_allow_users(self):
        for request in self:
            allow_approve = True
            action_rule = self.action_rule_id

            if action_rule:
                action_rule_line = action_rule.get_action_rule_line("purchase.request", request)
                if action_rule_line:
                    allow_approve = action_rule_line.check_access("Approved", request.id)

            request.allow_approve = allow_approve

    def _compute_check_products(self):
        for request in self:
            check_products = False
            if request.state == "approved":
                lines = request.line_ids.filtered(lambda l: not l.purchase_order_line and not l.display_type)
                if lines:
                    check_products = True

            request.check_products = check_products

    @api.depends('request_by')
    def _compute_department_id(self):
        for request in self:
            if request.request_by and request.request_by.employee_ids:
                # Get the first employee record for the user
                employee = request.request_by.employee_ids[0]
                request.department_id = employee.department_id
            else:
                request.department_id = False

    def _compute_purchase_order_count(self):
        for purchase_request in self:
            purchase_request.purchase_order_count = len(purchase_request.mapped("line_ids.purchase_order_line.order_id"))

    @api.onchange('is_it')
    def _onchange_is_it(self):
        if self.is_it == True:
            self.pr_product = False
        else:
            self.pr_product = True
        self.line_ids = False

    @api.onchange('pr_product')
    def _onchange_pr_product(self):
        self.line_ids = False

    def add_follower_id(self, partner_id):
        default_subtypes, _, _ = self.env['mail.message.subtype'].default_subtypes('purchase.request')

        vals = {
            'res_id': self.id,
            'res_model': 'purchase.request',
            'partner_id': partner_id.id,
            'subtype_ids': [(6, 0, default_subtypes.ids)]
        }

        follower_id = self.env['mail.followers'].create(vals)

        return follower_id

    @api.depends('line_ids.price_total')
    def _amount_all(self):
        for purchase_request in self:
            amount_untaxed = amount_tax = 0.0

            for line in purchase_request.line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            purchase_request.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.model
    def create(self, vals):
        res = super(PurchaseRequest, self).create(vals)
        res.get_user_action_rule()
        return res

    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)

        # update approval if change is it
        if 'is_it' in vals.keys():
            for purchase_request in self:
                purchase_request.get_user_action_rule()

        return res

    def get_user_action_rule(self, apply_it=False):
        action_rule = self.create_uid.action_rule_id
        approval_it = False

        if self.is_it:
            approval_it_id = self.env["ir.config_parameter"].sudo().get_param("purchase_request.approval_it_id", False)
            approval_it_id = approval_it_id and eval(approval_it_id) or approval_it_id

            if approval_it_id:
                approval_it = self.sudo().env["user.action.rule"].search([("id", "=", approval_it_id)])

        if apply_it:
            return self.write({"action_rule_id": approval_it_id, "apply_approval_it": True})

        # get managers of approval it if apply
        manager_ids = []
        if approval_it:
            approval_it_line = approval_it.get_action_rule_line("purchase.request", self)

            if approval_it_line:
                manager_ids = approval_it_line.manager_ids.ids

        if action_rule:
            action_rule_line = action_rule.get_action_rule_line("purchase.request", self)

            if action_rule_line:
                manager_ids += action_rule_line.manager_ids.ids

        vals = {"manager_ids": [(6, 0, manager_ids)], "action_rule_id": False}
        if action_rule:
            vals.update({"action_rule_id": action_rule.id, "apply_approval_it": False})
        elif self.is_it:
            vals.update({"action_rule_id": approval_it.id, "apply_approval_it": True})

        self.write(vals)

        return True

    def action_reset_to_draft(self):
        for purchase_request in self:
            if purchase_request.state not in ["to_approve", "rejected"]:
                continue
            purchase_request.state = "draft"
        return True

    @api.model
    def action_deadline_date(self):
        purchase_requests = self.search([("state", "!=", "done"), ("deadline_date", "<", date.today())])
        for request in purchase_requests:
            request.request_by.partner_id.message_post(subject="Validation Date",
                                                       body='Yor Request Was Expired "%s" ' % (request.deadline_date),
                                                       partner_ids=[request.request_by.partner_id.id])

    def action_to_approve(self):
        for purchase_request in self:
            if purchase_request.state != "draft":
                continue
            if not self.line_ids:
                raise ValidationError(_("Please create some Products"))

            purchase_request.write({"state": "to_approve"})
        return True

    def action_approve(self):
        object = self.sudo().env["ir.model"].search([("model", "=", "purchase.request")])
        current_user = self.env.user
        action_rule_history = self.sudo().env["user.action.rule.history"]
        for purchase_request in self:
            if purchase_request.state != "to_approve":
                continue
            if not self.line_ids:
                raise ValidationError(_("Please create some products"))

            action_rule = self.action_rule_id

            if action_rule:
                action_rule_line = action_rule.get_action_rule_line("purchase.request", purchase_request)

                if action_rule_line:
                    if not action_rule_line.check_access("Approved", purchase_request.id):
                        continue
                    # create action rule history
                    vals = {
                        "record_id": purchase_request.id,
                        "action": "Approved",
                        "object_id": object.id,
                        "manager_id": current_user.id,
                        "action_rule_line_id": action_rule_line.id
                    }
                    action_rule_history.create(vals)
                    # get partners of rule line
                    partners = []
                    for manager in action_rule_line.manager_ids:
                        if current_user.id != manager.id:
                            partners.append(manager.partner_id.id)
                    # send message for managers
                    msg = _('User %s, approve purchase request') % (current_user.name)
                    purchase_request.message_post(partner_ids=partners, body=msg,
                                                  subtype_xmlid='mail.mt_comment')
                    if not action_rule_line.check_action_object("Approved", purchase_request.id):
                        continue
                    elif purchase_request.is_it and not purchase_request.apply_approval_it:
                        purchase_request.get_user_action_rule(True)
                        if purchase_request.action_rule_id:
                            continue

            purchase_request.write(
                {"state": "approved", "name": self.env['ir.sequence'].next_by_code('purchase.request')})
        return True

    def action_create_rfq(self):
        if not self.check_products:
            return
        lines = self.line_ids.filtered(lambda l: not l.purchase_order_line and not l.display_type)
        return lines.action_create_purchase_order()

    def action_create_purchase_order(self):
        if not self.check_products:
            return
        lines = self.line_ids.filtered(lambda l: not l.purchase_order_line and not l.display_type)
        return lines.action_create_purchase_order(True)

    def action_done(self):
        for purchase_request in self:
            if purchase_request.state != "approved":
                continue
            lines = self.line_ids.filtered(lambda l: not l.purchase_order_line and not l.display_type)
            if lines:
                raise ValidationError(_("Some products did not have purchase order"))
            purchase_request.state = "done"
        return True

    def unlink(self):
        for purchase_request in self:
            if purchase_request.state != "draft":
                raise ValidationError(_("Only draft purchase request can be delete"))

        return super(PurchaseRequest, self).unlink()

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return self.env.ref('purchase_request.mt_purchase_request_reset_draft')
        elif 'state' in init_values and self.state == 'to_approve':
            return self.env.ref('purchase_request.mt_purchase_request_to_be_approved')
        elif 'state' in init_values and self.state == 'approved':
            return self.env.ref('purchase_request.mt_purchase_request_approved')
        elif 'state' in init_values and self.state == 'rejected':
            return self.env.ref('purchase_request.mt_purchase_request_rejected')
        elif 'state' in init_values and self.state == 'done':
            return self.env.ref('purchase_request.mt_purchase_request_done')

        return super(PurchaseRequest, self)._track_subtype(init_values)

    def get_purchase_orders(self):
        action = self.sudo().env.ref("purchase.purchase_form_action")
        result = action.read()[0]
        result["domain"] = [("id", "in", self.mapped("line_ids.purchase_order_line.order_id").ids)]

        return result


class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purcha se Request Line"
    _order = 'purchase_request_id, sequence, id'

    name = fields.Text(string='Description', required=True, index=True)
    sequence = fields.Integer(string='Sequence', default=10, )
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',
                             domain="[('category_id', '=', product_uom_category_id)]")
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True,
                               default=1.0)
    date = fields.Datetime(string='Date', index=True, default=datetime.today())
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])
    product_id = fields.Many2one('product.product', string='Product', check_company=True,
                                 domain="[('purchase_ok', '=', True), '|', ('company_id', '=', False),('company_id', '=', company_id)]",
                                 )
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    price_subtotal = fields.Monetary(related='purchase_order_line.price_subtotal', string='Subtotal', store=True,
                                     readonly=True)
    price_total = fields.Monetary(related='purchase_order_line.price_total', string='Total', store=True, readonly=True)
    # In Odoo 18, purchase.order.line.price_tax type may differ; avoid a mismatched related field
    # Compute tax amount from total and subtotal to ensure consistent Monetary type
    price_tax = fields.Monetary(
        compute='_compute_price_tax',
        string='Tax',
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request', index=True, required=True,
                                          ondelete='cascade')
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        store=True,
        string='Analytic Account',
        check_company=True,
    )
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        store=True,
        string='Analytic Tags',
        check_company=True,
    )
    company_id = fields.Many2one('res.company', related='purchase_request_id.company_id', string='Company', store=True,
                                 readonly=True)
    currency_id = fields.Many2one(related='purchase_request_id.currency_id', store=True, string='Currency',
                                  readonly=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.", )
    request_by = fields.Many2one(related="purchase_request_id.request_by", string="Request By", store=True)
    state = fields.Selection(related="purchase_request_id.state", string='Status', readonly=True, index=True,
                             default='draft', tracking=True, store=True)

    purchase_order_line = fields.Many2one("purchase.order.line", string="Purchase Order Line", copy=False)
    vendor_id = fields.Many2one(related="purchase_order_line.partner_id", string="Vendor", store=True, readonly=True)

    @api.depends('price_total', 'price_subtotal')
    def _compute_price_tax(self):
        for line in self:
            total = line.price_total or 0.0
            subtotal = line.price_subtotal or 0.0
            line.price_tax = total - subtotal

    @api.onchange('product_id')
    def onchange_product(self):
        product = self.product_id

        # get description from product
        self.name = product.display_name
        if product.description_purchase:
            self.name += '\n' + product.description_purchase

        # self.price_unit = product.standard_price
        self.price_unit = 0.0

        self.uom_id = product.uom_po_id or product.uom_id

        if product.supplier_taxes_id:
            self.taxes_id = [(4, tax.id) for tax in product.supplier_taxes_id]
        domain = []
        if self.purchase_request_id.is_it:
            domain += [('categ_id.is_it', '=', True)]
            if self.product_id and not self.product_id.categ_id.is_it:
                self.product_id = False
        if self.purchase_request_id.pr_product:
            domain += [('categ_id.pr_product', '=', True)]
            if self.product_id and not self.product_id.categ_id.pr_product:
                self.product_id = False

        return {'domain': {'product_id': domain}}

    @api.onchange('product_id', 'date')
    def onchange_analytic_id_and_tag_ids(self):
        for rec in self:
            default_analytic_account = rec.env['account.analytic.default'].sudo().account_get(
                product_id=rec.product_id.id,
                date=rec.purchase_request_id.date,
                company_id=rec.company_id.id,
            )
            rec.account_analytic_id = rec.account_analytic_id or default_analytic_account.analytic_id
            rec.analytic_tag_ids = rec.analytic_tag_ids or default_analytic_account.analytic_tag_ids

    def action_create_purchase_order(self, create_purchase_order=False):
        # request for question or purchase order
        action = self.sudo().env.ref("purchase_request.action_create_purchase_request_quotation_wizard")
        result = action.read()[0]
        lines = []
        for line in self:
            vals = {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'price_unit': line.price_unit,
                'uom_id': line.uom_id.id,
                'purchase_request_line': line.id,
            }
            lines.append((0, 0, vals))
        result["context"] = {"default_lines": lines,
                             "create_purchase_order": create_purchase_order}

        return result
