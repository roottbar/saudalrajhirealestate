# -*- coding: utf-8 -*-
{
    'name': "Rent Customize",
    'summary': """Sale Renting Customization""",
    'category': 'Sales Management',
    'version': '0.1',
    'depends': ['sale_renting', 'renting', 'web_google_maps'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sales_views.xml',
        'views/rent_property_build.xml',
        'views/sale_rental_schedule.xml',
        'views/attachment.xml',
        'views/product.xml',
        'report/contract.xml',
    ]
}
