# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Hrleavetype(models.Model):
    _inherit = 'hr.leave.type'
    
    is_include_balance = fields.Boolean(string="Include Balance", copy=False)

    @api.onchange('allocation_type')
    def onchange_allocation_type(self):
        if self.allocation_type == 'no':
            self.is_include_balance = False
