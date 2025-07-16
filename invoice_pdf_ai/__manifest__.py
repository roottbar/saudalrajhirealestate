{
    'name': "PDF AI Invoice Processor",
    'version': '18.0.1.0.0',
    'author': "Othmancs",
    'category': 'Accounting',
    'summary': "Extract payment data from PDF using AI",
    'description': """
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
