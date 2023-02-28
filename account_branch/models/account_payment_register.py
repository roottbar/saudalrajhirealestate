from odoo import models, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.onchange('journal_id')
    def on_change_journal_id_domain(self):
        domain = [('company_id', '=', self.env.company.id), ('type', 'in', ('bank', 'cash'))]
        active_id = self._context.get('active_id')
        if self._context.get('active_model') == 'account.move' and active_id:
            move_id = self.env["account.move"].browse(active_id)
            if move_id.branch_id:
                domain.insert(0, ('id', 'in', move_id.branch_id.bank_cash_journal_ids.ids))
        return {"domain": {"journal_id": domain}}

    @api.depends('can_edit_wizard', 'company_id')
    def _compute_journal_id(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                active_id = self._context.get('active_id')
                if self._context.get('active_model') == 'account.move' and active_id:
                    move_id = self.env["account.move"].browse(active_id)
                    if move_id.branch_id:
                        if len(move_id.branch_id.bank_cash_journal_ids) > 0:
                            wizard.journal_id = move_id.branch_id.bank_cash_journal_ids[0]
                    else:
                        batch = wizard._get_batches()[0]
                        wizard.journal_id = wizard._get_batch_journal(batch)
                else:
                    batch = wizard._get_batches()[0]
                    wizard.journal_id = wizard._get_batch_journal(batch)
            else:
                active_id = self._context.get('active_id')
                if self._context.get('active_model') == 'account.move' and active_id:
                    move_id = self.env["account.move"].browse(active_id)
                    if move_id.branch_id:
                        if len(move_id.branch_id.bank_cash_journal_ids) > 0:
                            wizard.journal_id = move_id.branch_id.bank_cash_journal_ids[0]
                    else:
                        wizard.journal_id = self.env['account.journal'].search([
                            ('type', 'in', ('bank', 'cash')),
                            ('company_id', '=', wizard.company_id.id),
                        ], limit=1)
                else:
                    wizard.journal_id = self.env['account.journal'].search([
                        ('type', 'in', ('bank', 'cash')),
                        ('company_id', '=', wizard.company_id.id),
                    ], limit=1)
