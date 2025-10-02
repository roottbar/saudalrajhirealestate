# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.company"

    name_arabic = fields.Char(string="Name(Arabic)", copy=False)
