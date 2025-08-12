# -*- coding: utf-8 -*-
{
    'name': 'Partner Identity Number',
    'version': '15.0.1.0.0',
    'summary': 'Add Identity/Residence number to partners with rental validation',
    'description': """
        This module adds:
        - Identity/Residence number field to partners (10 digits, required, unique)
        - Inherited field in sale_renting module
        - Workflow approval for price reduction in rental orders
        - Manager approval permissions
    """,
    'author': 'Custom Development',
    'depends': ['base', 'sale', 'mail'],    
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'data/approval_workflow.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
