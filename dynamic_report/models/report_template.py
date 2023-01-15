from odoo import fields, models, api, _
from docxtpl import DocxTemplate
# run this command to install package
# sudo pip3 install docxtpl
import io
import os
import base64
import subprocess
import sys
from odoo.exceptions import ValidationError
import urllib, mimetypes
from datetime import datetime, date

split_chr = '\\' if ':' in __file__ else '/'  # if ':' in file_name then I'm running on windows server


class ReportTemplate(models.Model):
    _name = 'report.template'
    _description = 'Report Template'

    name = fields.Char(required=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade', )
    template_type = fields.Selection([('doc', 'Document'), ('xlsx', 'Excel')], 'File Type', default='doc')
    template = fields.Binary(required=True)
    template_filename = fields.Char('File Name', track_visibility='onchange')
    mapping_ids = fields.One2many(
        comodel_name='template.mapping.line',
        inverse_name='template_id',
        string='Mapping')
    state = fields.Selection([
        ('header', 'Header Data'),
        ('mapping', 'Mapping Fields'),
        ('done', 'Done')], string='Status',
        default='header')

    code = fields.Char()

    report_id = fields.Many2one('ir.actions.report', string='Report')

    _sql_constraints = [('report_name_unique', 'unique(name)', 'Report name already exists !.'),
                        ('code_uniq', 'unique (code)', "Code already exists !"), ]

    @api.constrains('template_filename')
    def check_template_filename(self):
        for record in self:
            if record.template_filename and mimetypes.guess_type(record.template_filename)[
                0] != 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' and record.template_type == 'doc':
                raise ValidationError(_("Sorry only 'Docx' type supported"))
            elif record.template_filename and mimetypes.guess_type(record.template_filename)[
                0] != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' and record.template_type == 'xlsx':
                raise ValidationError(_("Sorry only 'XLSX' type supported"))

    def add_report(self):
        vals = {
            'name': self.name,
            'template_id': self.id,
            'report_type': 'qweb-pdf',
            'report_name': self.name,
            'model': self.model_id.model,
            'dynamic_report': True,
        }
        if self.report_id:
            self.report_id.update(vals)
        else:
            report = self.env['ir.actions.report'].create(vals)
            report.create_action()
            self.report_id = report.id

    @api.model
    def create(self, vals):
        res = super(ReportTemplate, self).create(vals)
        res.add_report()
        return res

    def write(self, vals):
        res = super(ReportTemplate, self).write(vals)
        self.add_report()
        return res

    def confirm_header(self):
        self.state = 'mapping'

    def back_header(self):
        self.state = 'header'

    @api.model
    def generate_report(self, record, template_id):
        template_id = self.env['report.template'].browse(template_id)
        return self.download_report(template_id, record)

    def get_field_value(self, obj, field_str):
        field_value = obj[field_str]
        if obj._fields[field_str].type == 'many2one':
            rec_name = field_value._rec_name
            if field_value._rec_name == 'name':
                field_value = field_value.name
            else:
                field_value = self.get_field_value(field_value, rec_name)
        return field_value

    def get_related_field_value(self, record, line):
        record_id = record[line.field_id.name].id
        record_id = self.env[line.relation].browse(int(record_id))
        return self.get_field_value(record_id, line.related_field_id.name)

    def prepare_data(self, template_id, record):
        vals = {}
        for line in template_id.mapping_ids:
            record = self.env[self.model_id.model].browse(int(record))
            if line.print_date:
                value = date.today()
            elif line.related_field_id:
                value = self.get_related_field_value(record, line)
            else:
                value = self.get_field_value(record, line.field_id.name)
            vals.update({line.placeholder: value})
        return vals

    def download_report(self, record):
        # template = split_chr.join(__file__.split(os.sep)[:-2]) + '/data/hr_letter.docx'
        fl = split_chr.join(__file__.split(split_chr)[:-2]) + os.sep
        # fl += '/static/docx/%s' % self.template_id.name
        fl += os.path.join('static', 'docx', self.name)
        tpl = open(fl, "wb")
        tpl.write(base64.b64decode(self.template))
        doc = DocxTemplate(tpl.name)
        # render
        template_data = self.prepare_data(self, record)
        doc.render(template_data)
        file_stream = io.BytesIO()
        doc.save(file_stream)

        file_stream.seek(0)

        # save as docx file
        f = open('{}.docx'.format(fl), 'wb')
        f.write(file_stream.read())
        f.close()

        # convert docx to pdf
        self.convert_to_pdf('{}.docx'.format(fl))

        # open pdf file an object
        file = open('{}.pdf'.format(fl), 'rb')
        bytes_stream = io.BytesIO(file.read())

        return bytes_stream.read()

        return file_stream.read()

    def convert_to_pdf(self, source):
        command = 'abiword --to=pdf "{}" '.format(source)
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        p.communicate()


class TemplateMappingLine(models.Model):
    _name = 'template.mapping.line'
    _description = 'Template Mapping Line'

    @api.onchange('field_id')
    def onchange_field(self):
        if self.field_id:
            if self.field_id.ttype == 'many2one':
                related_field_id = self.env['ir.model.fields'].search(
                    [('name', '=', 'name'), ('model_id', '=', self.field_id.model_id.id)])
                self.related_field_id = related_field_id.id if related_field_id else False

    @api.depends('field_id')
    def _compute_field_readonly(self):
        for rec in self:
            rec.field_readonly = True
            if rec.field_id:
                if rec.field_id.ttype == 'many2one':
                    rec.field_readonly = False

    @api.depends('field_id')
    def _compute_field_relation(self):
        for rec in self:
            rec.relation = False
            if rec.field_id:
                if rec.field_id.ttype == 'many2one':
                    rec.relation = rec.field_id.relation

    template_id = fields.Many2one('report.template')
    model_id = fields.Many2one('ir.model', related='template_id.model_id', readonly=False)
    field_id = fields.Many2one('ir.model.fields', string='Field',
                               domain="[('model_id', '=', model_id), ('ttype', '!=', 'binary')]")
    relation = fields.Char(compute='_compute_field_relation')
    related_field_id = fields.Many2one('ir.model.fields', string='Related Field',
                                       domain="[('model', '=', relation), ('ttype', 'not in', ('binary', 'one2many','many2many'))]")
    field_readonly = fields.Boolean(compute='_compute_field_readonly')
    print_date = fields.Boolean()
    placeholder = fields.Char(required=True)
