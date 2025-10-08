# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import fields, models


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    # Keep only the view type extension and rely on Odoo 18 core
    # validation to avoid domain parsing issues.
    type = fields.Selection(selection_add=[('google_map', 'Google Maps')])
