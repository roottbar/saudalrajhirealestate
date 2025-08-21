from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        readonly=True
    )

    def _query(self, with_, fields, groupby, from_clause):
        fields = dict(fields)
        fields['operating_unit_id'] = ", s.operating_unit_id as operating_unit_id"
        groupby = f"{groupby}, s.operating_unit_id"
        return super()._query(with_, fields, groupby, from_clause)
