# -*- coding: utf-8 -*-
{
    'name': "Notify Upcoming And OverDue",
    'summary': """Notify Upcoming And OverDue""",
    'author': "plustech",
    'website': "",
    'category': 'Accounting/Accounting',
    'version': '0.1',
    'depends': ['base', 'account', 'sale'],
    'data': [
        'cron/cron.xml',
        'views/settings.xml',
        'views/move.xml',
        'views/mail.xml',
    ]
}
