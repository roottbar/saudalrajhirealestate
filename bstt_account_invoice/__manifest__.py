# -*- coding: utf-8 -*-
{
    'name': "BSTT Account Invoice",
    'version': "18.0.1.0.0",
    'summary': "Enhanced BSTT Account Invoice module",
    'description': "Enhanced BSTT Account Invoice module for Odoo 18.0 by roottbar",
    'category': "Invoicing",
    'author': "BSTT",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'web',
        'l10n_gcc_invoice',
        'l10n_sa',
        'hr',
    ],
    'data': [
        'security/account_security.xml',
        'views/company.xml',
        'reports/invoice_report.xml',
        'reports/base_document_layout.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}