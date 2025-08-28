from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.constrains('order_line')
    def _check_rental_product_availability(self):
        """
        Validate that rental products are available for the specified dates
        """
        for order in self:
            if hasattr(order, 'rental_status') and order.rental_status:
                for line in order.order_line:
                    if line.product_id and line.product_id.rent_ok:
                        if not line.product_id.product_tmpl_id._check_rental_availability(
                            line.fromdate, line.todate, order.id
                        ):
                            raise ValidationError(
                                "المنتج '%s' غير متاح للإيجار في الفترة المحددة. "
                                "المنتج مؤجر حالياً في عقد آخر." % line.product_id.name
                            )

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.onchange('product_id', 'fromdate', 'todate')
    def _onchange_rental_product_availability(self):
        """
        Check product availability when product or dates change
        """
        if self.product_id and self.product_id.rent_ok and self.fromdate and self.todate:
            if not self.product_id.product_tmpl_id._check_rental_availability(
                self.fromdate, self.todate, self.order_id.id if self.order_id else None
            ):
                return {
                    'warning': {
                        'title': 'تحذير',
                        'message': "المنتج '%s' غير متاح للإيجار في الفترة المحددة. المنتج مؤجر حالياً في عقد آخر." % self.product_id.name
                    }
                }
    
    @api.model
    def _get_rental_product_domain(self):
        """
        Get domain for filtering available rental products
        """
        domain = [('rent_ok', '=', True)]
        
        # Get context values for date filtering
        from_date = self.env.context.get('default_fromdate')
        to_date = self.env.context.get('default_todate')
        order_id = self.env.context.get('default_order_id')
        
        if from_date and to_date:
            available_products = self.env['product.template'].get_available_rental_products(
                from_date, to_date, order_id
            )
            if available_products:
                domain.append(('id', 'in', available_products.ids))
            else:
                domain.append(('id', '=', False))  # No products available
                
        return domain