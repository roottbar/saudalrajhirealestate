from odoo import models, fields, api
from datetime import date

class CostCenterReport(models.TransientModel):
    _name = 'cost.center.report'
    _description = 'Cost Center Report'

    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1)
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=lambda self: fields.Date.context_today(self)
    )
    group_id = fields.Many2one('account.analytic.group', string='Analytic Group')
    analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        string='Analytic Accounts',
        domain="[('group_id', '=', group_id)]"
    )
    
    @api.onchange('group_id')
    def _onchange_group_id(self):
        if self.group_id:
            return {'domain': {'analytic_account_ids': [('group_id', '=', self.group_id.id)]}}
        else:
            return {'domain': {'analytic_account_ids': []}}
    
    def action_generate_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'group_id': self.group_id.id,
            'analytic_account_ids': self.analytic_account_ids.ids,
        }
        return self.env.ref('cost_center_reports.action_cost_center_report').report_action(self, data=data)
    
    def _get_report_data(self, data):
        # Get expenses
        expense_lines = self.env['account.move.line'].search([
            ('date', '>=', data['date_from']),
            ('date', '<=', data['date_to']),
            ('analytic_account_id', 'in', data['analytic_account_ids']),
            ('move_id.state', '=', 'posted'),
            ('account_id.internal_group', '=', 'expense'),
        ])
        
        # Get revenues
        revenue_lines = self.env['account.move.line'].search([
            ('date', '>=', data['date_from']),
            ('date', '<=', data['date_to']),
            ('analytic_account_id', 'in', data['analytic_account_ids']),
            ('move_id.state', '=', 'posted'),
            ('account_id.internal_group', '=', 'income'),
        ])
        
        # Get collections (customer payments)
        collection_lines = self.env['account.move.line'].search([
            ('date', '>=', data['date_from']),
            ('date', '<=', data['date_to']),
            ('analytic_account_id', 'in', data['analytic_account_ids']),
            ('move_id.state', '=', 'posted'),
            ('account_id.internal_type', '=', 'receivable'),
            ('credit', '>', 0),
        ])
        
        # Get debts (unpaid invoices)
        debt_lines = self.env['account.move.line'].search([
            ('date', '<=', data['date_to']),
            ('analytic_account_id', 'in', data['analytic_account_ids']),
            ('move_id.state', '=', 'posted'),
            ('account_id.internal_type', '=', 'receivable'),
            ('reconciled', '=', False),
            ('balance', '>', 0),
        ])
        
        # Organize data by analytic account
        report_data = {}
        analytic_accounts = self.env['account.analytic.account'].browse(data['analytic_account_ids'])
        
        for account in analytic_accounts:
            report_data[account.id] = {
                'name': account.name,
                'expenses': 0,
                'revenues': 0,
                'collections': 0,
                'debts': 0,
            }
        
        for line in expense_lines:
            report_data[line.analytic_account_id.id]['expenses'] += abs(line.balance)
        
        for line in revenue_lines:
            report_data[line.analytic_account_id.id]['revenues'] += abs(line.balance)
        
        for line in collection_lines:
            report_data[line.analytic_account_id.id]['collections'] += abs(line.balance)
        
        for line in debt_lines:
            report_data[line.analytic_account_id.id]['debts'] += abs(line.balance)
        
        return {
            'date_from': data['date_from'],
            'date_to': data['date_to'],
            'group_name': self.env['account.analytic.group'].browse(data['group_id']).name,
            'report_data': report_data,
        }
