# -*- coding: utf-8 -*-
{
    'name': "Facilities",

    'summary': """
        Contracts Management""",

    'description': """
        Contracts Management
    """,

    'author': "Crevisoft Corporate",
    'website': "https://www.crevisoft.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Project',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_accountant', 'project', 'planning', 'sale_timesheet', 'purchase_stock', 'crm',
                'accounting_category_partner', 'hr_payroll'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/tender_contract_types.xml',
        'data/tender_service_categories.xml',
        'data/quotation_term_condition.xml',
        'data/ir_sequence.xml',
        'wizard/tender_contract_check_analytic_account_views.xml',
        'wizard/tender_contract_validate_account_move_views.xml',
        'wizard/tender_contract_confirm_sale_order_views.xml',
        'wizard/tender_contract_confirm_purchase_order_views.xml',
        'wizard/tender_contract_validate_stock_picking_views.xml',
        'wizard/tender_quotation_version_views.xml',
        'wizard/tender_contract_invoice_report_views.xml',
        'views/tender_contract_type_views.xml',
        'views/tender_service_type_views.xml',
        'views/tender_service_category_views.xml',
        'views/tender_service_manpower.xml',
        'views/tender_branch_views.xml',
        'views/tender_project_category_views.xml',
        'views/tender_contract_category_views.xml',
        'views/tender_lead_views.xml',
        'views/planning_views.xml',
        'views/tender_contracts_views.xml',
        'views/tender_project_views.xml',
        'views/res_partner_account_category_views.xml',
        'views/crm_lead_views.xml',
        'views/tender_quotation_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/sales_views.xml',
        'views/purchases_views.xml',
        'views/stock_picking_views.xml',
        'views/project_views.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
        'views/hr_employee_views.xml',
        'views/res_config_view.xml',
        'views/templates.xml',
        'views/menuitems.xml',
        'report/report_tender_contract.xml',
        'report/report_tender_quotation.xml',
        'report/report_tender_lead.xml',
        'report/report_invoice_tender_contract.xml',
        'report/report_invoice.xml',
        'views/reports.xml',
    ],
    'web.assets_backend' :[
        '/static/src/js/tender_project.js',
        '/static/src/scss/tender_project.scss',
        
    ],
    'application': True,
}

