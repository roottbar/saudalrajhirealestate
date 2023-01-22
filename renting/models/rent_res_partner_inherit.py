# -*- coding: utf-8 -*-

from odoo import models, fields


class RentResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    # Fields will be added in case of a Company
    commercial_number = fields.Char(string='Commercial No.')
    commercial_number_date = fields.Date(string='Commercial No. Date')

    agency_number = fields.Char(string='Agency No.')
    agency_number_date = fields.Date(string='Agency No. Date')

    # Fields will be added in case of an Individual
    national_id_image = fields.Binary(string='National ID')
    national_id_number = fields.Char(string='National ID No.')
    date_o_birth = fields.Date(string='Date of Birth')
    function_document = fields.Binary(string='البيان الوظيفي')
