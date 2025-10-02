# -*- coding: utf-8 -*-

{
    "name" : "Odoo Purchase Team Allocation",
    "author": "Edge Technologies",
    "version" : "15.0.1.0",
    "live_test_url":'https://youtu.be/H3cwPVEGO20',
    "images":["static/description/main_screenshot.png"],
    'summary': 'App purchase team purchase analysis team analysis for team in purchase report purchase team analysis purchase team reports team allocation in purchase purchase indent purchase user allocation purchase team report specific team for purchase order',
    "description": """
    
        Purchase team
        Purchase analysis team
        Analysis for team in purchase report
        Purchase team analysis
        Purchase team reports
        Team allolcation in purchase
        Purchase indent
        Purchase user allocation 




            Purchase team app helps user to assign a team to all the vendors as well as the rfq and purchase order. user can create a purchase team and assign team member and team leader. purchase team can be seen in the purchase analysis report.  
    
    """,
    "license" : "OPL-1",
    "depends" : ['base','purchase'],
    "data": [
        'security/ir.model.access.csv',
        'security/purchase_team_security.xml',
        'views/purchase_team_views.xml',
        'views/data.xml',
        'views/purchase_customer_views.xml',
        'views/purchase_config_views.xml',           
    ],
    "auto_install": False,
    "installable": True,
    "price": 0.00,
    "currency": 'EUR',
    "category" : "Purchase",   
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
