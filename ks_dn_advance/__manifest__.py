# -*- coding: utf-8 -*-
{
    'name': "Dashboard Ninja Advance",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Dashboard Ninja Advance module",
    'description': "Enhanced Dashboard Ninja Advance module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Ksolves India Ltd.",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'ks_dashboard_ninja',
    ],
    'assets': {
        'web.assets_backend': [
            'ks_dn_advance/static/src/css/ks_tv_dashboard.css',
            'ks_dn_advance/static/src/js/ks_dashboard_ninja_tv_graph_preview.js',
            'ks_dn_advance/static/src/js/ks_dashboard_ninja_tv_list_preview.js',
            'ks_dn_advance/static/src/js/ks_dn_kpi_preview.js',
            'ks_dn_advance/static/src/js/ks_labels.js',
            'ks_dn_advance/static/src/js/ks_tv_dashboard.js',
            'ks_dn_advance/static/src/js/ks_ylabels.js',
        ],
        'web.assets_qweb': [
            'ks_dn_advance/static/src/xml/ks_dashboard_tv_ninja.xml',
            'ks_dn_advance/static/src/xml/ks_dna_to_template.xml',
            'ks_dn_advance/static/src/xml/ks_query_templates.xml',
        ],
        'web.assets_frontend': [
            'ks_dn_advance/static/src/js/ks_website_dashboard.js',
            'ks_dn_advance/static/src/xml/ks_dashboard_tv_ninja.xml',
            'ks_dn_advance/static/src/xml/ks_query_templates.xml',
        ],
    },
    'data': [
        'views/ks_dashboard_ninja_item_view_inherit.xml',
        'views/ks_dashboard_form_view_inherit.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}

