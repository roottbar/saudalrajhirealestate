from odoo import api, fields, models

class IssuesWizard(models.Model):
    _name = "issues.wizard"
    _description = "Issues Details Wizard"


    date_from = fields.Date(string='Date from')
    date_to = fields.Date(string='Date to')

    def action_print_report(self):
        domain = []
        date_from=self.date_from
        if date_from:
            domain += [('date_of_the_invitation','>=',date_from)]
        date_to=self.date_to
        if date_to:
            domain += [('date_of_the_invitation', '<=', date_to)]
        details = self.env['issues'].search_read(domain)
        data= {
            'form_data': self.read()[0],
            'details':details
        }
        return self.env.ref('legal_management.action_issues_details').report_action(self, data=data)