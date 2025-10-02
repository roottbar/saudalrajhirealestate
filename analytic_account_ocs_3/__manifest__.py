{
    'name': 'تقرير مراكز التكلفة',
    'version': '15.0.1.0.0',
    'summary': 'تقرير مفصل عن المصروفات والإيرادات والتحصيل والمديونية حسب مراكز التكلفة',
    'description': """
        تقرير مراكز التكلفة
        ==================

        هذا التقرير يقوم بحساب:
        - المصروفات حسب مراكز التكلفة
        - الإيرادات حسب مراكز التكلفة
        - التحصيل حسب مراكز التكلفة
        - المديونية حسب مراكز التكلفة

        مع إمكانية تصدير التقرير إلى Excel أو PDF
    """,
    'author': 'othmancs',
    'website': 'https://www.tbarholdingocs.com',
    'category': 'Accounting',
    'depends': ['base', 'account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'views/analytic_account_report_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'sequence': 1,
}
