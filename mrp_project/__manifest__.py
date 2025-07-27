# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Project Link",
    "summary": "Link production with projects",
    "version": "15.0.1.2.1",
    "depends": [
        "mrp_analytic",
        "project",
        "hr_timesheet",
        "stock",
    ],
    'license': 'AGPL-3',
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "Antiun Ingeniería S.L.,"
              "Odoo Community Association (OCA)",
    "category": "Manufacturing",
    'data': [
        "views/mrp_production_view.xml",
        "views/project_project_view.xml",
        "views/account_analytic_line_view.xml",
        "views/project_task_view.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
