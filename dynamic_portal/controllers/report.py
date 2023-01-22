import logging

from odoo import fields, http, SUPERUSER_ID, _
from odoo.http import request, content_disposition

from odoo.http import request
from odoo import http, fields

_logger = logging.getLogger(__name__)


class EmployeeProfile(http.Controller):

    @http.route(['/download/report/<string:report>/<string:model>/<int:recode_id>'], type="http", auth="public",
                methods=['GET'], website=True)
    def download_hr_letter(self, model, report, recode_id):
        record = request.env[model].sudo().browse(int(recode_id))
        if not record.exists():
            return request.not_found()

        return self._generate_report(report, record, download=False)

    def _generate_report(self, report_id, record, download=True):
        report_obj = request.env['ir.actions.report'].browse(int(report_id))

        report = report_obj.with_user(SUPERUSER_ID)._render_qweb_pdf([record.id], data={'report_type': 'pdf'})[0]

        report_content_disposition = content_disposition('{}.pdf'.format(report_obj.report_file))
        if not download:
            content_split = report_content_disposition.split(';')
            content_split[0] = 'inline'
            report_content_disposition = ';'.join(content_split)

        return request.make_response(report, headers=[
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(report)),
            ('Content-Disposition', report_content_disposition),
        ])
