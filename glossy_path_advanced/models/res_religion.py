# -*- coding: utf-8 -*-

from odoo import models, fields


class ResReligion(models.Model):
    _name = "res.religion"
    _description = "Religion"

    name = fields.Char(string="Religion",required=True, copy=False)
    code = fields.Char(string="Code", copy=False)
    note = fields.Text(string="Note", copy=False)
    active = fields.Boolean(string="Active",default=True, copy=False)
