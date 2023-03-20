# -*- coding: utf-8 -*-

from odoo import models, fields, api
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _


class AssetLocation(models.Model):
    _name = "asset.location"

    name = fields.Char()


class AccountAsset(models.Model):
    _inherit = "account.asset"

    asset_location_id = fields.Many2one('asset.location')


    def unlink_lines(self):
        for rec in self:
            for line in rec.depreciation_move_ids:
                line.button_draft()
                line.unlink()
            rec.set_to_draft()
