# -*- coding: utf-8 -*-
{
    'name': "Web Google Maps",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Web Google Maps module",
    'description': "Enhanced Web Google Maps module for Odoo 18.0 by roottbar",
    'category': "Extra Tools",
    'author': "Yopi Angi",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'base_setup',
        'base_geolocalize',
    ],
    'data': [
        'data/google_maps_libraries.xml',
        'views/google_places_template.xml',
        'views/res_partner.xml',
        'views/res_config_settings.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}