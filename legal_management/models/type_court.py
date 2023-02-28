from odoo import api, fields, models

class TypeCourt(models.Model):
    _name = "type.court"
    _description = "Type of Court"
    _rec_name ="type_court"


    type_court = fields.Char(string='Type of courts')