# -*- coding: utf-8 -*-

import odoo
from odoo import http
from odoo.http import request
from odoo.api import Environment
from odoo import SUPERUSER_ID
import base64
import logging

_logger = logging.getLogger(__name__)

class Binary(http.Controller):
    """Common controller to download file"""

    @http.route('/web/binary/download_document', type='http', auth="public")
    def download_document(self, model, field, id, filename=None, **kw):
        try:
            env = Environment(request.cr, SUPERUSER_ID, {})
            res = env[str(model)].sudo().browse(int(id))
            filecontent = res[field] and base64.b64decode(res[field]) or b''
            if not filename:
                filename = '%s_%s' % (model.replace('.', '_'), id)
            if not filecontent:
                return request.not_found()
            headers = [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', 'attachment; filename="%s"' % filename)
            ]
            return request.make_response(filecontent, headers)
        except Exception as e:
            _logger.exception("Failed to download document: %s", e)
            return request.not_found()
