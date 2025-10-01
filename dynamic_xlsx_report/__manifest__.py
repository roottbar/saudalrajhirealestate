# -*- coding: utf-8 -*-
{
    'name': 'Dynamic XLS Report',
    'version': '18.0.1.0.0',
    'summary': """Dynamic XLS Report""",
    'description': '''Dynamic XLS Report
        
        Enhanced by roottbar for Odoo 18.0
    ''',
    'category': 'Tools',
    'author': 'Mahmoud Abd-Elaziz',
    'maintainer': 'roottbar',
    'depends': ['base', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'views/report_template.xml',
        'report/dynamic_pdf_report.xml',
    ],
    'demo': [],
    'installable': True,
}
