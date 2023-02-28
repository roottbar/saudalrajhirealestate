# -*- coding: utf-8 -*-
###################################################################################
#    A part of plustech hr Project <www.plustech-it.com>
#
#   Plus Technology.
#    Copyright (C) 2022-TODAY PlusTech Technologies (<www.plustech-it.com>).
#    Author: Hassan Abdallah  (<hassanyahya101@gmail.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    id_days = fields.Integer(string='Identification Days', required=True, default=30)
    passport_days = fields.Integer(string='Passport Days', required=True, default=180)
    membership_days = fields.Integer(string='Membership Days', default=30)
    email_rec = fields.Char(string='E-Mail', required=False)
    hrm_notification = fields.Boolean()
    manager_notification = fields.Boolean()
    employee_notification = fields.Boolean()
    hrm_id = fields.Many2one('res.users', string='HRM')


class HRConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    id_days = fields.Integer(string='Identification Days', required=True,
                             default=lambda self: self.env.user.company_id.id_days)
    passport_days = fields.Integer(string='Passport Days', required=True,
                                   default=lambda self: self.env.user.company_id.passport_days)
    email_rec = fields.Char(string='E-Mail', default=lambda self: self.env.user.company_id.email_rec)
    hrm_notification = fields.Boolean(default=lambda self: self.env.user.company_id.hrm_notification)
    manager_notification = fields.Boolean(default=lambda self: self.env.user.company_id.manager_notification)
    employee_notification = fields.Boolean(default=lambda self: self.env.user.company_id.employee_notification)
    hrm_id = fields.Many2one('res.users', 'HRM', default=lambda self: self.env.user.company_id.hrm_id)
    membership_days = fields.Integer(string='Membership Days', required=True,
                                     default=lambda self: self.env.user.company_id.membership_days)

    @api.model
    def create(self, vals):
        res = super(HRConfigSettings, self).create(vals)
        res.company_id.write({'id_days': vals['id_days'], 'passport_days': vals['passport_days'],
                              'hrm_id': vals['hrm_id'], 'email_rec': vals['email_rec'],
                              'hrm_notification': vals['hrm_notification'],
                              'manager_notification': vals['manager_notification'],
                              'employee_notification': vals['employee_notification'],
                              'membership_days': vals['membership_days']})

        return res

    @api.onchange('hrm_id')
    def _onchange_(self):
        hrm_ids = self.env.ref('hr.group_hr_manager').users.ids
        res = {'domain': {'hrm_id': [('id', 'in', hrm_ids)]}}
        return res
