# -*- coding: utf-8 -*-
{
    'name': "Parent Account (Chart of Account Hierarchy)",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Parent Account (Chart of Account Hierarchy) module",
    'description': "Enhanced Parent Account (Chart of Account Hierarchy) module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "Omal Bastin / O4ODOO",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/account_parent_security.xml',
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/open_chart.xml',
        'data/account_type_data.xml',
        'views/report_coa_hierarchy.xml',
    ],
    'license': "LGPL-3",
    'installable': True,  # Disabled for Odoo 18 - account.coa.report model no longer exists
    'auto_install': False,
}
