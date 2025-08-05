from odoo import models, fields, api

class RentalReportWizard(models.TransientModel):
    _name = 'rental.report.wizard'
    _description = 'Rental Report Wizard'

    company_id = fields.Many2one('res.company', string='Company', required=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')
    property_address_build = fields.Char(string='Building Address')
    property_id = fields.Many2one('property.property', string='Property')
    
    def generate_report(self):
        data = {
            'company_id': self.company_id.id,
            'operating_unit_id': self.operating_unit_id.id,
            'property_address_build': self.property_address_build,
            'property_id': self.property_id.id,
            'form_data': self.read()[0],
        }
        return self.env.ref('rental_reports.action_rental_report').report_action(self, data=data)