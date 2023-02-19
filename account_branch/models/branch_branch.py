from odoo import fields, models, _


class BranchBranch(models.Model):
    _inherit = "branch.branch"

    bank_cash_journal_ids = fields.Many2many(
        'account.journal', string='Bank & Cash Journals')
    default_cash_journal_id = fields.Many2one('account.journal', string='Default Cash Journal',
                                              domain=[('type', 'in', ('cash', 'bank'))])
    default_sale_journal_id = fields.Many2one('account.journal', string='Default Sale Journal',
                                              domain=[('type', '=', 'sale')])
    default_purchase_journal_id = fields.Many2one('account.journal', string='Default Purchase Journal',
                                                  domain=[('type', '=', 'purchase')])

    def action_view_moves(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Branch Moves'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'context': {'group_by': 'move_type'},
            'domain': [('state', 'in', ['posted']), ('branch_id', '=', self.id)],
        }
