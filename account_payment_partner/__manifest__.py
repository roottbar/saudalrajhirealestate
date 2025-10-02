# -*- coding: utf-8 -*-
{
    'name': "Account Payment Partner",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Account Payment Partner module",
    'description': "Enhanced Account Payment Partner module for Odoo 18.0 by roottbar",
    'category': "Banking addons",
    'author': "Akretion, Tecnativa, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account_payment_mode',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/account_move_view.xml',
        'views/account_move_line.xml',
        'views/account_payment_mode.xml',
        'views/report_invoice.xml',
        'reports/account_invoice_report_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}