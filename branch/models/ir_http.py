# File: branch/models/ir_http.py
# Class/Method: Http.session_info

# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super().session_info()
        if request.session.uid:
            user = request.env.user
            # expose the active branch id while preserving Odoo 18's default payload
            res['branch_id'] = user.branch_id.id if getattr(user, 'branch_id', False) else None
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
