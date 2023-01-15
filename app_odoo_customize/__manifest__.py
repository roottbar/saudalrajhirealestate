# -*- coding: utf-8 -*-

# Created on 2018-11-26
# author: 广州尚鹏，https://www.sunpop.cn
# email: 300883@qq.com
# resource of Sunpop
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Odoo12在线用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/12.0/en/index.html

# Odoo12在线开发者手册（长期更新）
# https://www.sunpop.cn/documentation/12.0/index.html

# Odoo10在线中文用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.sunpop.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.sunpop.cn/odoo10_developer_document_offline/
# description:

{
    'name': 'odoo 16,15 Customize OEM(Boost, Data reset)',
    'version': '15.22.09.28',
    'author': 'Sunpop.cn',
    'category': 'Productivity',
    'website': 'https://www.sunpop.cn',
    'license': 'LGPL-3',
    'sequence': 2,
    'images': ['static/description/banner.gif'],
    'summary': """
    1 click customize odoo, reset data. For quick develop. Set brand, boost, reset data, debug. Language Switcher.
    Easy Delete data.reset account chart.
    customize my odoo.
    """,
    'depends': [
        'base_setup',
        'web',
        'mail',
        'iap',
        # 'digest',
        # when enterprise
        # 'web_mobile'
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/app_odoo_customize_views.xml',
        'views/app_theme_config_settings_views.xml',
        'views/res_config_settings_views.xml',
        'views/ir_views.xml',
        'views/ir_module_module_views.xml',
        'views/ir_translation_views.xml',
        'views/ir_ui_menu_views.xml',
        'views/ir_ui_view_views.xml',
        'views/ir_model_fields_views.xml',
        'views/ir_model_data_views.xml',
        # data
        'data/ir_config_parameter_data.xml',
        'data/ir_module_module_data.xml',
        # 'data/digest_template_data.xml',
        'data/res_company_data.xml',
    ],
    # 'qweb': [
    #     'static/src/xml/*.xml',
    # ],
    'assets': {
        'web.assets_backend': [
            'app_odoo_customize/static/src/scss/app.scss',
            'app_odoo_customize/static/src/scss/ribbon.scss',
            'app_odoo_customize/static/src/scss/dialog.scss',
            'app_odoo_customize/static/src/js/app_window_title.js',
            'app_odoo_customize/static/src/js/user_menu.js',
            # 'app_odoo_customize/static/src/js/ribbon.js',
            'app_odoo_customize/static/src/js/dialog.js',
        ],
    },
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': True,

}
