{
    'name': "PDF AI Invoice Processor",
    'version': '15.0.1.0.0',
    'author': "Othmancs",
    'maintainer': 'roottbar',
    'category': 'Accounting',
    'summary': "Extract payment data from PDF using AI",
    'description': """
        
        
        Enhanced Module
        
        
        This module extracts payment schedule data from PDF files
        and updates invoice records with paid invoice counts.
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'depends': ['account'],
    'data': [
        'views/invoice_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}