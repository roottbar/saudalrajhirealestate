# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class PettyCashRequestFeeding(models.Model):
    _name = "petty.cash.request.feeding"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Petty Cash Request Feeding"

    name = fields.Char(string='Name', required=True, readonly=True, copy=False, default="/")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validation', 'Validation'),
        ('review', 'Review'),
        ('p_m_approved', 'PM Approved'),
        ('gm_approved', 'GM Approved'),
        ('f_m_approved', 'FM Approved'),
        ('rejected', 'Rejected'),
    ], string='State', index=True, readonly=True, default='draft', copy=False, track_visibility='onchange')
    date = fields.Datetime('Date', required=True, default=fields.Datetime.now)
    user_rule_id = fields.Many2one("petty.cash.user.rule", string='Box', required=True, )
    journal_id = fields.Many2one('account.journal', related="user_rule_id.journal_id", string='Journal', readonly=True,
                                 store=True)
    account_id = fields.Many2one('account.account', related="user_rule_id.account_id", string="Account", readonly=True,
                                 store=True)
    payment_journal_id = fields.Many2one('account.journal', string='Payment Journal', readonly=True)
    current_balance = fields.Float("Current Balance", readonly=True, compute='_compute_current_balance')
    final_current_balance = fields.Float("Current Balance", readonly=True)
    amount = fields.Float("Amount", required=True, digits=dp.get_precision('Product Price'))
    actual_amount = fields.Float("Actual Amount", readonly=True, digits=dp.get_precision('Product Price'))
    reason = fields.Char('Reason')
    approved_reason = fields.Char('Approved Reason', readonly=True)
    rejected_reason = fields.Char('Rejected Reason', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, copy=False,
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    active = fields.Boolean('Active', default=True)
    project_id = fields.Many2one('project.project', string='Project', copy=False, tracking=True)
    manager_project_id = fields.Many2one("res.users", string="Project Manger", copy=False)
    allow_pm_approve = fields.Boolean(string="Allow Approve", copy=False, compute="_compute_allow_pm_approve")

    def _compute_allow_pm_approve(self):
        for request_feeding in self:
            allow_pm_approve = False
            if request_feeding.state == "review" and request_feeding.manager_project_id and request_feeding.manager_project_id == self.env.user:
                allow_pm_approve = True

            request_feeding.allow_pm_approve = allow_pm_approve

    def add_follower_id(self, res_id, partner_id):
        default_subtypes, _, _ = self.env['mail.message.subtype'].default_subtypes('petty.cash.request.feeding')

        vals = {
            'res_id': res_id,
            'res_model': 'petty.cash.request.feeding',
            'partner_id': partner_id.id,
            'subtype_ids': [(6, 0, default_subtypes.ids)]
        }

        follower_id = self.sudo().env['mail.followers'].create(vals)

        return follower_id

    def _compute_current_balance(self):
        account_move_line = self.env['account.move.line']

        for request_feeding in self:
            current_balance = 0
            if request_feeding.state != "gm_approved" and request_feeding.state != "rejected":
                account_move_lines = account_move_line.search([('journal_id', '=', request_feeding.journal_id.id),
                                                               ('account_id', '=', request_feeding.account_id.id)])

                for line in account_move_lines:
                    current_balance += line.debit - line.credit

            request_feeding.current_balance = current_balance

    @api.constrains('amount')
    def _check_amount(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero"))

    @api.model
    def create(self, vals):
        res = super(PettyCashRequestFeeding, self).create(vals)

        # add all admin in followers
        users = self.env['res.users'].search([('id', '!=', self.env.user.id)])

        for user in users:
            if user.has_group('base.group_system'):
                self.add_follower_id(res.id, user.partner_id)
        return res

    @api.model
    def default_get(self, default_fields):
        user_rule = self.env['petty.cash.user.rule'].search([('user', '=', self.env.user.id)], limit=1)

        if not user_rule:
            raise ValidationError(_("User must have box"))
        contextual_self = self.with_context(default_user_rule_id=user_rule)
        return super(PettyCashRequestFeeding, contextual_self).default_get(default_fields)

    def action_validate(self):
        manager_ids = self.sudo().env["res.users"].search(
            [('id', '!=', self.env.user.id),
             ('groups_id', 'in', [self.sudo().env.ref("petty_cash.group_petty_general_m_approved").id])]).ids
        # validate Request Feeding
        for request_feeding in self:
            if request_feeding.state != 'draft':
                continue
            vals = {"name": self.env['ir.sequence'].next_by_code('petty.cash.request.feeding')}
            if request_feeding.project_id.user_id:
                manager_ids.append(request_feeding.project_id.user_id.id)
            if request_feeding.project_id.user_id:
                vals.update({
                    "state": "review",
                    "manager_project_id": request_feeding.project_id.user_id.id
                })
            else:
                vals.update({"state": "p_m_approved"})
            request_feeding.write(vals)
            # send massage to gm managers and project manager
            if manager_ids:
                msg = ('petty cash request feeding %s has been created by %s') % (
                    request_feeding.name, request_feeding.create_uid.name)
                request_feeding.message_post(partner_ids=list(set(manager_ids)), body=msg,
                                             subtype_xmlid='mail.mt_comment')
        return True

    def action_project_manager_approve(self):
        # transfer Request Feeding to  Project Manager Approved
        for request_feeding in self:
            if request_feeding.state != 'review':
                continue
            request_feeding.write({'state': 'p_m_approved'})
        return True

    def action_gm_approve(self):
        # transfer Request Feeding to  Financial Manager Approved
        for request_feeding in self:
            if request_feeding.state not in ['review', 'p_m_approved']:
                continue
            request_feeding.write({'state': 'gm_approved'})
        return True

    def _track_subtype(self, init_values):
        self.ensure_one()

        if 'state' in init_values and self.state == 'review':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_request_feeding_validation')
        elif 'state' in init_values and self.state == 'p_m_approved':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_request_p_m_approved')
        elif 'state' in init_values and self.state == 'gm_approved':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_request_feeding_gm_approved')
        elif 'state' in init_values and self.state == 'f_m_approved':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_request_feeding_f_m_approved')
        elif 'state' in init_values and self.state == 'rejected':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_request_feeding_rejected')

        return super(PettyCashRequestFeeding, self)._track_subtype(init_values)

    def open_journal_entries(self):
        action = self.sudo().env.ref('account.action_move_journal_line', False)
        result = action.read()[0]
        result['context'] = {'view_no_maturity': True}
        result['domain'] = [('request_feeding_id', '=', self.id)]

        return result
