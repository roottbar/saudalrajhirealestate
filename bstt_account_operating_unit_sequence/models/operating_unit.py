from odoo import api, fields, models, _

class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    automated_sequence = fields.Boolean('انشاء مسلسل اوتوماتيك؟',
                                        help="If checked, it will have an automated generated name based on the given code.")
    invoice_sequence_id = fields.Many2one('ir.sequence', 'مسلسل الفواتير', copy=False, check_company=True)
    journal_sequence_id = fields.Many2one('ir.sequence', 'مسلسل القيود', copy=False, check_company=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('automated_sequence'):
                inv_sequence = self.env['ir.sequence'].create({
                    'name': _('Sequence') + ' ' + vals['code'] + _(' فواتير '),
                    'padding': 5,
                    'prefix': vals['code'],
                    'company_id': vals.get('company_id'),
                })
                vals['invoice_sequence_id'] = inv_sequence.id

                journal_sequence = self.env['ir.sequence'].create({
                    'name': _('Sequence') + ' ' + vals['code'] + _(' قيود '),
                    'padding': 5,
                    'prefix': vals['code'],
                    'company_id': vals.get('company_id'),
                })
                vals['journal_sequence_id'] = journal_sequence.id

        return super(OperatingUnit, self).create(vals_list)

    def write(self, vals):
        if 'code' in vals:
            for rec in self:
                inv_sequence = {
                    'name': _('Sequence') + ' ' + vals['code'] + _(' فواتير '),
                    'padding': 5,
                    'prefix': vals['code'],
                }
                if rec.invoice_sequence_id:
                    rec.invoice_sequence_id.write(inv_sequence)

                journal_sequence = {
                    'name': _('Sequence') + ' ' + vals['code'] + _(' قيود '),
                    'padding': 5,
                    'prefix': vals['code'],
                }
                if rec.journal_sequence_id:
                    rec.journal_sequence_id.write(journal_sequence)

        if 'company_id' in vals:
            for rec in self:
                if rec.invoice_sequence_id:
                    rec.invoice_sequence_id.company_id = vals.get('company_id')
                if rec.journal_sequence_id:
                    rec.journal_sequence_id.company_id = vals.get('company_id')
        return super().write(vals)
