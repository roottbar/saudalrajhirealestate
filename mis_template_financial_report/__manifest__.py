# -*- coding: utf-8 -*-
{
    'name': "Profit & Loss / Balance sheet MIS templates",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Profit & Loss / Balance sheet MIS templates module",
    'description': "Enhanced Profit & Loss / Balance sheet MIS templates module for Odoo 18.0 by roottbar",
    'category': "Localization",
    'author': "Hunki Enterprises BV,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'mis_builder',
    ],
    'data': [
        'data/mis_report_style.xml',
        'data/mis_report.xml',
        'data/mis_report_kpi.xml',
        'data/mis_report_subreport.xml',
        'views/mis_report_instance_views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/mis_template_financial_report.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}