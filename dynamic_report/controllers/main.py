# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import mimetypes

from werkzeug import exceptions
from werkzeug.urls import url_decode
from odoo.tools.safe_eval import safe_eval, time
from odoo.http import request, route
from odoo.tools import html_escape

from odoo.addons.web.controllers import main
from odoo.addons.web.controllers.main import _serialize_exception, content_disposition


class ReportController(main.ReportController):

    def report_routes(self, reportname, docids=None, converter=None, **data):
        report = request.env['ir.actions.report'].search([('report_name', '=', reportname)])
        if report.dynamic_report:
            docx = report.template_id.download_report(docids)

            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(docx))]
            return request.make_response(docx, headers=pdfhttpheaders)

        return super(ReportController, self).report_routes(reportname, docids, converter, **data)

