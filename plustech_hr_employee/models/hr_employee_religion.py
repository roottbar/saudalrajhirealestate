from odoo import fields, models, api


class ResReligion(models.Model):
    _name = 'employee.religion'
    _description = 'Res Religion'

    name = fields.Char(translate=True)
