{
    'name': 'Fix Timesheet Portal _compute_domain',
    'version': '15.0',
    'category': 'Accounting',
    'summary': 'Fixes TypeError in Timesheet portal due to _compute_domain missing mode',
    'description': """
        This module fixes the issue when opening portal invoices
        where hr_timesheet _compute_domain() was missing required argument 'mode'.
    """,
    'author': 'Your Name',
    'depends': ['hr_timesheet', 'sale_timesheet', 'sale_timesheet_enterprise', 'account'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
