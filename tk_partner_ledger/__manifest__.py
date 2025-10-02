# -*- coding: utf-8 -*-
{
    'name': "Partner Ledger Reports in XLS and PDF",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Partner Ledger Reports in XLS and PDF module",
    'description': "Enhanced Partner Ledger Reports in XLS and PDF module for Odoo 18.0 by roottbar",
    'category': "Accounting",
    'author': "Othmancs.",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'contacts',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/partner_ledger_pdf_report.xml',
        'wizard/partner_ledger_report_views.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}
