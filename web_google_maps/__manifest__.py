# -*- coding: utf-8 -*-
{

This module brings two features:
1. Allows user to view all partners addresses on google maps.
2. Enabled google places autocomplete address form into partner
form view, provide autocomplete feature when typing address of partner

        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.

    'depends': ['base_setup', 'base_geolocalize'],
    'website': '',
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