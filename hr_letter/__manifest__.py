# -*- coding: utf-8 -*-
{
    'name': "HR Letter",

    'summary': """Letter For Employee""",

    'description': """
        Letter For Employee
    """,
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['hr','hr_contract','bstt_hr'],

    # always loaded
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'report/hr_letter.xml',
        'views/hr_letter.xml',
        'views/hr_employee.xml',
    ]
}
