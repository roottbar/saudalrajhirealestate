# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResBranch(models.Model):
    _name = 'res.branch'
    _description = 'Branch'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True)
    telephone = fields.Char(string='Telephone No')
    address = fields.Text('Address')
    vat = fields.Char(string="Tax ID")
    company_registry = fields.Char(string="Company Registry")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    website = fields.Char(string="Website")
