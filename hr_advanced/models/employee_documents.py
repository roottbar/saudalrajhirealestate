# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmployeeDocument(models.Model):
    _name = 'employee.document'
    _description = 'Employee Documents'

    name = fields.Char(string='Reference', copy=False)
    doc_type = fields.Selection([
        ('national_id', 'National ID'),
        ('visa', 'Visa'),
        ('iqama', 'Iqama'),
        ('driving_licence', 'Driving Licence'),],
         string='ID Type', index=True, copy=False,
        tracking=True)
    state = fields.Selection([
        ('run', 'Runnig'),
        ('expire', 'Expired')
        ,],
         string='Document State', index=True, copy=False,
        tracking=True,default='run')

    emp_id = fields.Many2one('hr.employee', copy=False, tracking=True,string='Employee')
    document_expire = fields.Date(string="Expiry Date")
    doc_file = fields.Binary(string='Document Attachment')


    @api.depends('barcode')
    def _compute_employee_ref(self):
        self.ref = self.barcode


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.employee.doc')
        return super(EmployeeDocument, self).create(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('emp_id', operator, name), ('name', operator, name)] + args
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
