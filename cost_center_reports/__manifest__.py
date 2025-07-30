{
    'name': 'Cost Center Reports',
    'version': '15.0.1.0.0',
    'summary': 'Generate reports for cost centers including expenses, revenues, collections and debts',
    'description': """
        This module generates detailed reports for cost centers including:
        - Expenses by cost center
        - Revenues by cost center
        - Collections
        - Debts
    """,
    'category': 'Accounting',
    'author': 'Othmancs',
    'website': 'https://www.tbarholdingcs.com',
    'license': 'AGPL-3',
    'depends': ['base', 'report', 'account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'views/cost_center_report_views.xml',
        'reports/cost_center_report.xml',
        'reports/cost_center_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
