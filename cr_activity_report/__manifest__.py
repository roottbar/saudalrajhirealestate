# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Generate Excel & PDF Report of Activity for Specific Users',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    'category': 'Sales,Mail',
    'summary': 'Generate PDF & Excel report of user activitys based on due date, type and range.',
    'license': 'LGPL-3',
    'version': '15.0',
    'description': """

Generate Excel & PDF Report For Activity Of Users will allow to
generate the PDF and Excel Report of user activity on bases of
activity type like Email, Call, etc, Due date and 
Range like less-then, grater-then, equal-to the due date added.

""",
    'depends': ["base", "sale"],
    'data': [
        "security/ir.model.access.csv",
        "wizard/activity_report_wizard_views.xml",
        "report/activity_report.xml",
        "report/activity_template.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "images": ["static/description/banner.png", ],
    "price": 0,
    "currency": "USD"
}
