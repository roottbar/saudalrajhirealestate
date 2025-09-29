# -*- coding: utf-8 -*-
{
    'name': "Base Dynamic Reports",

    'summary': """
        Base Dynamic Reports""",

    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
        Base Dynamic Reports
    """,

    'author': "Crevisoft",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'views/templates.xml',
    ],
    'web.assets_backend':[
        '/static/src/css/search_menus.css',
        '/static/src/js/dynamic_relation_filters.js',
        '/static/src/js/dynamic_report_widgets.js',
        '/static/src/js/basic_dynamic_report.js',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ]
}
