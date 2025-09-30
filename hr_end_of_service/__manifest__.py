# -*- coding: utf-8 -*-
{
    'name': "HR End Of Service",
    'summary': """HR End Of Service""",
    'author': "Crevisoft Corporate",
    'maintainer': 'roottbar',
    'website': "https://www.crevisoft.com",

    'category': 'Human Resources',
    'version': '15.0.1.0',
    'installable': False,  # Requires hr_payroll (Enterprise module)

    'depends': ['hr_payroll', 'hr_holidays'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/salary_rules.xml',
        'data/ir_sequence.xml',
        'data/mail_subtypes.xml',
        'wizard/reject_reason_wizard_view.xml',
        'views/hr_end_service_views.xml',
        'views/hr_payslip.xml',
        'views/hr_holiday.xml'
    ]
}
