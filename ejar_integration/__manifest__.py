# -*- coding: utf-8 -*-
{
    'name': "Ejar Platform Integration",
    'version': "15.0.1.0.0",
    'summary': """
        Integration with Saudi Arabia's Ejar Platform for Real Estate Rental Management
    """,
    'description': """
        This module provides comprehensive integration with the Ejar platform (https://www.ejar.sa/),
        the official Saudi Arabian electronic platform for real estate rental sector regulation.
        
        Key Features:
        - Synchronization with Ejar platform contracts
        - Automated contract registration and documentation
        - Real-time status updates and notifications
        - Compliance with Saudi rental regulations
        - Integration with existing renting module
        - Support for residential and commercial contracts
        - Electronic contract management
        - Automated renewal processes
        - Comprehensive reporting and analytics
    """,
    'author': "Othmancs",
    'website': "https://www.ejar.sa/",
    'category': 'Real Estate',
    'license': 'LGPL-3',
    
    # Dependencies
    'depends': [
        'base',
        'base_accounting_kit',
        'product',
        'einv_sa',
        'contacts',
        'mail',
        'portal'
    ],
    
    # Data files
    'data': [
        # Security
        'security/ejar_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/ejar_minimal_data.xml',
        
        # Views
        'views/ejar_menu.xml',
        'views/ejar_property_views.xml',
        'views/ejar_contract_views.xml',
        'views/ejar_tenant_views.xml',
        'views/ejar_landlord_views.xml',
        'views/ejar_sync_log_views.xml',
        'views/ejar_dashboard_views.xml',
    ],
    
    # Demo data
    'demo': [],
    
    # Assets
    'assets': {
        'web.assets_backend': [
            'ejar_integration/static/src/css/ejar_styles.css',
            'ejar_integration/static/src/js/ejar_dashboard.js',
        ],
    },
    
    # Installation
    'installable': True,
    'auto_install': False,
    'application': True,
    
    # External dependencies
    'external_dependencies': {
        'python': ['requests', 'cryptography', 'pyjwt'],
    },
}
