# -*- coding: utf-8 -*-
# Odoo 18.0 Compatible - Updated by roottbar

import odoo
from odoo import http
from odoo.http import request
from odoo.api import Environment
from odoo import SUPERUSER_ID
# ensure_db is no longer available in Odoo 18
# We'll handle database checking differently
import datetime
import json
import logging
# from openpyxl.pivot import record
from datetime import datetime

# from docutils.languages import fa
_logger = logging.getLogger(__name__)
# serialize_exception and content_disposition are no longer available in Odoo 18
# We'll implement them directly or remove them
from odoo.tools.translate import _
import base64


def serialize_exception(func):
    """Decorator to serialize exceptions for Odoo 18 compatibility"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            _logger.error("Exception in %s: %s", func.__name__, str(e))
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
    return wrapper


def content_disposition(filename):
    """Generate content disposition header for Odoo 18 compatibility"""
    import urllib.parse
    return f'attachment; filename="{urllib.parse.quote(filename)}"'


class Binary(http.Controller):
    """Common controller to download file"""

    @http.route('/web/binary/download_document', type='http', auth="public")
    @serialize_exception
    def download_document(self, model, field, id, filename=None, **kw):
        env = Environment(request.cr, SUPERUSER_ID, {})
        res = env[str(model)].search([('id', '=', int(id))]).sudo().read()[0]
        filecontent = base64.b64decode(res.get(field) or '')
        if not filename:
            filename = '%s_%s' % (model.replace('.', '_'), id)
        if not filecontent:
            return request.not_found()
        return request.make_response(filecontent,
                                     [('Content-Type', 'application/octet-stream'),
                                      ('Content-Disposition', content_disposition(filename))])
