# -*- coding: utf-8 -*-
{
    'name': 'Dynamic Portal',
    'version': '15.0.1.0.0',
    'summary': """ Dynamic Portal """,
    'description': '''Dynamic Portal
        
        Enhanced by roottbar for Odoo 15.0
    ''',
    'category': 'web',
    'author': 'Mahmoud Abd-Elaziz',
    'maintainer': 'roottbar',
    'depends': ['portal','calendar','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/template.xml',
        'views/sharing_templates.xml',
        'views/portal.xml',
        # 'views/portal_assets.xml',
    ],
    'web.assets_frontend' :[
        '/static/src/css/style.css',
        '/static/src/js/edit_one2many_lines.js',
        '/static/src/js/onchange_buttons.js',
        '/static/src/js/onchange_fields.js',
        '/static/src/js/select2.js',
    ],
    'demo': [],
    'installable': True,
}

