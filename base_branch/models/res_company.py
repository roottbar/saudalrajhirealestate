from odoo import fields, models, api

class Company(models.Model):
    _inherit = 'res.company'
    
    def get_domain(self):
        return [('company_id','=',self.env.company.id)]

    branch_id = fields.Many2one(comodel_name='branch.branch',domain=get_domain,string='Branch')
    