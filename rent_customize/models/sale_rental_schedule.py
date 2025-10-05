from odoo import fields, models
from odoo.tools.sql import SQL


class SaleRentalSchedule(models.Model):
    _inherit = 'sale.rental.schedule'

    property_number = fields.Many2one(related="order_line_id.property_number")
    property_id = fields.Many2one("rent.property")
    property_address_area = fields.Many2one("operating.unit")
    property_address_build = fields.Many2one("rent.property.build")

    def _select(self):
        parent = super(SaleRentalSchedule, self)._select()
        return SQL(
            "%s, t.property_id as property_id, rp.property_address_area as property_address_area, rp.property_address_build as property_address_build",
            parent,
        )

    # Odoo 18 switched to _group_by() returning SQL; keep backward compatibility
    def _group_by(self):
        try:
            parent = super(SaleRentalSchedule, self)._group_by()
        except AttributeError:
            parent = super(SaleRentalSchedule, self)._groupby()
        return SQL("%s, t.property_id, rp.property_address_area, rp.property_address_build", parent)

    def _from(self):
        return SQL(
            """
            sale_order_line sol
                join sale_order s on (sol.order_id=s.id)
                join res_partner partner on s.partner_id = partner.id
                left join product_product p on (sol.product_id=p.id)
                left join product_template t on (p.product_tmpl_id=t.id)
                left join rent_property rp on (t.property_id=rp.id)
                left join uom_uom u on (u.id=sol.product_uom)
                left join uom_uom u2 on (u2.id=t.uom_id)
                left outer join ordered_lots lot_info on (sol.id=lot_info.sol_id)
            """
        )
