# -*- coding: utf-8 -*-
{
    'name': "Contacts Maps",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Contacts Maps module",
    'description': "Enhanced Contacts Maps module for Odoo 18.0 by roottbar",
    'category': "Tools",
    'author': "Yopi Angi",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'contacts',
        'base_geolocalize',
        'web_google_maps',
        'google_marker_icon_picker',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}