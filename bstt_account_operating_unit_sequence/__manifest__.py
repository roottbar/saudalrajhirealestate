# -*- coding: utf-8 -*-
{
    'name': "BSTT Account Operating Unit Sequence",
    "version" : "15.0.0.1",
    "category" : "Accounting",
    'description': """
        
        
        Enhanced Module
        
        
       Account Operating Unit Sequence BSTT
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'author': "BSTT company",
    'maintainer': 'roottbar',
    'email': "info@bstt.com.sa ",
    'website': "https://bstt.com.sa",
    'category': 'Generic',
    'version': '15.0.1.0',
    'license': 'AGPL-3',
    'images': ['static/description/logo.png'],
    'depends': ['operating_unit','account', 'plustech_asset_enhance'],
    'data': [
        'views/operating_unit_view.xml',
        'views/account_move_view.xml',
    ],
}
