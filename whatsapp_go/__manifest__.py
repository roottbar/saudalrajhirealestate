# -*- coding: utf-8 -*-
{
    'name': "Go4whatsup",
    'category': 'Extra Tools',
    'summary': 'Send quotations and invoices directly to customers via WhatsApp, with automatic PDF sharing upon confirmation. Requires a Go4WhatsApp subscription available at Go4WhatsApp.',
    'description': """
        
        
        Enhanced Module
        
        
        This module allows you to directly send quotations and invoices to customers via WhatsApp. Once the quotation or invoice is confirmed, the system automatically generates and shares a PDF of the document with the customer. To enable this feature, a Go4WhatsApp subscription is required. You can access the subscription through their website at Go4WhatsApp 'https://app.go4whatsup.com/'.
        This integration streamlines the process, making it easier to communicate with customers and share important documents quickly and efficiently.
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'author': "Inwizards software Technology Pvt Ltd",
    'maintainer': 'roottbar',
    'website': "https://www.inwizards.com/",
    'version': '15.0.1.0',
    'depends': ['base', 'sale'],
    "license": "AGPL-3",
    'live_test_url': 'https://pos.onlineemenu.com/web/login?db=whatsapp_go',
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/cron_job.xml',
        'views/views.xml',
        'views/whatsapp.xml',
        'views/res_config.xml'
    ],
   "images" : ['static/description/banner.gif']
}

