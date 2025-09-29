# -*- coding: utf-8 -*-
{
    'name': "Partner Accounting Categories",

    'summary': """
        Partner Accounting Categories""",

    'description': """
        Partner accounting categories used when created customers or vendors to select payable & receivable accounts
    """,
    'author': "Crevisoft",
    'website': "https://www.crevisoft.com",
    'category': 'hidden',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_account_category_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_view.xml'
    ],
}
