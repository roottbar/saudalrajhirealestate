# -*- coding: utf-8 -*-
{
    'name': "MIS Builder Cash Flow",
    'version': "18.0.1.0.0",
    'summary': "Enhanced MIS Builder Cash Flow module",
    'description': "Enhanced MIS Builder Cash Flow module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "ADHOC SA, Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'mis_builder',
    ],
    'data': [
        'security/mis_cash_flow_security.xml',
        'report/mis_cash_flow_views.xml',
        'views/mis_cash_flow_forecast_line_views.xml',
        'views/account_account_views.xml',
        'data/mis_report_style.xml',
        'data/mis_report.xml',
        'data/mis_report_instance.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}