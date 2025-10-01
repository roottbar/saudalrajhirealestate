# -*- coding: utf-8 -*-
{
    'name': "PostgreSQL Query Deluxe",
    'version': "18.0.1.0.0",
    'summary': "Enhanced PostgreSQL Query Deluxe module",
    'description': "Enhanced PostgreSQL Query Deluxe module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Yvan Dotet",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/query_deluxe_views.xml',
        'wizard/pdforientation.xml',
        'report/print_pdf.xml',
        'datas/data.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}
