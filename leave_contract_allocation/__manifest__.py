# -*- coding: utf-8 -*-
{
    'name': "Leave Contract Allocation",
    'summary': """Leave Contract Allocation""",
    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""Adding an option at the level of the type of leave, in case it is selected,
     the leave will be linked to the employee’s contract - as when a year is completed,
     the employee’s balance will be zero
     """,
    'author': "Mahmoud Abdelaziz",
    'maintainer': 'roottbar',
    'category': 'Human Resources',
    'version': '18.0.0.1',
    'depends': ['hr_holidays', 'hr_contract'],
    'data': [
        'views/hr_leave_type.xml',
        'data/cron.xml',
    ]
}
