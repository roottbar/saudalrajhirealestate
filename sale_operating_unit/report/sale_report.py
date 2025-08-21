# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        readonly=True
    )

    def _query(self, with_clause='', fields=None, groupby='', from_clause=''):
        fields = dict(fields or {})
        fields['operating_unit_id'] = ", s.operating_unit_id as operating_unit_id"
        groupby = f"{groupby}, s.operating_unit_id"
        return super()._query(with_clause, fields, groupby, from_clause)
