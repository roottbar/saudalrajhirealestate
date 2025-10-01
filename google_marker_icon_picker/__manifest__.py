# -*- coding: utf-8 -*-
{
- New widget `google_marker_picker` allowing user to assign marker's color
  manually. To apply the selecter marker on map, you can tell map view by
  adding attribute color='[field_name]'

    "depends": ["web_google_maps"],
    "assets": {
        "web.assets_backend": [
            "/google_marker_icon_picker/static/src/js/view/google_map/google_map_view.js",
            "/google_marker_icon_picker/static/src/js/view/google_map/google_map_renderer.js",
            "/google_marker_icon_picker/static/src/js/widget/field_marker.js",
        ],
        "web.assets_qweb": [
            "/google_marker_icon_picker/static/src/xml/marker_color.xml"
        ],
    },
    "website": "",
    "data": [],
    "demo": [],
    "installable": True,
}
    'name': "Google Marker Icon Picker",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Google Marker Icon Picker module",
    'description': "Enhanced Google Marker Icon Picker module for Odoo 18.0 by roottbar",
    'category': "Extra Tools",
    'author': "Yopi Angi",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'web_google_maps',
    ],
    'data': [],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}
