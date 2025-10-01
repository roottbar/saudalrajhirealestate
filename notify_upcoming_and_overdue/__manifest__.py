# -*- coding: utf-8 -*-
{
    'name': "Notify Upcoming And OverDue",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Notify Upcoming And OverDue module",
    'description': "Enhanced Notify Upcoming And OverDue module for Odoo 18.0 by roottbar",
    'category': "Accounting/Accounting",
    'author': "plustech",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'account',
        'sale',
    ],
    'data': [
        'cron/cron.xml',
        'views/settings.xml',
        'views/move.xml',
        'views/mail.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}