from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        
        # البحث باستخدام default_code إذا كان الإدخال رقميًا أو يتطابق مع نمط الكود
        if name:
            domain = args + ['|', ('default_code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in ('=', '!=', 'ilike', '=ilike', 'not ilike'):
                domain = args + ['|', ('default_code', operator, name), ('name', operator, name)]
            
            products = self.search(domain, limit=limit)
            return products.name_get()
        
        return super(ProductProduct, self).name_search(
            name=name, args=args, operator=operator, limit=limit)