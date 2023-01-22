# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class PettyCashRequest(models.Model):
    _name = "petty.cash.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Petty Cash Request"

    name = fields.Char(readonly=True, copy=False)
    description = fields.Text("Description", required=True)
    recommends = fields.Text("Recommends")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Send'),
        ('in progress', 'In Progress'),
        ('p_m_approved', 'PM Approved'),
        ('gm_approved', 'GM Approved'),
        ('f_m_approved', 'FM Approved'),
        ('cancel', 'Cancel'),
    ], string='State', index=True, readonly=True, default='draft', copy=False, track_visibility='onchange')
    date = fields.Datetime('Date', required=True, default=fields.Datetime.now, copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner')
    amount = fields.Float("Amount", required=True, digits=dp.get_precision('Product Price'))
    actual_amount = fields.Float("Actual Amount", readonly=True, digits=dp.get_precision('Product Price'), copy=False)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, copy=False,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, copy=False,
                                 default=lambda self: self.env.user.company_id.id)
    journal_id = fields.Many2one('account.journal', string='Journal')
    attachment = fields.Binary(string='Attachment')
    manager_id = fields.Many2one('res.users', string='FM Manager', required=True,
                                 domain=lambda self: [
                                     ("groups_id", "=", self.sudo().env.ref("petty_cash.group_petty_cash_manager").id)])
    payment_voucher_id = fields.Many2one('payment.voucher', string='Payment Voucher', copy=False)
    petty_cash_id = fields.Many2one('petty.cash', string='Petty Cash', compute='_get_petty_cash', copy=False)
    show_button = fields.Boolean('Show Button', compute="_compute_show_button")
    project_id = fields.Many2one('project.project', string='Project', copy=False, tracking=True)
    manager_project_id = fields.Many2one("res.users", string="Project Manger", copy=False)
    allow_pm_approve = fields.Boolean(string="Allow Approve", copy=False, compute="_compute_allow_pm_approve")

    def _compute_allow_pm_approve(self):
        for petty_cash_request in self:
            allow_pm_approve = False
            if petty_cash_request.state == "in progress" and petty_cash_request.manager_project_id and petty_cash_request.manager_project_id == self.env.user:
                allow_pm_approve = True

            petty_cash_request.allow_pm_approve = allow_pm_approve

    @api.constrains('amount')
    def _check_amount(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero"))

    def _compute_show_button(self):
        for petty_cash_request in self:
            if petty_cash_request.env.user.id == petty_cash_request.create_uid.id:
                petty_cash_request.show_button = True
            else:
                petty_cash_request.show_button = False

    def _get_petty_cash(self):
        petty_cash_line_obj = self.env['petty.cash.line']
        for petty_cash_request in self:
            petty_cash_line = petty_cash_line_obj.search([('petty_cash_request_id', '=', petty_cash_request.id)])
            petty_cash_request.petty_cash_id = petty_cash_line and petty_cash_line.petty_cash_id or False

    def add_follower_id(self, res_id, partner_id):
        default_subtypes, _, _ = self.env['mail.message.subtype'].default_subtypes('petty.cash.request')

        vals = {
            'res_id': res_id,
            'res_model': 'petty.cash.request',
            'partner_id': partner_id.id,
            'subtype_ids': [(6, 0, default_subtypes.ids)]
        }

        follower_id = self.sudo().env['mail.followers'].create(vals)

        return follower_id

    @api.model
    def create(self, vals):
        if not vals.get('journal_id', False):
            raise ValidationError(_("User must have journal"))

        res = super(PettyCashRequest, self).create(vals)

        # add all admin in followers
        users = self.env['res.users'].search([('id', '!=', self.env.user.id)])

        for user in users:
            if user.has_group('base.group_system'):
                self.add_follower_id(res.id, user.partner_id)
        return res

    @api.model
    def default_get(self, default_fields):
        user_rule = self.env['petty.cash.user.rule'].search([('user', '=', self.env.user.id)], limit=1)
        journal = user_rule.journal_id

        contextual_self = self.with_context(default_journal_id=journal)
        return super(PettyCashRequest, contextual_self).default_get(default_fields)

    def action_send(self):
        manager_ids = self.sudo().env["res.users"].search(
            [('id', '!=', self.env.user.id),
             ('groups_id', 'in', [self.sudo().env.ref("petty_cash.group_petty_general_m_approved").id])]).ids

        # send petty cash request
        for petty_cash_request in self:
            if petty_cash_request.state != 'draft':
                continue
            vals = {"name": self.env['ir.sequence'].next_by_code('petty.cash.request')}
            if petty_cash_request.project_id.user_id:
                manager_ids.append(petty_cash_request.project_id.user_id.id)
                vals.update({
                    "state": "in progress",
                    "manager_project_id": petty_cash_request.project_id.user_id.id
                })
            else:
                vals.update({"state": "p_m_approved"})
            petty_cash_request.write(vals)

            # send massage to gm managers and project manager
            if manager_ids:
                msg = ('petty cash request %s has been created by %s') % (
                    petty_cash_request.name, petty_cash_request.create_uid.name)
                petty_cash_request.message_post(partner_ids=list(set(manager_ids)), body=msg,
                                                subtype_xmlid='mail.mt_comment')
        return True

    def create_payment_voucher(self):
        if self.payment_voucher_id:
            raise ValidationError(_("Petty Cash Request already has payment voucher"))
        if self.petty_cash_id:
            raise ValidationError(_("Petty Cash Request assign already has petty cash"))

        ctx = {
            'default_reference': self.name,
            'default_partner_id': self.partner_id and self.partner_id.id or False,
            'default_payment_date': self.date,
            'default_amount': self.actual_amount,
            'default_currency_id': self.currency_id.id,
            'default_journal_id': self.journal_id.id,
            'default_communication': self.description,
        }

        form = self.sudo().env.ref('petty_cash.view_payment_voucher_form')

        return {
            'name': _('Payment Voucher'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payment.voucher',
            'views': [(form.id, 'form')],
            'view_id': form.id,
            'context': ctx,
        }

    def assign_petty_cash(self):
        if self.payment_voucher_id:
            raise ValidationError(_("Petty Cash Request already has payment voucher"))
        if self.petty_cash_id:
            raise ValidationError(_("Petty Cash Request assign already has petty cash"))

        petty_cash_ids = self.env['petty.cash'].search(
            [('state', '!=', 'closed'), ('responsible_id', '=', self.create_uid.id)])

        if not petty_cash_ids:
            raise ValidationError(_("No exists petty cash, Please create new petty cash"))

        action = self.sudo().env.ref('petty_cash.action_petty_cash_request_line', False)
        result = action.read()[0]

        result['context'] = {'petty_cash_ids': petty_cash_ids.ids}

        return result

    def action_project_manager_approve(self):
        # transfer Request to  Project Manager Approved
        for petty_cash_request in self:
            if petty_cash_request.state != 'in progress':
                continue
            petty_cash_request.write({'state': 'p_m_approved'})
        return True

    def action_gm_approve(self):
        # transfer Request to  Financial Manager Approved
        for petty_cash_request in self:
            if petty_cash_request.state not in ['in progress', 'p_m_approved']:
                continue
            petty_cash_request.write({'state': 'gm_approved'})
        return True

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'in progress':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_request_send')
        elif 'state' in init_values and self.state == 'gm_approved':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_request_gm_approved')
        elif 'state' in init_values and self.state == 'p_m_approved':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_p_m_approved')
        elif 'state' in init_values and self.state == 'f_m_approved':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_f_m_approved')
        elif 'state' in init_values and self.state == 'cancel':
            return self.sudo().env.ref('petty_cash.mt_petty_cash_request_cancel')
        return super(PettyCashRequest, self)._track_subtype(init_values)

    def open_payment_voucher(self):
        action = self.sudo().env.ref('petty_cash.action_payment_voucher_petty_cash_request', False)
        result = action.read()[0]
        result['domain'] = [('id', '=', self.payment_voucher_id.id)]
        return result

    def open_petty_cash(self):
        action = self.sudo().env.ref('petty_cash.action_petty_cash', False)
        result = action.read()[0]
        result['domain'] = [('id', '=', self.petty_cash_id.id)]
        return result
