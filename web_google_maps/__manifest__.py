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
Web Google Map and google places autocomplete address form
==========================================================

This module brings two features:
1. Allows user to view all partners addresses on google maps.
2. Enabled google places autocomplete address form into partner
form view, provide autocomplete feature when typing address of partner
""",
    'depends': ['base', 'web'],
    'website': '',
    'data': [
        'data/google_maps_libraries.xml',
        'views/google_places_template.xml',
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
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}
