# -*- coding: utf-8 -*-
{
    'name': 'Transferred ID Fix',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Fix for transferred_id field missing in sale.order model',
    'description': """
        This module adds the missing transferred_id and related fields to the sale.order model
        to resolve view validation errors.
        
        الوحدة تضيف الحقول المفقودة transferred_id والحقول المرتبطة إلى نموذج sale.order
        لحل أخطاء التحقق من العرض.
    """,
    'author': 'Odoo Fix Team',
    'website': '',
    'depends': ['sale', 'payment'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}