# -*- coding: utf-8 -*-
####################################
# Author: Bashier Elbashier
# Date: 27th February, 2021
####################################
from odoo import models, fields, api, _


class HREmployee(models.Model):
    _inherit = "hr.attendance"

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
