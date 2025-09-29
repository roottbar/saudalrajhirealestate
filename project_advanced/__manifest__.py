# -*- coding: utf-8 -*-
{
    'name': "Project Advanced",

    'summary': """
        Template stages for projects""",

    'description': """
        Template stages for projects
    """,

    'author': "Crevisoft",
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hidden',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['project_forecast', 'project_enterprise', 'hr_contract', 'hr_timesheet', 'web_dashboard'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/sequence.xml',
        'views/project_views.xml',
        'views/project_task.xml',
        'views/project_template_views.xml',
        'views/project_task_type.xml',
        'views/res_config_settings.xml',
        'wizard/change_allow_user_task_view.xml',
        'wizard/task_assign_history_wizard_view.xml'
    ],
}
