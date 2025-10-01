# -*- coding: utf-8 -*-
{
        
        هذا الموديول يوفر:
        * حساب تصفية نهاية الخدمة حسب قانون العمل السعودي
        * حساب تصفية الإجازة السنوية (22 يوم من الراتب الشهري)
        * منع التصفية المتكررة للموظف الواحد
        * تقارير PDF وExcel للتصفيات
        * إدارة كاملة لعمليات نهاية الخدمة
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'author': 'Othmancs',
    'maintainer': 'roottbar',
    'website': 'https://www.Othmancs.com',
    'name': "HR End of Service Saudi Arabia",
    'version': "18.0.1.0.0",
    'summary': "Enhanced HR End of Service Saudi Arabia module",
    'description': "Enhanced HR End of Service Saudi Arabia module for Odoo 18.0 by roottbar",
    'category': "Human Resources",
    'author': "Othmancs",
    'maintainer': "roottbar",
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
    'license': "LGPL-3",
    'installable': False,
    'auto_install': False,
}