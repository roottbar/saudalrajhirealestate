from odoo import models, fields

class RentalWizard(models.TransientModel):
    _name = 'rental.wizard'  # الاسم الذي كان مستخدم في _inherit
    _description = 'Rental Wizard (Mock)'

    duration_unit = fields.Selection([
        ('hour', 'Hours'),
        ('day', 'Days'),
        ('week', 'Weeks'),
        ('month', 'Months'),
        ('year', 'Years'),
    ], string="Unit", required=True)

    # أي حقول إضافية ضرورية عشان لا ينهار الكود
    name = fields.Char(string="Name")
