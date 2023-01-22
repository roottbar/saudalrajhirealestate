# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import tools


class RentMaintenancePivotReport(models.Model):
    _name = 'rent.maintenance.pivot.report'
    _auto = False

    # id = fields.Integer(string='ID')
    prod_id = fields.Many2one('product.template', string='Product')
    unit_number = fields.Char(string='Unit Number')
    prop_id = fields.Many2one('rent.property', string='Property', copy=True)
    # unit_maintenance_desc = fields.Char(string='Maintenance Description')
    # unit_maintenance_val = fields.Float(string='Maintenance Value')

    def _init(self):
        tools.drop_view_if_exists(self.env.cr, 'rent_maintenance_pivot_report')
        self.env.cr("""CREATE OR REPLACE VIEW rent_maintenance_pivot_report AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    line.prod_id,
                    line.unit_number,
                    line.prop_id FROM (
                        SELECT
                            unit.id as prod_id,
                            unit.unit_number as unit_number,
                            unit.property_id as prop_id
                        FROM product_template unit
                        LEFT JOIN rent_property rp ON (unit.id = rp.product_id)
                    ) as line
            )""")
