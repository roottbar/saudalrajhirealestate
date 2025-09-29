{
    'name': 'Suprema Biometric Integration',
    'version': '15.0.1.0.0',
    'summary': 'Integration with Suprema Biometric Devices',
    'description': """
        
        
        Enhanced Module
        
        
        This module integrates Odoo with Suprema biometric devices
        to manage employee attendance automatically.
    
        
        Updated by roottbar for better functionality.
    
        
        Enhanced by roottbar.
    """,
    'author': 'Your Company',
    'maintainer': 'roottbar',
    'website': 'https://www.yourcompany.com',
    'category': 'Human Resources',
    'depends': ['web', 'hr', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        'views/device_views.xml',
        'views/attendance_views.xml',
        # 'views/templates.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'suprema_attendance/static/src/js/suprema_connection.js',
        ],
    },
    'external_dependencies': {
        'python': ['pyzk'],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
