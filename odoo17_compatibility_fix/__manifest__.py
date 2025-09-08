# -*- coding: utf-8 -*-
{
    'name': 'Odoo 17.0 Compatibility Fix',
    'version': '17.0.1.0.0',
    'category': 'Technical',
    'summary': 'Fix compatibility issues for Odoo 17.0+ validation errors',
    'description': '''
        This module fixes validation errors in Odoo 17.0+ by:
        - Adding missing fields (transferred_id, locked, authorized_transaction_ids)
        - Adding missing methods (payment_action_capture, payment_action_void, resume_subscription)
        - Providing proper view definitions for sale.order model
    ''',
    'author': 'Custom Development',
    'website': '',
    'depends': [
        'base',
        'sale',
        'payment',
        'account',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}