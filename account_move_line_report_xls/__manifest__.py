# -*- coding: utf-8 -*-
{
    'name': "Account Move Line XLSX export",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Account Move Line XLSX export module",
    'description': "Enhanced Account Move Line XLSX export module for Odoo 18.0 by roottbar",
    'category': "Accounting & Finance",
    'author': "Noviat, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'report_xlsx_helper',
    ],
    'data': [
        'report/account_move_line_xlsx.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}