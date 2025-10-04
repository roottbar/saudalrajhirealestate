# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class SaleReport(models.Model):

    _inherit = "sale.report"

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

    def _select_additional_fields(self):
        fields_add = super()._select_additional_fields()
        fields_add['operating_unit_id'] = "s.operating_unit_id"
        return fields_add

    def _group_by_sale(self):
        groupby = super()._group_by_sale()
        groupby += ", s.operating_unit_id"
        return groupby
