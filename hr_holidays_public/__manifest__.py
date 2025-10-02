# -*- coding: utf-8 -*-
{
    'name': "HR Holidays Public",
    'version': "18.0.1.0.0",
    'summary': "Enhanced HR Holidays Public module",
    'description': "Enhanced HR Holidays Public module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Michael Telahun Makonnen, Tecnativa, Fekete Mihai (Forest and Biomass Services Romania), Druidoo, Odoo Community Association (OCA),",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_holidays',
    ],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/hr_holidays_public_view.xml',
        'views/hr_leave_type.xml',
        'wizards/holidays_public_next_year_wizard.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}