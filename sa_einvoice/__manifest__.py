# -*- coding: utf-8 -*-
{
    'name': "sa_einvoice",
    'version': "18.0.1.0.0",
    'summary': "Enhanced sa_einvoice module",
    'description': "Enhanced sa_einvoice module for Odoo 18.0 by roottbar",
    'category': "accounting",
    'author': "BSTT Company",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'sale',
        'account',
        'uom',
        'account_invoice_ubl',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'wizards/elect_inv_reason.xml',
        'views/elect_reaons.xml',
        'views/company.xml',
        'views/partner.xml',
        'views/invoice.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}