{
    'name': 'Product Search by Default Code',
    'version': '18.0.1.0.0',
    'summary': 'Enhance product search by default_code',
    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
        This module adds search functionality for products using default_code.
    """,
    'author': 'Your Name',
    'maintainer': 'roottbar',
    'website': 'https://www.yourwebsite.com',
    'category': 'Inventory/Inventory',
    'depends': ['product'],
    'data': [
        'views/product_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}