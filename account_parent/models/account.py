# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 - 2020 Steigend IT Solutions (Omal Bastin)
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#
##############################################################################
from odoo import api, fields, models
from odoo.osv import expression


# class AccountAccountTemplate(models.Model):
#     _inherit = "account.account.template"

#     parent_id = fields.Many2one('account.account.template', 'Parent Account', ondelete="set null")

#     @api.model
#     def _search(self, domain, offset=0, limit=None, order=None):
#         context = self._context or {}
#         new_domain = []
#         if domain:
#             for arg in domain:
#                 if isinstance(arg, (list, tuple)) and arg[0] == 'name' and isinstance(arg[2], str):
#                     new_domain.append('|')
#                     new_domain.append(arg)
#                     new_domain.append(['code', arg[1], arg[2]])
#                 else:
#                     new_domain.append(arg)
#         if not context.get('show_parent_account', False):
#             new_domain = expression.AND([[('account_type', '!=', 'view')], new_domain])
#         return super()._search(new_domain, offset=offset, limit=limit, order=order)


# class AccountAccountType(models.Model):
#     _inherit = "account.account.type"

#     type = fields.Selection(selection_add=[('view', 'View')], ondelete={'view': 'cascade'})


class AccountAccount(models.Model):
    _inherit = "account.account"

    # parent_id = fields.Many2one('account.account', 'Parent Account', ondelete="set null")
    child_ids = fields.One2many('account.account', 'parent_id', 'Child Accounts')
    parent_path = fields.Char(index=True)
    parent_id = fields.Many2one(
        'account.account', 
        string="Parent Account",
        domain=[('account_type','=','view')]
    )

    @api.depends('move_line_ids', 'move_line_ids.debit', 'move_line_ids.credit')
    def compute_values(self):
        for account in self:
            domain = [('account_id', '=', account.id)]
            if self._context.get('date_from'):
                domain.append(('date', '>=', self._context['date_from']))
            if self._context.get('date_to'):
                domain.append(('date', '<=', self._context['date_to']))
            if self._context.get('state'):
                domain.append(('parent_state', '=', self._context['state']))
                
            move_lines = self.env['account.move.line'].search(domain)
            debit = sum(move_lines.mapped('debit'))
            credit = sum(move_lines.mapped('credit'))
            
            # Calculate initial balance if date_from is set
            initial_balance = 0.0
            if self._context.get('date_from') and self._context.get('show_initial_balance'):
                init_domain = [
                    ('account_id', '=', account.id),
                    ('date', '<', self._context['date_from'])
                ]
                if self._context.get('state'):
                    init_domain.append(('parent_state', '=', self._context['state']))
                init_lines = self.env['account.move.line'].search(init_domain)
                initial_balance = sum(init_lines.mapped('debit')) - sum(init_lines.mapped('credit'))
            
            account.debit = debit
            account.credit = credit
            account.balance = debit - credit
            account.initial_balance = initial_balance

    move_line_ids = fields.One2many('account.move.line', 'account_id', 'Journal Entry Lines')
    balance = fields.Float(compute="compute_values", digits=(16, 4), string='Balance')
    credit = fields.Float(compute="compute_values", digits=(16, 4), string='Credit')
    debit = fields.Float(compute="compute_values", digits=(16, 4), string='Debit')
    initial_balance = fields.Float(compute="compute_values", digits=(16, 4), string='Initial Balance')

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'code, name'
    _order = 'code, id'

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        context = self._context or {}
        new_domain = []
        if domain:
            for arg in domain:
                if isinstance(arg, (list, tuple)) and arg[0] == 'name' and isinstance(arg[2], str):
                    new_domain.append('|')
                    new_domain.append(arg)
                    new_domain.append(['code', arg[1], arg[2]])
                else:
                    new_domain.append(arg)
        if not context.get('show_parent_account', False):
            # In Odoo 18, check account_type field instead of user_type_id.type
            new_domain = expression.AND([[('account_type', '!=', 'view')], new_domain])
        return super()._search(new_domain, offset=offset, limit=limit, order=order)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.model
    def _prepare_liquidity_account_vals(self, company, code, vals):
        # Updated method name for Odoo 18
        res = super()._prepare_liquidity_account_vals(company, code, vals)
        
        if vals.get('type') == 'bank':
            account_code_prefix = company.bank_account_code_prefix or ''
        else:
            account_code_prefix = company.cash_account_code_prefix or company.bank_account_code_prefix or ''

        parent_id = self.env['account.account'].with_context({'show_parent_account': True}).search([
            ('code', '=', account_code_prefix),
            ('company_id', '=', company.id),
            ('account_type', '=', 'view')], limit=1)

        if parent_id:
            res.update({'parent_id': parent_id.id})
        return res
