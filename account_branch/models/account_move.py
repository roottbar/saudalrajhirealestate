from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_default_branch(self):
        return self.env.user.branch_id

    branch_id = fields.Many2one('branch.branch',
                                string='Branch',
                                store=True,
                                readonly=False,
                                default=_get_default_branch,
                                domain=lambda self: [("id", "in", self.env.user.allowed_branches.ids)])

    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
                                 states={'draft': [('readonly', False)]},
                                 domain="['|', ('company_id', '=', False), "
                                        "('company_id', '=', company_id)]",
                                 string='Partner', change_default=True)

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        move_type = self._context.get('default_move_type') or 'entry'
        if move_type in self.get_sale_types(include_receipts=True):
            self.journal_id = self.branch_id.default_sale_journal_id
        elif move_type in self.get_purchase_types(include_receipts=True):
            self.journal_id = self.branch_id.default_purchase_journal_id
        if self.journal_id and self.journal_id.currency_id:
            new_currency = self.journal_id.currency_id
            if new_currency != self.currency_id:
                self.currency_id = new_currency
                self._onchange_currency()
        if self.state == 'draft' and self._get_last_sequence() and self.name and self.name != '/':
            self.name = '/'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.user_has_groups('account_branch.branch_user_see_own_invoice'):
            args += ['|', ('branch_id', 'in', self.env.user.allowed_branches.ids), ('branch_id', '=',False),]
        return super(AccountMove, self).search(args=args, offset=offset, limit=limit, order=order, count=count)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_default_branch(self):
        return self.move_id.branch_id or self.env.user.branch_id

    branch_id = fields.Many2one('branch.branch',
                                string='Branch',
                                store=True,
                                readonly=False,
                                related='move_id.branch_id',
                                domain=lambda self: [("id", "in", self.env.user.allowed_branches.ids)])
