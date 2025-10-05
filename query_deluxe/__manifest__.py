# -*- coding: utf-8 -*-
{
    'name': "PostgreSQL Query Deluxe",
    'version': "18.0.1.0.0",
    'summary': "Execute PostgreSQL queries from Odoo interface - DEVELOPMENT ONLY",
    'description': """
PostgreSQL Query Deluxe - DEVELOPMENT/DEBUGGING TOOL ONLY
==========================================================

⚠️ SECURITY WARNING ⚠️
----------------------
This module allows direct execution of PostgreSQL queries from the Odoo interface.

**This module should NEVER be installed in production environments or on Odoo.sh!**

Risks:
------
* Direct database access bypasses Odoo security and access controls
* Can expose sensitive data
* Allows destructive operations (DELETE, DROP, ALTER)
* Not suitable for managed hosting environments like Odoo.sh
* May violate hosting provider security policies

Recommended Use:
----------------
* Local development environments only
* Database debugging and analysis
* Advanced troubleshooting by experienced developers
* Should be disabled/uninstalled before deploying to production

For Odoo.sh deployments:
-------------------------
Keep this module disabled (installable=False) to prevent security issues.
    """,
    'category': "Hidden",
    'author': "Yvan Dotet",
    'maintainer': "roottbar",
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/query_deluxe_views.xml',
        'wizard/pdforientation.xml',
        'report/print_pdf.xml',
        'datas/data.xml',
    ],
    'license': "LGPL-3",
    'application': False,
    'installable': False,  # Disabled by default for security - enable only in dev environments
    'auto_install': False,
}

