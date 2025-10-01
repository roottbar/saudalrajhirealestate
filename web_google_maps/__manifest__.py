# -*- coding: utf-8 -*-
{
    'name': "Web Google Maps",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Web Google Maps module",
    'description': """
        This module brings two features:
        1. Allows user to view all partners addresses on google maps.
        2. Enabled google places autocomplete address form into partner
        form view, provide autocomplete feature when typing address of partner
        
        Updated by roottbar for better functionality.
        Enhanced by roottbar.
    """,
    'category': "Extra Tools",
    'author': "Yopi Angi",
    'maintainer': "roottbar",
    'website': "",
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
    'assets': {
        'web.assets_common': [
            'web_google_maps/static/src/js/widgets/utils.js',
            'web_google_maps/static/src/js/widgets/gplaces_autocomplete.js',
            'web_google_maps/static/src/js/widgets/fields_registry.js',
            'web_google_maps/static/src/js/view/view_registry.js',
            'web_google_maps/static/src/js/view/google_map/google_map_view.js',
            'web_google_maps/static/src/js/view/google_map/google_map_sidebar.js',
            'web_google_maps/static/src/js/view/google_map/google_map_renderer.js',
            'web_google_maps/static/src/js/view/google_map/google_map_model.js',
            'web_google_maps/static/src/js/view/google_map/google_map_controller.js',
            'web_google_maps/static/src/js/view/form/form_view.js',
            'web_google_maps/static/src/js/view/form/form_controller.js',
            'web_google_maps/static/src/js/fields/relational_fields.js',
        ],
    },
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}