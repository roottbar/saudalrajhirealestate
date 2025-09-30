# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Migrated by roottbar on 2025-01-30
# © 2016-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base UBL",
    "version": "18.0.1.6.0",
    "category": "Hidden",
    "license": "AGPL-3",
    "summary": "Base module for Universal Business Language (UBL)",
    "author": "Akretion,Onestein,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi",
    "depends": ["uom_unece", "account_tax_unece", "base_vat", "pdf_helper"],
    "external_dependencies": {"python": ["PyPDF2"]},
    "installable": True,
}
