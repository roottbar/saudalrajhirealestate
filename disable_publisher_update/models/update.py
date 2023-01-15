# -*- coding: utf-8 -*-

from odoo import api, models

class PublisherWarrantyContract(models.AbstractModel):
    _inherit = "publisher_warranty.contract"

    def update_notification(self, cron_mode=True):
        return True
