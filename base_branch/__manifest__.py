{
    'name': 'Branches Configuration',
    'version': '15.0.1.0.0',
    'sequence': 1,
    'depends': ['base_setup', 'base', 'product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/branch_branch_views.xml',
        'views/res_users_views.xml',
        'views/res_partner_views.xml',
        'views/product_views.xml',
        'views/company_view.xml',
    ],
    'installable': True,
    'application': True,
}
