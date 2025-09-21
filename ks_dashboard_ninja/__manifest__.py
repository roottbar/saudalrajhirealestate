# -*- coding: utf-8 -*-
{
    'name': 'Dashboard Ninja',
    
    'summary': """
Ksolves Dashboard Ninja gives you a wide-angle view of your business that you might have missed. Get smart visual data with interactive and engaging dashboards for your Odoo ERP. Odoo Dashboard, CRM Dashboard, Inventory Dashboard, Sales Dashboard, Account Dashboard, Invoice Dashboard, Revamp Dashboard, Best Dashboard, Odoo Best Dashboard, Odoo Apps Dashboard, Best Ninja Dashboard, Analytic Dashboard, Pre-Configured Dashboard, Create Dashboard, Beautiful Dashboard, Customized Robust Dashboard, Predefined Dashboard, Multiple Dashboards, Advance Dashboard, Beautiful Powerful Dashboards, Chart Graphs Table View, All In One Dynamic Dashboard, Accounting Stock Dashboard, Pie Chart Dashboard, Modern Dashboard, Dashboard Studio, Dashboard Builder, Dashboard Designer, Odoo Studio. Revamp your Odoo Dashboard like never before! It is one of the best dashboard odoo apps in the market.
""",
    
    'description': """
Dashboard Ninja v18.0 - Updated for Odoo 18 compatibility,
        Odoo Dashboard,
        Dashboard,
        Dashboards,
        Odoo apps,
        Dashboard app,
        HR Dashboard,
        Sales Dashboard,
        inventory Dashboard,
        Lead Dashboard,
        Opportunity Dashboard,
        CRM Dashboard,
        POS,
        POS Dashboard,
        Connectors,
        Web Dynamic,
        Report Import/Export,
        Date Filter,
        HR,
        Sales,
        Theme,
        Tile Dashboard,
        Dashboard Widgets,
        Dashboard Manager,
        Debranding,
        Customize Dashboard,
        Graph Dashboard,
        Charts Dashboard,
        Invoice Dashboard,
        Project management,
        ksolves,
        ksolves apps,
        Ksolves India Ltd.
        Ksolves India Limited,
        odoo dashboard apps
        odoo dashboard app
        odoo dashboard module
        odoo modules
        dashboards
        powerful dashboards
        beautiful odoo dashboard
        odoo dynamic dashboard
        all in one dashboard
        multiple dashboard menu
        odoo dashboard portal
        beautiful odoo dashboard
        odoo best dashboard
        dashboard for management
        Odoo custom dashboard
        odoo dashboard management
        odoo dashboard apps
        create odoo dashboard
        odoo dashboard extension
        odoo dashboard module
""",

    'author': 'Ksolves India Ltd.',
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': '363',
    'website': 'https://www.ksolves.com',
    'maintainer': 'Ksolves India Ltd.',
    'live_test_url': 'https://www.ksolves.com',
    'category': 'Productivity',
    'version': '18.0.1.0.7',
    'depends': ['base', 'web', 'base_setup'],
    'external_dependencies': {
        'python': [],
    },

    'assets': {
        'web.assets_backend': [
            'ks_dashboard_ninja/static/src/scss/ks_dashboard_ninja.scss',
            'ks_dashboard_ninja/static/src/css/ks_dashboard_ninja_item.css',
            'ks_dashboard_ninja/static/src/css/ks_icon_container_modal.css',
            'ks_dashboard_ninja/static/src/css/ks_dashboard_item_theme.css',
            'ks_dashboard_ninja/static/src/css/ks_dn_filter.css',
            'ks_dashboard_ninja/static/src/css/ks_toggle_icon.css',
            'ks_dashboard_ninja/static/src/css/ks_dashboard_options.css',
            'ks_dashboard_ninja/static/lib/css/gridstack.min.css',
            'ks_dashboard_ninja/static/src/js/ks_global_functions.js',
            'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja.js',
            'ks_dashboard_ninja/static/src/js/ks_to_do_dashboard.js',
            'ks_dashboard_ninja/static/src/js/ks_filter_props.js',
            'ks_dashboard_ninja/static/src/js/ks_color_picker.js',
            'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_item_preview.js',
            'ks_dashboard_ninja/static/src/js/ks_image_basic_widget.js',
            'ks_dashboard_ninja/static/src/js/ks_dashboard_item_theme.js',
            'ks_dashboard_ninja/static/src/js/ks_widget_toggle.js',
            'ks_dashboard_ninja/static/src/js/ks_import_dashboard.js',
            'ks_dashboard_ninja/static/src/js/ks_domain_fix.js',
            'ks_dashboard_ninja/static/src/js/ks_quick_edit_view.js',
            'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_kpi_preview.js',
            'ks_dashboard_ninja/static/src/js/ks_date_picker.js',
            'ks_dashboard_ninja/static/lib/js/gridstack-h5.js',
            'ks_dashboard_ninja/static/lib/js/Chart.bundle.min.js',
        ],
        'web.assets_frontend': [],
    },

    'data': [
        'security/ir.model.access.csv',
        'data/ks_default_data.xml',
        'views/ks_dashboard_ninja_view.xml',
        'views/ks_dashboard_ninja_item_view.xml',
        'views/ks_dashboard_ninja_assets.xml',
        'views/ks_to_do_view.xml',
        'views/ks_import_dashboard_view.xml',
    ],
    'demo': [
        'demo/ks_dashboard_ninja_demo.xml',
    ],
    'qweb': [
        'static/src/xml/ks_dashboard_ninja_templates.xml',
        'static/src/xml/ks_widget_template.xml',
        'static/src/xml/ks_dashboard_ninja_item_templates.xml',
        'static/src/xml/ks_quick_edit_view.xml',
        'static/src/xml/ks_import_list_view_template.xml',
        'static/src/xml/ks_to_do_template.xml',
        'static/src/xml/ks_color_picker.xml',
    ],
    'uninstall_hook': 'uninstall_hook',
    'installable': False,
    'auto_install': False,
    'application': True,
}
