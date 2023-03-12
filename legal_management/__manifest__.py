{
    'name': 'Legal Management ',
    'sequence': -101,

    'depends': ['mail','sale'],
    'data':[
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/cron_scheduler.xml',
        'data/send_notification.xml',
        'wizard/issues_details_views.xml',
        'views/menu.xml',
        'views/issues_views.xml',
        'views/type_court_views.xml',
        'views/hearing_views.xml',
        'views/appeal_views.xml',
        'views/contract_views.xml',
        'views/implementation_views.xml',
        'views/power_of_attorney_views.xml',
        'views/promissory_note_views.xml',
        'views/investigation_views.xml',
        'views/res_config_settings_views.xml',
        'report/report.xml',
        'report/issues_details.xml',
        'report/report_issues_view.xml',
    ],

}
