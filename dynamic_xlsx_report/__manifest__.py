# -*- coding: utf-8 -*-
{
    'name': "Dynamic XLS Report",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Dynamic XLS Report module",
    'description': "Enhanced Dynamic XLS Report module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Mahmoud Abd-Elaziz",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/report_template.xml',
        'report/dynamic_pdf_report.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}