# -*- coding: utf-8 -*-

from lxml import etree
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare


class PettyCash(models.Model):
    _name = "petty.cash"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Petty Cash"

    def _get_domain_responsible(self):
        domain = []

        if self.env.user.has_group('petty_cash.group_petty_cash_responsible_box'):
            user_rules = self.env['petty.cash.user.rule'].search([])
            users = set()

            for user_rule in user_rules:
                users.add(user_rule.user.id)

            domain = [('id', 'in', list(users))]

        return domain

    name = fields.Char(string='Name', required=True, readonly=True, copy=False, default="/")
    reference = fields.Char("Reference")
    start_date = fields.Date("Start Date", default=fields.Date.today, required=True, readonly=True, copy=False)
    close_date = fields.Date("Close Date", copy=False)
    journal_id = fields.Many2one('account.journal', string="Journal", required=True)
    account_id = fields.Many2one('account.account', string="Account", required=True)
    user_rule = fields.Many2one('petty.cash.user.rule', string="User Rule", required=True)
    responsible_id = fields.Many2one('res.users', string='Responsible', required=True, readonly=True,
                                     domain=_get_domain_responsible)
    balance = fields.Float("Opening Balance", copy=False)
    last_balance = fields.Monetary(string="Last Balance", copy=False)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, readonly=True, compute='_compute_amount')
    amount_tax = fields.Monetary(string="Tax", store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string="Total", store=True, readonly=True, compute='_compute_amount')
    net_balance = fields.Monetary(string="Net Balance", store=True, readonly=True, compute='_compute_amount')
    note = fields.Text("Note")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in progress', 'In Progress'),
        ('review', 'Review'),
        ('closed', 'Closed')
    ], string='Status', index=True, readonly=True, default='draft', copy=False, track_visibility='onchange')
    template_type = fields.Selection([
        ('with product', 'With Product'),
        ('without product', 'without product'),
    ], string='Template Type', required=True)
    dynamic_journal = fields.Boolean("Dynamic Journal", copy=False)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', domain="[('code','=','incoming')]",
                                      help="This will determine operation type of incoming shipment")
    petty_cash_line_ids = fields.One2many('petty.cash.line', 'petty_cash_id', string='Petty Cash Lines')
    petty_cash_line_ids2 = fields.One2many('petty.cash.line', 'petty_cash_id', string='Petty Cash Lines')
    transfers = fields.One2many('petty.cash.transfer', 'petty_cash_id', 'Petty Cash Transfers')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, copy=False,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, copy=False,
                                 default=lambda self: self.env.user.company_id.id)
    move_id = fields.Many2one('account.move', string='Journal Entry', copy=False)
    picking_count = fields.Integer(compute='_compute_picking', string='Receptions')
    picking_ids = fields.One2many('stock.picking', 'petty_cash_id', string='Receptions')
    partner_ids = fields.Many2many('res.partner', compute='_compute_partner_ids', string="Partners", store=True,
                                   readonly=True)
    move_ids = fields.One2many('account.move', 'petty_cash_id', string='Journal Entries', copy=False)
    moves_count = fields.Integer(compute='_compute_journal_entry_count', string='Journal Entry Count')

    # dynamic journal items
    dynamic_move_id = fields.Many2one('account.move', string='Dynamic Journal Entry')
    dynamic_move_line_ids = fields.One2many('account.move.line', 'petty_cash_id', string='Dynamic Journal Items',
                                            copy=False)

    def add_follower_id(self, res_id, partner_id):
        default_subtypes, _, _ = self.env['mail.message.subtype'].default_subtypes('petty.cash')

        vals = {
            'res_id': res_id,
            'res_model': 'petty.cash',
            'partner_id': partner_id.id,
            'subtype_ids': [(6, 0, default_subtypes.ids)]
        }

        follower_id = self.env['mail.followers'].create(vals)

        return follower_id

    @api.depends('petty_cash_line_ids2.amount_untaxed', 'petty_cash_line_ids2.amount_tax',
                 'petty_cash_line_ids.amount_untaxed', 'petty_cash_line_ids.amount_tax', 'last_balance')
    def _compute_amount(self):
        for petty_cash in self:
            amount_untaxed = 0
            amount_tax = 0
            lines = petty_cash.petty_cash_line_ids
            if petty_cash.template_type == 'with product':
                lines = petty_cash.petty_cash_line_ids2
            for line in lines:
                amount_untaxed += line.amount_untaxed
                amount_tax += line.amount_tax

            petty_cash.amount_untaxed = amount_untaxed
            petty_cash.amount_tax = amount_tax
            petty_cash.amount_total = petty_cash.amount_untaxed + petty_cash.amount_tax
            petty_cash.net_balance = petty_cash.last_balance - petty_cash.amount_total

    def _compute_picking(self):
        for petty_cash in self:
            petty_cash.picking_count = len(petty_cash.picking_ids)

    def _compute_journal_entry_count(self):
        for petty_cash in self:
            petty_cash.moves_count = len(petty_cash.move_ids)

    @api.depends('petty_cash_line_ids2.partner_id', 'petty_cash_line_ids.partner_id')
    def _compute_partner_ids(self):
        for petty_cash in self:
            lines = petty_cash.petty_cash_line_ids
            if petty_cash.template_type == 'with product':
                lines = petty_cash.petty_cash_line_ids2

            partners = lines.mapped('partner_id')
            petty_cash.partner_ids = partners.ids

    @api.onchange('user_rule', 'responsible_id')
    def onchange_user_rule(self):
        account_move_lines = self.env['account.move.line'].search(
            [('journal_id', '=', self.user_rule.journal_id.id), ('account_id', '=', self.user_rule.account_id.id)])

        balance = 0
        for line in account_move_lines:
            balance += line.debit - line.credit

        self.journal_id = self.user_rule.journal_id.id
        self.account_id = self.user_rule.account_id.id
        self.balance = balance
        self.last_balance = balance

    @api.onchange('responsible_id')
    def onchange_responsible(self):
        domain = [('user', '=', self.responsible_id.id)]
        user_rule = self.env['petty.cash.user.rule'].search(domain, limit=1)
        self.user_rule = user_rule.id

        return {'domain': {'user_rule': domain}}

    def action_open(self):
        for petty_cash in self:
            if petty_cash.state != 'draft':
                continue

            name = self.env['ir.sequence'].next_by_code('petty.cash')
            vals = {'name': name, 'state': 'in progress'}

            # create dynamic journal entry
            if petty_cash.dynamic_journal:
                reference_move = name
                if petty_cash.reference:
                    reference_move += '/' + petty_cash.reference

                move_vals = petty_cash._prepare_journal_entry(reference_move)
                move = self.env['account.move'].with_context(force_petty_cash=True).create(move_vals)
                vals.update({'dynamic_move_id': move.id, 'move_ids': [(4, move.id)]})

            petty_cash.write(vals)
        return True

    def action_close(self):
        account_move_line = self.env['account.move.line']
        for petty_cash in self:
            if petty_cash.state != 'in progress':
                continue

            if not petty_cash.petty_cash_line_ids:
                raise ValidationError(_("Please create some Petty Cash lines"))

            account_move_lines = account_move_line.search(
                [('journal_id', '=', petty_cash.journal_id.id), ('account_id', '=', petty_cash.account_id.id)])

            last_balance = 0
            for line in account_move_lines:
                last_balance += line.debit - line.credit

            date_today = fields.Date.context_today(self)

            petty_cash.write({'state': 'review', 'close_date': date_today, 'last_balance': last_balance})
        return True

    def action_post(self):
        # can be create stock move or not
        is_stock_move = self.env["ir.config_parameter"].get_param('is_stock_move')

        for petty_cash in self:
            if petty_cash.state == 'closed':
                continue

            if not petty_cash.petty_cash_line_ids:
                raise ValidationError(_("Please create some Petty Cash lines"))

            if petty_cash.template_type == 'with product' and is_stock_move:
                if not petty_cash.picking_type_id.default_location_dest_id:
                    raise ValidationError(
                        _("You must set Destination Location for this Operation Type"))

                if not petty_cash.picking_type_id.default_location_src_id:
                    raise ValidationError(
                        _("You must set Source Location for this Operation Type"))

                for line in petty_cash.petty_cash_line_ids:
                    if line.product_id.type != 'service':
                        # add supplier to product if there is partner
                        if line.partner_id:
                            petty_cash._add_supplier_to_product(line)

                        # create stock picking
                        picking = petty_cash._create_picking(line)

                        # create stock move
                        petty_cash._create_stock_moves(picking, line)

            if petty_cash.dynamic_journal:
                petty_cash.dynamic_move_id.with_context(force_petty_cash=True).action_post()
            else:
                petty_cash._create_journal_entry()

            petty_cash.write({'state': 'closed'})

        return True

    def _create_journal_entry(self):
        move_lines = []

        reference_move = self.name
        if self.reference:
            reference_move += '/' + self.reference

        for line in self.petty_cash_line_ids:
            move_lines += line._create_update_journal_items()

        # create Journal item total amount
        vals = self._prepare_journal_item(reference_move)

        move_lines.append([0, 0, vals])

        # create Journal Entry
        vals = self._prepare_journal_entry(reference_move, move_lines)
        move = self.env['account.move'].with_context(force_petty_cash=True).create(vals)
        move.with_context(force_petty_cash=True).action_post()

        return move

    @api.model
    def _prepare_journal_item(self, reference_move):
        vals = {
            'account_id': self.account_id.id,
            'name': reference_move,
            'credit': self.amount_total,
            'currency_id': self.company_id.currency_id.id,
            'date_maturity': self.close_date,
            'petty_cash_id': self.id
        }

        return vals

    @api.model
    def _prepare_journal_entry(self, reference_move, move_lines=False):
        vals = {
            'date': self.start_date,
            'ref': reference_move,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'narration': self.note,
            'line_ids': move_lines,
            'petty_cash_id': self.id,
        }
        return vals

    @api.model
    def _create_picking(self, line):
        stock_picking = self.env['stock.picking']
        vals = {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': line.partner_id and line.partner_id.id or False,
            'date': self.start_date,
            'origin': self.name,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'location_id': self.picking_type_id.default_location_src_id.id,
            'company_id': self.company_id.id,
            'petty_cash_id': self.id,
        }
        picking = stock_picking.create(vals)

        return picking

    def _create_stock_moves(self, picking, line):
        stock_moves = self.env['stock.move']
        config_parameters = self.env["ir.config_parameter"].sudo()

        line_name = line.description
        if line.reference:
            line_name += '/' + line.reference

        vals_stock_move = {
            'name': line_name,
            'product_id': line.product_id.id,
            'product_uom': line.uom_id.id,
            'date': self.start_date,
            'date_expected': line.date,
            'location_id': self.picking_type_id.default_location_src_id.id,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'picking_id': picking.id,
            'state': 'draft',
            'company_id': self.company_id.id,
            'price_unit': line.price_unit,
            'picking_type_id': self.picking_type_id.id,
            'origin': self.name,
            'route_ids': self.picking_type_id.warehouse_id and [
                (6, 0, [x.id for x in self.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.picking_type_id.warehouse_id.id,
        }

        if float_compare(line.quantity, 0.0, precision_rounding=line.uom_id.rounding) > 0:
            quant_uom = line.product_id.uom_id
            propagate_uom = config_parameters.get_param('stock.propagate_uom')

            if line.uom_id.id != quant_uom.id and propagate_uom != '1':
                product_qty = line.uom_id._compute_quantity(line.quantity, quant_uom,
                                                            rounding_method='HALF-UP')
                vals_stock_move['product_uom'] = quant_uom.id
                vals_stock_move['product_uom_qty'] = product_qty
            else:
                vals_stock_move['product_uom_qty'] = line.quantity

        stock_move = stock_moves.create(vals_stock_move)
        stock_move = stock_move._action_confirm()
        stock_move.sequence = 5
        stock_move._action_assign()

        return True

    def _add_supplier_to_product(self, line):
        partner = line.partner_id if not line.partner_id.parent_id else line.partner_id.parent_id
        if partner not in line.product_id.seller_ids.mapped('name') and len(line.product_id.seller_ids) <= 10:
            currency = self.env.user.company_id.currency_id

            supplierinfo = {
                'name': partner.id,
                'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
                'product_uom': line.uom_id.id,
                'min_qty': 0.0,
                'price': self.currency_id.compute(line.price_unit, currency, round=False),
                'currency_id': currency.id,
                'delay': 0,
            }

            vals = {
                'seller_ids': [(0, 0, supplierinfo)],
            }
            line.product_id.write(vals)

    @api.model
    def create(self, vals):
        res = super(PettyCash, self).create(vals)

        # add all admin in followers
        users = self.env['res.users'].search([('id', '!=', self.env.user.id)])

        for user in users:
            if user.has_group('base.group_system'):
                self.add_follower_id(res.id, user.partner_id)
        return res

    def write(self, vals):
        for petty_cash in self:
            if petty_cash.template_type == 'with product' and 'petty_cash_line_ids2' in vals.keys():
                vals.update({'petty_cash_line_ids': vals['petty_cash_line_ids2'], 'petty_cash_line_ids2': []})

        res = super(PettyCash, self).write(vals)

        # recompute journal entry in dynamic journal if update  start_date or reference or currency or note
        for petty_cash in self:
            if petty_cash.state != 'closed' and petty_cash.dynamic_journal:
                reference_move = petty_cash.name
                if petty_cash.reference:
                    reference_move += '/' + petty_cash.reference

                vals_dynamic_move = {
                    'date': petty_cash.start_date,
                    'ref': reference_move,
                    'currency_id': petty_cash.currency_id.id,
                    'narration': petty_cash.note
                }

                if petty_cash.petty_cash_line_ids:
                    # delete journal item total amount if not found petty cash lines
                    aml_credit = petty_cash.mapped('dynamic_move_line_ids').filtered(lambda l: l.credit > 0)
                    if aml_credit:
                        aml_credit.with_context(force_petty_cash=True).write(
                            {'name': reference_move, 'date_maturity': petty_cash.close_date})

                    if petty_cash.petty_cash_line_ids and (
                            'petty_cash_line_ids2' in vals.keys() or 'petty_cash_line_ids' in vals.keys()):
                        move_lines = petty_cash.petty_cash_line_ids._recompute_dynamic_lines()

                        if aml_credit:
                            move_lines.append([1, aml_credit.id, {"credit": petty_cash.amount_total}])
                        else:
                            vals_aml_credit = petty_cash._prepare_journal_item(reference_move)
                            move_lines.append([0, 0, vals_aml_credit])

                        vals_dynamic_move.update({'line_ids': move_lines})

                        # journal items for petty cash lines that delete
                        delete_aml = petty_cash.mapped('dynamic_move_line_ids').filtered(
                            lambda l: l.debit > 0 and not l.petty_cash_line)

                        for line in delete_aml:
                            move_lines.append([3, line.id])
                elif petty_cash.mapped('dynamic_move_line_ids'):
                    vals_dynamic_move.update({'line_ids': False})

                petty_cash.dynamic_move_id.with_context(force_petty_cash=True).write(vals_dynamic_move)
        return res

    def unlink(self):
        for petty_cash in self:
            if petty_cash.state == 'closed':
                raise UserError(_('You cannot delete petty cash which is closed'))
        return super(PettyCash, self).unlink()

    @api.model
    def default_get(self, default_fields):
        # get template type petty cash line
        config_parameters = self.env["ir.config_parameter"].sudo()
        template_type = config_parameters.get_param('template_type')

        # get picking_type_id
        picking_type_id = config_parameters.get_param('picking_type_id', False)

        # get dynamic journal
        dynamic_journal = config_parameters.get_param('petty_cash.dynamic_journal')

        contextual_self = self.with_context(default_responsible_id=self.env.user.id,
                                            default_template_type=template_type,
                                            default_dynamic_journal=dynamic_journal,
                                            default_picking_type_id=picking_type_id and eval(picking_type_id) or False)
        return super(PettyCash, contextual_self).default_get(default_fields)

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(PettyCash, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)

        if view_type == 'form':
            doc = etree.XML(res['arch'])

            # can be create stock move or not
            is_stock_move = self.env["ir.config_parameter"].get_param('is_stock_move')

            if not is_stock_move:
                for node in doc.xpath("//field[@name='picking_type_id']"):
                    node.set('invisible', "1")

            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'in progress':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_in_progress')
        elif 'state' in init_values and self.state == 'review':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_review')
        elif 'state' in init_values and self.state == 'closed':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_close')
        return super(PettyCash, self)._track_subtype(init_values)

    def open_journal_entries(self):
        action = self.sudo().env.ref('account.action_move_journal_line', False)
        result = action.read()[0]
        result['context'] = {'view_no_maturity': True}
        result['domain'] = [('id', '=', self.move_ids.ids)]

        return result

    def action_view_picking(self):
        action = self.sudo().env.ref('stock.action_picking_tree_all')
        result = action.read()[0]

        result['context'] = {}
        result['domain'] = [('id', 'in', self.picking_ids.ids)]

        return result


class PettyCashLine(models.Model):
    _name = "petty.cash.line"
    _description = "Petty Cash Line"

    def _get_domain_product(self):
        domain = []
        if self.petty_cash_id.template_type == 'with product':

            if self.env.user.has_group('petty_cash.group_petty_cash_manager'):
                products = eval(self.env["ir.config_parameter"].sudo().get_param('products', '[]'))
            else:
                user_rules = self.env['petty.cash.user.rule'].search([('user', '=', self.env.user.id)])
                products = set()

                for user_rule in user_rules:
                    products.update(user_rule.products.ids)

            domain = [('id', 'in', list(products))]
        return domain

    def _get_domain_account(self):
        if self.env.user.has_group('petty_cash.group_petty_cash_manager'):
            accounts = eval(self.env["ir.config_parameter"].sudo().get_param('accounts', '[]'))
        else:
            user_rules = self.env['petty.cash.user.rule'].search([('user', '=', self.env.user.id)])
            accounts = set()

            for user_rule in user_rules:
                accounts.update(user_rule.accounts.ids)

        domain = [('id', 'in', list(accounts))]
        return domain

    def _get_domain_analytic_account(self):
        if self.env.user.has_group('petty_cash.group_petty_cash_manager'):
            analytic_account_ids = eval(self.env["ir.config_parameter"].sudo().get_param('analytic_account_ids', '[]'))
        else:
            user_rules = self.env['petty.cash.user.rule'].search([('user', '=', self.env.user.id)])
            analytic_account_ids = set()

            for user_rule in user_rules:
                analytic_account_ids.update(user_rule.analytic_account_ids.ids)

        domain = [('id', 'in', list(analytic_account_ids))]
        return domain

    def _get_domain_partner(self):
        if self.env.user.has_group('petty_cash.group_petty_cash_manager'):
            partner_ids = eval(self.env["ir.config_parameter"].sudo().get_param('petty_cash.partner_ids', '[]'))
        else:
            user_rules = self.env['petty.cash.user.rule'].search([('user', '=', self.env.user.id)])
            partner_ids = set()

            for user_rule in user_rules:
                partner_ids.update(user_rule.partner_ids.ids)

        domain = [('id', 'in', list(partner_ids))]

        return domain

    @api.depends('tax_ids', 'product_id', 'price_unit', 'quantity', 'discount', 'discount_type', 'amount_currency',
                 'currency_id')
    def _compute_amount(self):
        for line in self:
            price_unit = line.price_unit
            quantity = line.quantity
            petty_cash_currency = line.petty_cash_id.currency_id
            amount_discount = 0

            if line.discount_type and line.discount != 0:
                amount_discount = line.discount_type == "percentage" and (
                        price_unit * line.discount / 100) or line.discount
                price_unit -= amount_discount

            taxes = line.tax_ids.compute_all(price_unit, petty_cash_currency, quantity, product=line.product_id,
                                             partner=line.partner_id)
            amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            amount_untaxed = taxes['total_excluded']
            amount_currency = 0
            amount_untaxed_currency = 0

            if line.currency_id and line.currency_id != petty_cash_currency:
                amount_untaxed_currency = amount_untaxed
                amount_untaxed = line.currency_id._convert(amount_untaxed, petty_cash_currency,
                                                           line.petty_cash_id.company_id, line.date)
                amount_discount = line.currency_id._convert(amount_discount, petty_cash_currency,
                                                            line.petty_cash_id.company_id, line.date)

                if line.amount_currency != 0 and line.amount_currency != amount_untaxed:
                    amount_currency = line.amount_currency
                    amount_untaxed = line.amount_currency

                    # recompute amount tax with amount currency
                    taxes = line.tax_ids.compute_all(amount_currency, petty_cash_currency, product=line.product_id,
                                                     partner=line.partner_id)
                    amount_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))

                else:
                    amount_tax = line.currency_id._convert(amount_tax, petty_cash_currency,
                                                           line.petty_cash_id.company_id, line.date)
                    amount_currency = amount_untaxed

            line.amount_untaxed = amount_untaxed
            line.amount_currency = amount_currency
            line.amount_untaxed_currency = amount_untaxed_currency
            line.amount_tax = amount_tax
            line.amount_discount = amount_discount * quantity

    @api.depends('amount_untaxed', 'amount_tax')
    def _compute_amount_total(self):
        for line in self:
            line.amount_total = line.amount_untaxed + line.amount_tax

    reference = fields.Char("Reference")
    type = fields.Selection([
        ("expenses", "Expenses"),
        ("payment", "Payment")], string="Type", required=True, default="expenses", copy=False)
    description = fields.Char("Description", required=True)
    date = fields.Date("Date", required=True, default=fields.Date.today)
    account_id = fields.Many2one('account.account', string="Account", required=True, domain=_get_domain_account)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic account',
                                          domain=_get_domain_analytic_account)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    amount_untaxed = fields.Monetary(string='Subtotal', store=True, readonly=True, compute=_compute_amount,
                                     help="Total amount and without taxes", currency_field='petty_cash_currency_id')
    amount_untaxed_currency = fields.Monetary(string='Subtotal', store=True, readonly=True, compute=_compute_amount,
                                              help="Total amount without taxes with currency of line")
    amount_discount = fields.Monetary(string="Amount Discount", store=True, readonly=True, compute=_compute_amount,
                                      currency_field='petty_cash_currency_id')
    amount_tax = fields.Monetary(string='Amount Tax', store=True, readonly=True, compute=_compute_amount,
                                 help="Total amount and with taxes", currency_field='petty_cash_currency_id')
    amount_total = fields.Monetary(string="Total", store=True, readonly=True, compute='_compute_amount_total',
                                   currency_field='petty_cash_currency_id')
    product_id = fields.Many2one('product.product', string='product', domain=_get_domain_product)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',
                             domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'), required=True)
    discount_type = fields.Selection([
        ("percentage", "Percentage"),
        ("fixed", "Fixed")], string="Discount Type", default="percentage", copy=False)
    discount = fields.Float(string='Discount', digits=dp.get_precision('Discount'), default=0.0)
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), default=1)
    tax_ids = fields.Many2many('account.tax', string='Taxes',
                               domain=[('type_tax_use', '=', 'purchase'), '|', ('active', '=', False),
                                       ('active', '=', True)])

    petty_cash_id = fields.Many2one('petty.cash', string='Petty Cash', required=True, ondelete='cascade')
    responsible_id = fields.Many2one('res.users', related='petty_cash_id.responsible_id', string='Responsible',
                                     store=True, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict', domain=_get_domain_partner)
    vat_partner = fields.Char(string='TIN', help="Tax Identification Number. "
                                                 "Fill it if the company is subjected to taxes. "
                                                 "Used by the some of the legal statements.", related='partner_id.vat',
                              store=True, readonly=True, related_sudo=False)
    file = fields.Binary(string='Attachment')
    file_name = fields.Char("File Name")
    company_id = fields.Many2one('res.company', related='petty_cash_id.company_id', string='Company', store=True,
                                 readonly=True)
    petty_cash_currency_id = fields.Many2one('res.currency', related='petty_cash_id.currency_id', string='Currency',
                                             store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount_currency = fields.Monetary(string='Amount in Currency', currency_field='petty_cash_currency_id', copy=True)
    petty_cash_request_id = fields.Many2one('petty.cash.request', string='Petty Cash Request')
    move_line_ids = fields.One2many('account.move.line', 'petty_cash_line', string='Journal Items', copy=False)
    is_review = fields.Boolean("Review", readonly=True, copy=False)

    @api.onchange('product_id')
    def onchange_product(self):
        product = self.product_id

        # get description from product
        if self.partner_id:
            product_lang = self.product_id.with_context(
                lang=self.partner_id.lang,
                partner_id=self.partner_id.id,
            )

            self.description = product_lang.display_name
            if product_lang.description_purchase:
                self.description += '\n' + product_lang.description_purchase
        else:
            self.description = product.display_name
            if product.description_purchase:
                self.description += '\n' + product.description_purchase

        self.price_unit = product.standard_price
        self.account_id = product.property_account_expense_id or product.categ_id.property_account_expense_categ_id

        self.uom_id = product.uom_po_id or product.uom_id

        if product.supplier_taxes_id:
            self.tax_ids = [(4, tax.id) for tax in product.supplier_taxes_id]

    @api.onchange("type")
    def onchange_type(self):
        if self.petty_cash_id.template_type != 'with product':
            domain = self._get_domain_account()
            if self.type == "payment":
                domain += [("account_type", "=", "liability_payable"), ("deprecated", "=", False)]

                if self.account_id and (self.account_id.account_type != "liability_payable" or self.account_id.deprecated):
                    self.account_id = False

            return {"domain": {"account_id": domain}}

    @api.onchange("account_id")
    def onchange_account(self):
        if self.petty_cash_id.template_type != 'with product':
            if self.type == "payment":
                domain = self._get_domain_account() + [("account_type", "=", "liability_payable"), ("deprecated", "=", False)]
                if self.account_id and (self.account_id.account_type != "liability_payable" or self.account_id.deprecated):
                    self.account_id = False

                return {"domain": {"account_id": domain}}

    def unlink(self):
        for line in self:
            if line.petty_cash_id.state == 'closed':
                raise UserError(_('You cannot delete petty cash line which is closed'))

        return super(PettyCashLine, self).unlink()

    def _recompute_dynamic_lines(self):
        move_lines = []
        for line in self:
            move_lines += line._create_update_journal_items()

        return move_lines

    def _create_update_journal_items(self):
        # create or update journal item , update in dynamic journal
        move_lines = []
        line_name = self.description
        dynamic_journal = self.petty_cash_id.dynamic_journal
        if self.reference:
            line_name += '/' + self.reference

        vals = self._prepare_journal_item(line_name)
        aml_ids = []
        aml_debit = False
        if dynamic_journal:
            aml_debit = self.mapped('move_line_ids').filtered(lambda l: l.debit > 0 and not l.tax_line_id)

        if aml_debit:
            move_lines.append([1, aml_debit.id, vals])
            aml_ids.append(aml_debit._origin.id)
        else:
            move_lines.append([0, 0, vals])

        # get Journal item  for every tax if exists taxs in line
        if self.tax_ids:
            price_unit = self.price_unit
            quantity = self.quantity
            petty_cash_currency = self.petty_cash_id.currency_id
            with_currency = True

            if self.discount_type and self.discount != 0:
                price_unit -= self.discount_type == "percentage" and (price_unit * self.discount / 100) or self.discount

            taxes = self.tax_ids._origin.compute_all(price_unit, petty_cash_currency, quantity, product=self.product_id,
                                                     partner=self.partner_id)

            if self.currency_id and self.currency_id != petty_cash_currency:
                amount_untaxed_currency = self.currency_id._convert(taxes['total_excluded'], petty_cash_currency,
                                                                    self.petty_cash_id.company_id, self.date)

                if self.amount_currency != 0 and self.amount_currency != amount_untaxed_currency:
                    with_currency = False
                    # recompute amount tax with amount currency
                    taxes = self.tax_ids._origin.compute_all(self.amount_currency, petty_cash_currency,
                                                             product=self.product_id, partner=self.partner_id)

            for tax_vals in taxes.get('taxes', []):
                amount_tax = tax_vals.get('amount', 0.0)
                amount_currency_tax = 0

                if with_currency and self.currency_id and self.currency_id != petty_cash_currency:
                    amount_currency_tax = amount_tax
                    amount_tax = self.currency_id._convert(amount_tax, petty_cash_currency,
                                                           self.petty_cash_id.company_id, self.date)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(
                    tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                if tax.tax_exigibility == 'on_payment':
                    account = tax.cash_basis_transition_account_id
                else:
                    account = tax_repartition_line.account_id

                vals = self._prepare_journal_item_tax(tax, tax_vals, account, amount_tax, amount_currency_tax)
                aml_tax_debit = False

                if dynamic_journal:
                    aml_tax_debit = self.mapped('move_line_ids').filtered(
                        lambda l: l.debit > 0 and l.tax_line_id == tax)

                if aml_tax_debit:
                    move_lines.append([1, aml_tax_debit.id, vals])
                    aml_ids.append(aml_tax_debit._origin.id)
                else:
                    move_lines.append([0, 0, vals])

        if dynamic_journal and self.move_line_ids:
            delete_aml_ids = list(set(self.move_line_ids.ids) - set(aml_ids))
            if delete_aml_ids:
                for aml_id in delete_aml_ids:
                    move_lines.append([3, aml_id])

        return move_lines

    @api.model
    def _prepare_journal_item(self, line_name):
        currency_id = self.company_id.currency_id.id
        debit = self.amount_untaxed
        amount_currency = self.amount_untaxed
        if self.currency_id and self.currency_id != self.petty_cash_id.currency_id:
            currency_id = self.currency_id.id
            debit = self.amount_currency
            amount_currency = self.amount_untaxed_currency

        vals = {
            'name': line_name,
            'quantity': self.quantity if self.petty_cash_id.template_type == 'with product' else 0,
            'product_id': self.product_id and self.product_id.id or False,
            'product_uom_id': self.uom_id and self.uom_id.id or False,
            'account_id': self.account_id.id,
            'partner_id': self.partner_id and self.partner_id.id or False,
            'currency_id': currency_id,
            'amount_currency': amount_currency,
            'debit': debit,
            'date_maturity': self.date,
            'analytic_account_id': self.analytic_account_id and self.analytic_account_id.id or False,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'tax_ids': [(6, 0, self.tax_ids.ids)],
            'petty_cash_line': self.id,
            'petty_cash_id': self.petty_cash_id.id
        }
        return vals

    @api.model
    def _prepare_journal_item_tax(self, tax, tax_vals, account, amount_tax, amount_currency_tax):
        currency_id = self.company_id.currency_id.id
        amount_currency = amount_tax
        if self.currency_id and self.currency_id != self.petty_cash_id.currency_id:
            currency_id = self.currency_id.id
            amount_currency = amount_currency_tax

        vals = {
            'name': tax.name,
            'account_id': account.id,
            'partner_id': self.partner_id and self.partner_id.id or False,
            'currency_id': currency_id,
            'amount_currency': amount_currency,
            'debit': amount_tax,
            'date_maturity': self.date,
            'analytic_account_id': self.analytic_account_id and self.analytic_account_id.id or False,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'tax_ids': [(6, 0, tax_vals['tax_ids'])],
            'tax_tag_ids': [(6, 0, tax_vals['tag_ids'])],
            'tax_repartition_line_id': tax_vals['tax_repartition_line_id'],
            'petty_cash_line': self.id,
            'petty_cash_id': self.petty_cash_id.id
        }

        return vals


class PettyCashTransfer(models.Model):
    _name = "petty.cash.transfer"
    _description = "Petty Cash Transfer"

    description = fields.Text(string="Description")
    manager = fields.Many2one('res.users', string='Manager', required=True)
    petty_cash_id = fields.Many2one('petty.cash', string='Petty Cash', required=True, ondelete='cascade')


class PettyCashUserRule(models.Model):
    _name = 'petty.cash.user.rule'
    _description = 'Petty Cash User Rule'

    def _get_domain_products(self):
        domain = [('purchase_ok', '=', True)]
        products = eval(self.env["ir.config_parameter"].sudo().get_param('products', '[]'))

        if products:
            domain = [('id', 'in', products)]

        return domain

    def _get_domain_accounts(self):
        domain = []
        accounts = eval(self.env["ir.config_parameter"].sudo().get_param('accounts', '[]'))

        if accounts:
            domain = [('id', 'in', accounts)]

        return domain

    def _get_domain_analytic_accounts(self):
        domain = []
        analytic_account_ids = eval(self.env["ir.config_parameter"].sudo().get_param('analytic_account_ids', '[]'))

        if analytic_account_ids:
            domain = [('id', 'in', analytic_account_ids)]

        return domain

    def _get_domain_partners(self):
        domain = []
        partner_ids = eval(self.env["ir.config_parameter"].sudo().get_param('petty_cash.partner_ids', '[]'))

        if partner_ids:
            domain = [('id', 'in', partner_ids)]

        return domain

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True, readonly=True, copy=False, default="/")
    user = fields.Many2one('res.users', string='User', required=True)
    account_id = fields.Many2one('account.account', string="Account", required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)

    # accounts and products and analytic_account_ids and partners petty cash line for every user rule
    accounts = fields.Many2many('account.account', string='Accounts', domain=_get_domain_accounts)
    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic Accounts',
                                            domain=_get_domain_analytic_accounts)
    products = fields.Many2many('product.product', string='Products', domain=_get_domain_products)
    partner_ids = fields.Many2many('res.partner', string='Partners', domain=_get_domain_partners)
    active = fields.Boolean('Active', default=True)

    @api.onchange("products")
    def onchange_products(self):
        accounts = self.accounts.ids

        for product in self.products:
            property_account_expense_id = product.property_account_expense_id
            if property_account_expense_id:
                if property_account_expense_id.id not in accounts:
                    accounts.append(property_account_expense_id.id)
            else:
                property_account_expense_categ_id = product.categ_id.property_account_expense_categ_id
                if property_account_expense_categ_id and property_account_expense_categ_id.id not in accounts:
                    accounts.append(property_account_expense_categ_id.id)
            self.accounts = [(6, 0, accounts)]

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('petty.cash.user.rule')

        return super(PettyCashUserRule, self).create(vals)

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(PettyCashUserRule, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                              submenu=submenu)

        if view_type == 'form':
            doc = etree.XML(res['arch'])

            template_type = self.env["ir.config_parameter"].get_param('template_type')

            if template_type == 'with product':
                for node in doc.xpath("//page[@name='accounts']"):
                    node.set('invisible', "1")
            else:
                for node in doc.xpath("//page[@name='products']"):
                    node.set('invisible', "1")

            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res


class BaseImport(models.TransientModel):
    _inherit = "base_import.import"

    def do(self, fields, columns, options, dryrun=False):
        return super(BaseImport,
                     self.with_context(dryrun=dryrun, import_petty_cash_line=options.get('import_petty_cash_line'))).do(
            fields, columns, options, dryrun)

    @api.model
    def _convert_import_data(self, fields, options):
        data, fields = super(BaseImport, self)._convert_import_data(fields, options)
        if self._context.get('import_petty_cash_line'):
            import_field = options.get('import_field')
            petty_cash_id = options.get('petty_cash_id')

            if import_field and petty_cash_id:
                fields.append(import_field)
                for row in data:
                    row.append(petty_cash_id)

        return data, fields
