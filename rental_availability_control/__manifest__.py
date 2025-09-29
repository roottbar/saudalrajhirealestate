{
    'name': 'Rental Availability Control',
    'version': '15.0.1.0.0',
    'category': 'Sales/Rental',
    'summary': 'Control product availability in rental orders based on occupancy status',
    'description': '
        
        Enhanced by roottbar for Odoo 15.0''
        This module prevents rented products from appearing in new rental orders
        if they are in 'occupied' status and within the contract period.
        Products will only be available when their status is 'termination'.
    ''',
    'author': 'Your Company',
    'maintainer': 'roottbar',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale',
        'product',
        'renting',
        'rent_customize',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
