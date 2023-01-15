{
    "name": "Easy Operating Unit Switching",

    "summary": """
        User With Multiple Operating Unit (OU) Can Easily Switch From Menu""",
    "version": "12.0.1",
    "author": "VaNnErI",
    "category": "Generic",
    "depends": ["web", "operating_unit"],
    "license": "LGPL-3",
    "data": [
        "views/web_switch_operating_units.xml",
    ],
    "qweb": [
        "static/src/xml/switch_op.xml",
    ],
    "images": ['static/description/Banner.png'],
    "installable": True,
    "application": False
}
