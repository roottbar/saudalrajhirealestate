# -*- coding: utf-8 -*-
{
    'name': "Task Deadline Reminder",
    'version': "18.0.1.0.0",
    'summary': "Enhanced Task Deadline Reminder module",
    'description': "Enhanced Task Deadline Reminder module for Odoo 18.0 by roottbar",
    'category': "Project",
    'author': "Cybrosys Techno Solutions",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'project',
    ],
    'data': [
        'views/deadline_reminder_view.xml',
        'views/deadline_reminder_cron.xml',
        'data/deadline_reminder_action_data.xml',
    ],
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}