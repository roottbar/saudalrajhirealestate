# -*- coding: utf-8 -*-
{
    'name': "Accounting with Operating Units",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Accounting with Operating Units module",
    'description': "Enhanced Accounting with Operating Units module for Odoo 18.0 by roottbar",
    'category': "Accounting & Finance",
    'author': "ForgeFlow, Serpent Consulting Services Pvt. Ltd.,WilldooIT Pty Ltd,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'analytic_operating_unit',
    ],
    'data': [
        # 'security/account_security.xml',  # Temporarily disabled due to Odoo 18 domain parsing issues
        'views/account_move_view.xml',
        'views/account_journal_view.xml',
        'views/company_view.xml',
        'views/account_payment_view.xml',
        'views/account_invoice_report_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}