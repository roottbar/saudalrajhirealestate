# -*- coding: utf-8 -*-
{
    'name': 'Rental AI Insights',
    'version': '15.0.1.0.0',
    'summary': 'AI-driven analysis for Rental Module: trends, forecasts, KPIs',
    'sequence': 30,
    'category': 'Accounting',
    'author': 'Othmancs',
    'website': 'http://example.com',
    'license': 'OPL-1',
    'depends': ['renting', 'account', 'operating_unit'],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_insights_wizard_views.xml',
        'report/report_actions.xml',
        'report/inherit_document_layout_preview.xml',
        'report/ai_insights_report_template.xml',
    ],
    'installable': True,
    'application': True,
}