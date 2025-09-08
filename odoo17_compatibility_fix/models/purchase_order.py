# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_budget(self):
        """
        طريقة لإدارة الميزانية للطلب
        """
        # التحقق من وجود الطلب
        if not self:
            raise UserError(_('No purchase order selected.'))
        
        # منطق أساسي لإدارة الميزانية
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Budget Action'),
                'message': _('Budget action executed for purchase order %s.') % self.name,
                'type': 'info',
            }
        }