# -*- coding: utf-8 -*-
from odoo import models, fields


class TenderBranch(models.Model):
    _name = "tender.branch"
    _description = "Tender Branches"

    name = fields.Char("Name", required=True, index=True, translate=True, copy=False)
    code = fields.Char("Code", copy=False)

    _sql_constraints = [("name", "unique(name)", "Name must be unique!")]
