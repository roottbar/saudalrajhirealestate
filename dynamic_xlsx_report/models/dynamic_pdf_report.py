# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ReportAccountHashIntegrity(models.AbstractModel):
    _name = 'report.dynamic_xlsx_report.dynamic_pdf_report'

    def get_field_value(self, obj, field):
        value = obj[field.name]
        if field.ttype == 'many2one':
            value = value.name_get()[0][1]
            return value
        else:
            return value

    @api.model
    def _get_report_values(self, docids, data):

        xlsx_template_id = data['xlsx_template_id']

        if not xlsx_template_id:
            return

        template = self.env['xlsx.report.template'].browse(int(xlsx_template_id))
        mapping_lines = template.mapping_ids.sorted(key='sequence')

        header = []
        for line in mapping_lines:
            header.append(line.label)

        records = []
        print(docids)
        for record in self.env[template.model_id.model].browse(docids):
            record_data = []
            for line in mapping_lines:
                field_value = self.get_field_value(record, line.field_id)
                record_data.append(field_value)
            records.append(record_data)
        print(records)

        return {
            'doc_ids': docids,
            'doc_model': self.env['res.company'],
            'header': header,
            'records': records,
            'docs': self.env['res.company'].browse(self.env.company.id),
        }
