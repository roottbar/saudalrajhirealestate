# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner"

    filter_branches = None
