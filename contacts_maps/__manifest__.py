# -*- coding: utf-8 -*-
{
    'name': "Contacts Maps",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Contacts Maps module",
    'description': """
        Added Google Map view on contacts
        
        Updated by roottbar for better functionality.
        Enhanced by roottbar.
    """,
    'category': "Tools",
    'author': "Yopi Angi",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'contacts',
        'base_geolocalize',
        # 'web_google_maps',  # Commented out - module not installable
        'google_marker_icon_picker',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}