# -*- coding: utf-8 -*-
{
    'name': 'Rental AI Insights',
    'version': '15.0.1.0',
    'summary': 'ذكاء اصطناعي لتحليلات الإيجار: اتجاهات، توقعات، أداء الفروع والعقارات',
    'category': 'Rental/Analytics',
    'author': 'Othmancs',
    'depends': ['base', 'account', 'renting', 'operating_unit', 'sale_operating_unit'],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_insights_wizard_views.xml',
        'views/menu.xml',
    ],
    'application': True,
}