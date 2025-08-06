from odoo import models, fields, api, _


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model_create_multi
    def create(self, vals_list):
        recs = super(Base, self).create(vals_list)
        if 'ir.' not in self._name and self.env.user.has_group('base.group_user'):
            items = self.env['ks_dashboard_ninja.item'].search(
                [['ks_model_id.model', '=', self._name], ['ks_auto_update_type', '=', 'ks_live_update']])
            if items:
                online_partner = self.env['res.users'].search([]).filtered(lambda x: x.im_status == 'online').mapped(
                    "partner_id").ids
                updates = [[
                    (self._cr.dbname, 'res.partner', partner_id),
                    {'type': 'ks_dashboard_ninja.notification', 'changes': items.ids},
                    {'id': self.id}
                ] for partner_id in online_partner]
                self.env['bus.bus']._sendmany(updates)
        return recs

    def write(self, vals):
        recs = super(Base, self).write(vals)
        if 'ir.' not in self._name and self.env.user.has_group('base.group_user'):
            items = self.env['ks_dashboard_ninja.item'].search(
                [['ks_model_id.model', '=', self._name], ['ks_auto_update_type', '=', 'ks_live_update']])
            if items:
                online_partner = self.env['res.users'].search([]).filtered(lambda x: x.im_status == 'online').mapped(
                    "partner_id").ids
                updates = [[
                    (self._cr.dbname, 'res.partner', partner_id),
                    {'type': 'ks_dashboard_ninja.notification', 'changes': items.ids},
                    {'id': self.id}
                ] for partner_id in online_partner]
                self.env['bus.bus']._sendmany(updates)
        return recs


class KSOdooBase(models.Model):
    _name = 'ks_odoo_base'
    
    @api.depends('related_model.field_name', recursive=True)
    def _compute_analytics(self):
        self.some_field = self.related_model.field_name
    
    @api.depends('cross_model.relation_field', recursive=True)
    def _compute_metrics(self):
        # Calculation logic
    
    @api.depends('dependent_field', recursive=True)  # Add recursive parameter
    def _compute_some_field(self):
        # Your computation logic
    
    @api.depends('analytic_account_id.balance', recursive=True)
    def _compute_financial_metrics(self):
        for record in self:
            record.financial_level = record.analytic_account_id.balance
    
    @api.depends('report_line_ids.value', recursive=True)
    def _compute_report_totals(self):
        self.total_value = sum(line.value for line in self.report_line_ids)
