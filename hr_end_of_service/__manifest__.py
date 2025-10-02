# -*- coding: utf-8 -*-
{
    'name': "HR End Of Service",
    'version': "18.0.1.0.0",
    'summary': "Enhanced HR End Of Service module",
    'description': "Enhanced HR End Of Service module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Crevisoft Corporate",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'hr_payroll',
        'hr_holidays',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/salary_rules.xml',
        'data/ir_sequence.xml',
        'data/mail_subtypes.xml',
        'wizard/reject_reason_wizard_view.xml',
        'views/hr_end_service_views.xml',
        'views/hr_payslip.xml',
        'views/hr_holiday.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}
