{
    'name': 'User Activity Log',
    'version': '15.0.1.0.0',
    'summary': 'Track and log user activities in the system',
    'description': """
        This module tracks and logs all user activities including create, write, unlink operations
        with date, time, user and model information.
    """,
    'author': 'Othmancs',
    'website': 'https://www.Tbarholding.com',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/user_log_views.xml',
        'views/user_log_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}