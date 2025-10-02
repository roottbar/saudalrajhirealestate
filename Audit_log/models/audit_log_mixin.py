from odoo import models, api

class AuditLogMixin(models.AbstractModel):
    _name = 'audit.log.mixin'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for vals, rec in zip(vals_list, records):
            self.env['custom.audit.log'].create({
                'user_id': self.env.uid,
                'model': self._name,
                'record_id': rec.id,
                'action': 'create',
                'changes': str(vals)
            })
        return records

    def write(self, vals):
        for rec in self:
            changed_fields = {}
            for field, new_value in vals.items():
                old_value = rec[field]
                if old_value != new_value:
                    changed_fields[field] = {
                        'old': old_value,
                        'new': new_value
                    }
            if changed_fields:
                self.env['custom.audit.log'].create({
                    'user_id': self.env.uid,
                    'model': self._name,
                    'record_id': rec.id,
                    'action': 'write',
                    'changes': str(changed_fields)
                })
        return super().write(vals)

    def unlink(self):
        for rec in self:
            self.env['custom.audit.log'].create({
                'user_id': self.env.uid,
                'model': self._name,
                'record_id': rec.id,
                'action': 'unlink',
                'changes': ''
            })
        return super().unlink()