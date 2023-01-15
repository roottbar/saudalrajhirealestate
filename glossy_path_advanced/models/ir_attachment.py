# -*- coding: utf-8 -*-

from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    is_export_report = fields.Boolean(string="Export Report", copy=False, readonly=True)
