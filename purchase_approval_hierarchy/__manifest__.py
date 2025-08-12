{
    'name': 'Purchase Approval Hierarchy',
    'version': '15.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Adds hierarchical approvals with permissions to Purchase Orders',
    'depends': ['purchase'],
    'data': [
        # 'security/ir.model.access.csv',  # يجب أن يكون أولاً
        'security/purchase_approval_security.xml',  # ثم أمان المجموعات
        'models/purchase_order.py',  # ملف النموذج قبل الواجهات
        'views/purchase_order_views.xml',  # أخيراً الواجهات
    ],
    'installable': True,
    'application': False,
}
