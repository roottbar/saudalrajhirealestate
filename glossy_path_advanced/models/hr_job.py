# -*- coding: utf-8 -*-

from odoo import models, fields


class HrJob(models.Model):
    _inherit = "hr.job"

    arabic_name = fields.Char(string="Job Position Arabic",  copy=False)

