# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons.base.models.ir_model import FIELD_TYPES
from odoo.exceptions import ValidationError


class ReportTemplate(models.Model):
    _name = 'xlsx.report.template'
    _description = 'Report Template'

    name = fields.Char(required=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    file_name = fields.Char()
    mapping_ids = fields.One2many('xlsx.template.mapping.line', 'xlsx_template_id', string='Mapping')
    report_id = fields.Many2one('ir.actions.report', string='Report', readonly=True)
    type = fields.Selection([('xlsx', 'XLSX'), ('qweb-pdf', 'PDF'), ], required=True, default="xlsx")
    paperformat_id = fields.Many2one('report.paperformat', 'Paper format', default=lambda self: self.env.ref('base.paperformat_euro', raise_if_not_found=False))


    @api.onchange('model_id')
    def onchange_model_id(self):
        self.mapping_ids = False

    @api.model
    def create(self, vals):
        res = super(ReportTemplate, self).create(vals)
        res.add_report()
        return res

    def write(self, vals):
        res = super(ReportTemplate, self).write(vals)
        self.add_report()
        return res

    def add_report(self):
        vals = {
            'name': self.name,
            'report_file': self.name,
            'xlsx_template_id': self.id,
            'report_type': self.type,
            'report_name': 'dynamic_xlsx_report.dynamic_pdf_report',
            'model': self.model_id.model,
            'paperformat_id': self.paperformat_id.id,
            'dynamic_xlsx_report': True,
        }
        if self.report_id:
            self.report_id.update(vals)
        else:
            report = self.env['ir.actions.report'].create(vals)
            report.create_action()
            self.report_id = report.id


class TemplateMappingLine(models.Model):
    _name = 'xlsx.template.mapping.line'
    _description = 'Template Mapping Line'

    @api.onchange('field_id')
    def onchange_field(self):
        if self.field_id:
            self.label = self.field_id.field_description

    xlsx_template_id = fields.Many2one('xlsx.report.template', ondelete='cascade')
    model_id = fields.Many2one('ir.model', related='xlsx_template_id.model_id', readonly=False)
    sequence = fields.Integer(default=1)
    field_id = fields.Many2one('ir.model.fields', string='Field',
                               domain="[('model_id', '=', model_id), ('ttype', '!=', 'binary')]")
    field_name = fields.Char()
    label = fields.Char(required=True)
