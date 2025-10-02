<<<<<<< HEAD
from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def _check_rental_availability(self, from_date=None, to_date=None, exclude_order_id=None):
        """
        Check if product is available for rental in the given date range
        Returns True if available, False if occupied
        """
        if not from_date or not to_date:
            return True
            
        # Convert string dates to datetime objects if needed
        if isinstance(from_date, str):
            from_date = datetime.strptime(from_date, DEFAULT_SERVER_DATE_FORMAT)
        if isinstance(to_date, str):
            to_date = datetime.strptime(to_date, DEFAULT_SERVER_DATE_FORMAT)
            
        # Search for existing rental orders with this product
        domain = [
            ('order_line.product_id', 'in', self.product_variant_ids.ids),
            ('rental_status', '=', 'occupied'),
            ('state', 'not in', ['cancel', 'draft']),
        ]
        
        # Exclude current order if editing
        if exclude_order_id:
            domain.append(('id', '!=', exclude_order_id))
            
        existing_orders = self.env['sale.order'].search(domain)
        
        for order in existing_orders:
            for line in order.order_line:
                if line.product_id.product_tmpl_id.id == self.id:
                    # Check date overlap
                    line_from = line.fromdate
                    line_to = line.todate
                    
                    if line_from and line_to:
                        # Convert to datetime for comparison
                        if isinstance(line_from, str):
                            line_from = datetime.strptime(line_from, DEFAULT_SERVER_DATE_FORMAT)
                        if isinstance(line_to, str):
                            line_to = datetime.strptime(line_to, DEFAULT_SERVER_DATE_FORMAT)
                            
                        # Check for date overlap
                        if (from_date <= line_to and to_date >= line_from):
                            return False
                            
        return True
    
    @api.model
    def get_available_rental_products(self, from_date=None, to_date=None, exclude_order_id=None):
        """
        Get list of products available for rental in the given date range
        """
        all_products = self.search([('rent_ok', '=', True)])
        available_products = self.env['product.template']
        
        for product in all_products:
            if product._check_rental_availability(from_date, to_date, exclude_order_id):
                available_products |= product
                
=======
from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def _check_rental_availability(self, from_date=None, to_date=None, exclude_order_id=None):
        """
        Check if product is available for rental in the given date range
        Returns True if available, False if occupied
        """
        if not from_date or not to_date:
            return True
            
        # Convert string dates to datetime objects if needed
        if isinstance(from_date, str):
            from_date = datetime.strptime(from_date, DEFAULT_SERVER_DATE_FORMAT)
        if isinstance(to_date, str):
            to_date = datetime.strptime(to_date, DEFAULT_SERVER_DATE_FORMAT)
            
        # Search for existing rental orders with this product
        domain = [
            ('order_line.product_id', 'in', self.product_variant_ids.ids),
            ('rental_status', '=', 'occupied'),
            ('state', 'not in', ['cancel', 'draft']),
        ]
        
        # Exclude current order if editing
        if exclude_order_id:
            domain.append(('id', '!=', exclude_order_id))
            
        existing_orders = self.env['sale.order'].search(domain)
        
        for order in existing_orders:
            for line in order.order_line:
                if line.product_id.product_tmpl_id.id == self.id:
                    # Check date overlap
                    line_from = line.fromdate
                    line_to = line.todate
                    
                    if line_from and line_to:
                        # Convert to datetime for comparison
                        if isinstance(line_from, str):
                            line_from = datetime.strptime(line_from, DEFAULT_SERVER_DATE_FORMAT)
                        if isinstance(line_to, str):
                            line_to = datetime.strptime(line_to, DEFAULT_SERVER_DATE_FORMAT)
                            
                        # Check for date overlap
                        if (from_date <= line_to and to_date >= line_from):
                            return False
                            
        return True
    
    @api.model
    def get_available_rental_products(self, from_date=None, to_date=None, exclude_order_id=None):
        """
        Get list of products available for rental in the given date range
        """
        all_products = self.search([('rent_ok', '=', True)])
        available_products = self.env['product.template']
        
        for product in all_products:
            if product._check_rental_availability(from_date, to_date, exclude_order_id):
                available_products |= product
                
>>>>>>> 37199f9744a6e4c8cc0af3f1967bf725aa67430a
        return available_products