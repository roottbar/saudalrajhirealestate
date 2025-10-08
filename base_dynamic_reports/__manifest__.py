# -*- coding: utf-8 -*-
{
    'name': "Base Dynamic Reports",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Base Dynamic Reports module",
    'description': "Enhanced Base Dynamic Reports module for Odoo 18.0 by roottbar",
    'category': "Uncategorized",
    'author': "Crevisoft",
    'maintainer': "roottbar",
    'depends': [
        'base',
    ],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'base_dynamic_reports/static/src/css/search_menus.css',
            'base_dynamic_reports/static/src/js/basic_dynamic_report.js',
            'base_dynamic_reports/static/src/js/dynamic_relation_filters.js',
            'base_dynamic_reports/static/src/js/dynamic_report_widgets.js',
        ],
        'web.assets_qweb': [
            'base_dynamic_reports/static/src/xml/*.xml',
        ],
    },
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}