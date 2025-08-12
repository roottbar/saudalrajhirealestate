{
    'name': 'Purchase Approval Workflow',
    'version': '15.0.1.0.0',
    'summary': 'نظام الموافقات الهرمية لأوامر الشراء',
    'description': """
        نظام متكامل لإدارة ثلاث مستويات من الموافقات على أوامر الشراء
    """,
    'author': 'Othmancs',
    'website': 'https://www.Tbarholding.com',
    'category': 'Purchases',
    'depends': ['purchase'],
    'data': [
        'security/approval_groups.xml',
        'security/ir.model.access.csv',
        'views/approval_config_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}