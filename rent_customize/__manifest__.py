# -*- coding: utf-8 -*-
{
    'name': "Rent Customize",
    'summary': """Sale Renting Customization""",
    'category': 'Sales Management',
    'version': '18.0.0.1',
    # 'depends': ['sale_renting', 'renting', 'web_google_maps'],
    'depends': [
        'sale_renting', 
        'renting', 
        'web_google_maps',
        'multi_branches',  # Add this
        'branch',          # Add this
        'sale_operating_unit',  # Add this
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'cron/cron.xml',
        'views/product.xml',
        'views/sales_views.xml',
        'views/rent_property_build.xml',
        'views/sale_rental_schedule.xml',
        'views/attachment.xml',
        'views/move.xml',
        'report/contract.xml',
        'report/transfer.xml',
    ]
}
