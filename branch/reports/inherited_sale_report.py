# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    branch_id = fields.Many2one('res.branch')

    def _select_additional_fields(self):
        fields_add = super()._select_additional_fields()
        fields_add['branch_id'] = "s.branch_id"
        return fields_add

    def _group_by_sale(self):
        groupby = super()._group_by_sale()
        groupby += ", s.branch_id"
        return groupby

