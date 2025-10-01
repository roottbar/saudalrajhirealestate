# -*- coding: utf-8 -*-
{
    'name': "Purchase Decimal Precision",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Purchase Decimal Precision module",
    'description': """
        This module extends the purchase order functionality to allow decimal precision
        up to 4 decimal places instead of the default 2 decimal places for:
        - Unit Price
        - Quantity
        - Subtotal

        Features:
        ---------
        * Increases decimal precision for purchase order line fields
        * Maintains compatibility with existing purchase workflows
        * Supports Arabic and English languages

        Installation:
        -------------
        1. Copy this module to your Odoo addons directory
        2. Update the app list
        3. Install the module

        Usage:
        ------
        After installation, you can enter decimal values with up to 4 decimal places
        in purchase order lines.
        
        Updated by roottbar for better functionality.
        Enhanced by roottbar.
    """,
    'category': "Purchase",
    'author': "Your Company",
    'maintainer': "roottbar",
    'website': "https://www.yourcompany.com",
    'depends': [
        'base',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/decimal_precision_data.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}
