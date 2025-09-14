# -*- coding: utf-8 -*-
{
    'name': 'Fix Template Inheritance Errors',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Fix XPath inheritance and template errors in Odoo 18',
    'description': """
        This module fixes template inheritance errors including:
        - XPath expressions targeting non-existent elements
        - Missing model references
        - Broken view inheritance chains
        - Invalid template syntax
    """,
    'author': 'Odoo Migration Helper',
    'depends': ['base', 'web'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': 'post_init_hook',
}