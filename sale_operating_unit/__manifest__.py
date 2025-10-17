# -*- coding: utf-8 -*-
{
    'name': "Operating Unit in Sales",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Operating Unit in Sales module",
    'description': "Enhanced Operating Unit in Sales module for Odoo 18.0 by roottbar",
    'category': "Sales Management",
    'author': "Eficent, Serpent Consulting Services Pvt. Ltd.,Odoo Community Association (OCA)",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'sale',
        'sale_renting',
        'sales_team_operating_unit',
    ],
    'data': [
        'security/sale_security.xml',
        'views/sale_view.xml',
        'views/sale_report_view.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}