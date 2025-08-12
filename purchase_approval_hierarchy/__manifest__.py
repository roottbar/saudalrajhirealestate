{
    'name': 'Purchase Approval Hierarchy',
    'version': '15.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Adds hierarchical approvals with permissions to Purchase Orders',
    'depends': ['purchase'],
    'data': [  # لملفات البيانات فقط (XML, CSV)
        # 'security/ir.model.access.csv',
        'security/purchase_approval_security.xml',
        'views/purchase_order_views.xml',
    ],
    'demo': [],  # ملفات البيانات للوضع التجريبي
    'installable': True,
    'application': False,
    'auto_install': False,
}
