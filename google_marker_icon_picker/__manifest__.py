# -*- coding: utf-8 -*-
{
    'name': "Google Marker Icon Picker",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Google Marker Icon Picker module",
    'description': """
        New widget `google_marker_picker` allowing user to assign marker's color
        manually. To apply the selecter marker on map, you can tell map view by
        adding attribute color='[field_name]'
        
        Updated by roottbar for better functionality.
        Enhanced by roottbar.
    """,
    'category': "Extra Tools",
    'author': "Yopi Angi",
    'maintainer': "roottbar",
    'website': "",
    'depends': [
        'base',
        # 'web_google_maps',  # Commented out - module not installable
    ],
    'assets': {
        'web.assets_backend': [
            '/google_marker_icon_picker/static/src/js/view/google_map/google_map_view.js',
            '/google_marker_icon_picker/static/src/js/view/google_map/google_map_renderer.js',
            '/google_marker_icon_picker/static/src/js/widget/field_marker.js',
        ],
        'web.assets_qweb': [
            '/google_marker_icon_picker/static/src/xml/marker_color.xml'
        ],
    },
    'data': [],
    'demo': [],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}