# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResBranch(models.Model):
    _inherit = 'res.branch'
    _description = 'Branch'

    # Keep only additional fields specific to this module to avoid redefining existing ones
    telephone = fields.Char(string='Telephone No')
    address = fields.Text('Address')
    vat = fields.Char(string="Tax ID")
    company_registry = fields.Char(string="Company Registry")
    # email, phone, website, name, and company_id are already defined in the base res.branch model
