# -*- coding: utf-8 -*-

{
    'name': 'PlusTech HR Employee',
    'version': '18.0.1.0.0',
    'author': 'Plus Technology Team',
    'maintainer': 'roottbar',
    'company': 'Plus Technology',
    'category': 'Human Resources/Employees',
    'website': "www.plustech-it.com",
    'description': """
        
        
        Enhanced Module
        
        manage employees data
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'summary': """employees module localization""",
    'depends': ['base', 'hr', 'resource', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'sequence/employee_sequence.xml',
        'views/hr_employee_view.xml',
        'views/hr_notification.xml',
        'views/hr_setting.xml',
        'views/hr_check_list_view.xml',
        'views/hr_employee_religion.xml',
        'data/mail_activity.xml',
        'data/server_action.xml',
        'data/mail_template.xml',
    ],
    'sequence': 20,
    'demo': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
