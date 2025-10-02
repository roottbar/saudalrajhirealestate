{
    'name': 'Product Search by Default Code',
    'version': '15.0.1.0.0',
    'summary': 'Enhance product search by default_code',
    'description': """
        This module adds search functionality for products using default_code.
    """,
    'author': 'Your Name',
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