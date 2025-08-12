{
    'name': 'Purchase Approval Hierarchy',
    'version': '15.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Adds hierarchical approvals with permissions to Purchase Orders',
    'depends': ['purchase'],
    'data': [
        'security/purchase_approval_security.xml',
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
}