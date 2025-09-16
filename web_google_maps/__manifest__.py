# -*- coding: utf-8 -*-
{
    'name': 'Web Google Maps',
    'version': '18.0.1.0.0',
    'author': 'Yopi Angi',
    'license': 'AGPL-3',
    'maintainer': 'Yopi Angi<yopiangi@gmail.com>',
    'support': 'yopiangi@gmail.com',
    'category': 'Extra Tools',
    'description': """
Web Google Map and Google Places autocomplete address form
==========================================================

Features:
1. View all partners' addresses on Google Maps.
2. Enable Google Places autocomplete in partner form for addresses.
""",
    'depends': ['base', 'web'],
    'data': [
        'data/google_maps_libraries.xml',
        'views/res_partner.xml',
        'views/res_config_settings.xml',
    ],
    'demo': [],
    'images': ['static/description/thumbnails.png'],
    'assets': {
        'web.assets_backend': [
            'web_google_maps/static/src/js/**/*.js',
            'web_google_maps/static/src/xml/**/*.xml',
            'web_google_maps/static/src/css/**/*.css',
        ],
        'web.assets_frontend': [
            'web_google_maps/static/src/js/**/*.js',
            'web_google_maps/static/src/css/**/*.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
