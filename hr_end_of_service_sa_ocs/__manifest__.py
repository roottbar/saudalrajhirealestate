# -*- coding: utf-8 -*-
{
    'name': 'HR End of Service Saudi Arabia',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'تصفية نهاية الخدمة والإجازة السنوية حسب النظام السعودي',
    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
        HR End of Service Saudi Arabia
        ==============================
        
        هذا الموديول يوفر:
        * حساب تصفية نهاية الخدمة حسب قانون العمل السعودي
        * حساب تصفية الإجازة السنوية (22 يوم من الراتب الشهري)
        * منع التصفية المتكررة للموظف الواحد
        * تقارير PDF وExcel للتصفيات
        * إدارة كاملة لعمليات نهاية الخدمة
    """,
    'author': 'Othmancs',
    'maintainer': 'roottbar',
    'website': 'https://www.Othmancs.com',
    'depends': [
        'base',
        'hr',
        'hr_contract',
        'hr_holidays',
        'mail',
        'report_xlsx',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_end_of_service_views.xml',
        'views/hr_annual_leave_settlement_views.xml',
        'views/wizard_views.xml',
        'reports/reports.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
