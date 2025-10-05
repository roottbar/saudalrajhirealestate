# -*- coding: utf-8 -*-
{
    'name': "PostgreSQL Query Deluxe",
    'version': "18.0.1.0.0",
    'summary': "Execute PostgreSQL queries from Odoo interface",
    'description': """
PostgreSQL Query Deluxe
=======================
Execute PostgreSQL queries directly from the Odoo interface.
    """,
    'category': "Technical",
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

