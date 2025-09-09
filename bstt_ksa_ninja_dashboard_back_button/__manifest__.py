# -*- coding: utf-8 -*-
{
    'name': "BSTT KSA Ninja Dashboard Add Back Button",

    'summary': "BSTT KSA Ninja Dashboard Add Back Button",

    'author': "BSTT Company",

    'website': "https://bstt.com.sa",

    'category': 'Test',

    'version': '18.0.0.1',  # تحديث رقم الإصدار
    'depends': [
        'base',
        'ks_dashboard_ninja',
    ],

    # تحديث من qweb إلى assets
    'assets': {
        'web.assets_backend': [
            'bstt_ksa_ninja_dashboard_back_button/static/src/xml/bstt_ksa_ninja_dashboard_back_button.xml',
        ]
    },
    # إزالة 'qweb' القديم
    'data': [],

    'demo': [],
    
    'qweb': [
        'static/src/xml/bstt_ksa_ninja_dashboard_back_button.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
