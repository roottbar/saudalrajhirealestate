{
    'name': "PDF AI Invoice Processor",
    'version': '18.0.1.0.0',
    'author': "Othmancs",
    'maintainer': 'roottbar',
    'category': 'Accounting',
    'summary': "Extract payment data from PDF using AI",
    'description': "
        
        Updated for Odoo 18.0 - 2025 Edition""
        This module extracts payment schedule data from PDF files
        and updates invoice records with paid invoice counts.
    """,
    'depends': ['account'],
    'data': [
        'views/invoice_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}