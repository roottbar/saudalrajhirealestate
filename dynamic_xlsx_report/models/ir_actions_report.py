# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.safe_eval import safe_eval, time
from odoo.tools import config, is_html_empty


class ActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    dynamic_xlsx_report = fields.Boolean()
    xlsx_template_id = fields.Many2one('xlsx.report.template')

    @api.model
    def _render_xlsx(self, docids, data):
        report_model_name = "report.%s" % self.report_name
        if self.dynamic_xlsx_report:
            report_model_name = "report.report_xlsx.dynamic_xlsx_report"
            data['xlsx_template_id'] = self.xlsx_template_id.id
        report_model = self.env.get(report_model_name)
        if report_model is None:
            raise UserError(_("%s model was not found") % report_model_name)
        return (
            report_model.with_context(active_model=self.model, xlsx_template_id=self.xlsx_template_id.id)
                .sudo(False)
                .create_xlsx_report(docids, data)  # noqa
        )



    def _get_rendering_context(self, docids, data):
        # If the report is using a custom model to render its html, we must use it.
        # Otherwise, fallback on the generic html rendering.
        report_model = self._get_rendering_context_model()

        data = data and dict(data) or {}

        if report_model is not None:
            # _render_ may be executed in sudo but evaluation context as real user
            report_model = report_model.sudo(False)
            data['xlsx_template_id'] = self.xlsx_template_id.id
            data.update(report_model._get_report_values(docids, data=data))
        else:
            # _render_ may be executed in sudo but evaluation context as real user
            docs = self.env[self.model].sudo(False).browse(docids)
            data.update({
                'doc_ids': docids,
                'doc_model': self.model,
                'docs': docs,
            })
        data['is_html_empty'] = is_html_empty
        return data