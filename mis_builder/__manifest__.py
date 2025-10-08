# -*- coding: utf-8 -*-
{
    'name': "MIS Builder",
    'version': "18.0.1.0.0",
    'summary': "Enhanced MIS Builder module",
    'description': "Enhanced MIS Builder module for Odoo 18.0 by roottbar",
    'category': "Reporting",
    'author': "ACSONE SA/NV, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'board',
        'report_xlsx',
        'date_range',
    ],
    'data': [
        'wizard/mis_builder_dashboard.xml',
        'views/mis_report.xml',
        'views/mis_report_instance.xml',
        'views/mis_report_style.xml',
        'datas/ir_cron.xml',
        'security/ir.model.access.csv',
        'security/mis_builder_security.xml',
        'report/mis_report_instance_qweb.xml',
        'report/mis_report_instance_xlsx.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'mis_builder/static/src/xml/mis_report_widget.xml',
        ],
    },
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}