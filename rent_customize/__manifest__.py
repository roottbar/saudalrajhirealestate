# -*- coding: utf-8 -*-
{
    'name': "Rent Customize",
    'summary': """Sale Renting Customization""",
    'category': 'Sales Management',
    'version': '0.1',
    'depends': ['sale_renting','renting'],
    'data': [
        'security/security.xml',
        'views/sales_views.xml',
        'views/rent_property_build.xml'
    ]
}
