# -*- coding: utf-8 -*-

{
    'name': 'Print Payment',
    'version': '18.0.0.0',
    'category': 'accounting',
    'depends': ['base','account','invoice_templates'],
    'data': [
            'report/payment.xml',
    ],
    'installable': True,
    'auto_install': False,
    "images":["static/description/Banner.png"],
}
