# -*- coding: utf-8 -*-
{
    'name': "Generate Excel & PDF Report of Activity for Specific Users",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Generate Excel & PDF Report of Activity for Specific Users module",
    'description': "Enhanced Generate Excel & PDF Report of Activity for Specific Users module for Odoo 18.0 by roottbar",
    'category': "Sales,Mail",
    'author': "Creyox Technologies",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/activity_report_wizard_views.xml',
        'report/activity_report.xml',
        'report/activity_template.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}