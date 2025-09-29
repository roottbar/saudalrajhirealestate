# -*- coding: utf-8 -*-
{
    'name': 'Partner Ledger Reports in XLS and PDF',
    'description': """
        
        
        Enhanced Module
        
        
            Partner Ledger Reports in XLS and PDF
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'summary': 'Partner Ledger Reports in XLS and PDF',
    'version': '15.0.1.0',
    'category': 'Accounting',
    'author': 'Othmancs.',
    'company': 'Tbarholding.',
    'maintainer': 'Tbarholding',
    'website': "https://www.Tbarholding.com",
    'depends': [
        'contacts', 'account',
    ],
    'data': [
        #  security
        'security/ir.model.access.csv',
        # report
        'report/partner_ledger_pdf_report.xml',
        # wizard
        'wizard/partner_ledger_report_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
