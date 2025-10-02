<<<<<<< HEAD
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one(
        'hr.employee', 
        string='Related Employee',
        help='Employee-related data of the user',
        auto_join=True
    )

    @api.model
    def create(self, vals):
        """Override create to automatically create employee if needed"""
        user = super(ResUsers, self).create(vals)
        if not user.employee_id and user.name:
            # Create employee record for the user
            employee_vals = {
                'name': user.name,
                'user_id': user.id,
                'work_email': user.email,
            }
            employee = self.env['hr.employee'].create(employee_vals)
            user.employee_id = employee.id

        return user 
=======
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one(
        'hr.employee', 
        string='Related Employee',
        help='Employee-related data of the user',
        auto_join=True
    )

    @api.model
    def create(self, vals):
        """Override create to automatically create employee if needed"""
        user = super(ResUsers, self).create(vals)
        if not user.employee_id and user.name:
            # Create employee record for the user
            employee_vals = {
                'name': user.name,
                'user_id': user.id,
                'work_email': user.email,
            }
            employee = self.env['hr.employee'].create(employee_vals)
            user.employee_id = employee.id

        return user 
>>>>>>> 37199f9744a6e4c8cc0af3f1967bf725aa67430a
