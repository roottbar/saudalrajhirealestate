# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Migrated by roottbar on 2025-01-30
# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# TODO: move it to a simple python package under OCA umbrella?
{
    "name": "PDF Helper",
    "version": "18.0.1.1.0",
    "category": "Tools",
    "license": "LGPL-3",
    "summary": "Provides helpers to work w/ PDFs",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["simahawk", "alexis-via"],
    "website": "https://github.com/OCA/edi",
    "depends": [
        "base",
    ],
    "external_dependencies": {"python": ["PyPDF2"]},
    "installable": True,
    "application": False,
    "auto_install": False,
}
