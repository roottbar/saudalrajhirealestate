from odoo import fields, models


class SaleRentalSchedule(models.Model):
    _inherit = 'sale.rental.schedule'

    property_number = fields.Many2one(related="order_line_id.property_number")
    property_id = fields.Many2one("rent.property")
    property_address_area = fields.Many2one("operating.unit")
    property_address_build = fields.Many2one("rent.property.build")

    def _select(self):
        return super(SaleRentalSchedule, self)._select() + ", t.property_id as property_id, rp.property_address_area as property_address_area, rp.property_address_build as property_address_build"

    def _groupby(self):
        return super(SaleRentalSchedule, self)._groupby() + ", t.property_id,rp.property_address_area,rp.property_address_build"

    def _from(self):
        return """
            sale_order_line sol
                join sale_order s on (sol.order_id=s.id)
                join res_partner partner on s.partner_id = partner.id
                left join product_product p on (sol.product_id=p.id)
                left join product_template t on (p.product_tmpl_id=t.id)
                left join rent_property rp on (t.property_id=rp.id)
                left join uom_uom u on (u.id=sol.product_uom)
                left join uom_uom u2 on (u2.id=t.uom_id)
                LEFT OUTER JOIN ordered_lots lot_info ON sol.id=lot_info.sol_id,
                padding pdg
        """
