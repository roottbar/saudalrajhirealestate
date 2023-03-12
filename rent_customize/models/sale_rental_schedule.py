from odoo import fields, models, api


class SaleRentalSchedule(models.Model):
    _inherit = 'sale.rental.schedule'

    property_number = fields.Many2one(related="order_line_id.property_number")
    property_id = fields.Many2one(related="product_id.property_id")
    property_address_area = fields.Many2one(related="product_id.property_id.property_address_area")
    property_address_build = fields.Many2one(related="product_id.property_id.property_address_build")
    # rental_name = fields.Char(string="Name", compute="get_rental_name")

    # @api.depends('order_line_id')
    # def get_rental_name(self):
    #     for rec in self: q
    #         if rec.order_line_id:
    #             if rec.order_line_id.product_id.name and rec.order_line_id.property_number.display_name:
    #                 rec.rental_name = rec.order_line_id.product_id.name + " - "+ rec.order_line_id.property_number.display_name
    #             if rec.order_line_id.product_id.name and not rec.order_line_id.property_number.display_name:
    #                 rec.rental_name = rec.order_line_id.product_id.name
    #             if not rec.order_line_id.product_id.name and rec.order_line_id.property_number.display_name:
    #                 rec.rental_name =  rec.order_line_id.property_number.display_name
    #         else:
    #             rec.rental_name = "------"