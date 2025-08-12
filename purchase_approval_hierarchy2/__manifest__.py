{
    'name': 'Purchase Approval Hierarchy',
    'version': '15.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Adds hierarchical approvals for purchase orders',
    'description': """
        Multi-level approval workflow for purchase orders
    """,
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'depends': ['purchase'],
    'data': [
        'security/purchase_approval_security.xml',
        'views/purchase_order_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}