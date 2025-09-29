# -*- coding: utf-8 -*-

{
    'name': 'Invoice Post,Draft and Cancel from List View.',
    'version': '15.0.1.0.0',
    'category': 'Accounting/Accounting',
    'license': 'LGPL-3',
    'summary': """Post your invoice/bill from list views and Multiple Cancel""",
    'depends': [
        'base',
        'account',
    ],
    'author': 'Naing Lynn Htun',
    'maintainer': 'roottbar',
    'support': 'konainglynnhtun@gmail.com',
    'description': """
        
        
        Enhanced Module
        
        
    - Post, Reset to Draft, Register Payment and cancel customer invoice from list view
    - Post, Reset to Draft, Register Payment and cancel vendor bill from list view
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'data': [
        'views/account_move.xml',
    ],
    'license': 'AGPL-3',
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
