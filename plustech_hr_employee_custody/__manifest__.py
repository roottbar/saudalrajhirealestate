# -*- coding: utf-8 -*-
{
    'name': "Plus Tech Employee Custody Management",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Plus Tech Employee Custody Management module",
    'description': "Enhanced Plus Tech Employee Custody Management module for Odoo 18.0 by roottbar",
    'category': "Human Resources/Custody",
    'author': "Plus Technology Team",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'plustech_hr_employee',
        'account_asset',
    ],
    'data': [
        'security/custody_security.xml',
        'security/ir.model.access.csv',
        'data/request_sequance.xml',
        'data/cron.xml',
        'data/template.xml',
        'views/employee_custody.xml',
        'views/custody_items.xml',
        'views/account_asset.xml',
        'views/hr_employee.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}