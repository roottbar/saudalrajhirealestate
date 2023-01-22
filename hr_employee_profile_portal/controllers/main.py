import logging

from odoo import fields, http, SUPERUSER_ID, _
from odoo.http import request, content_disposition

from odoo.http import request
from odoo import http, fields

_logger = logging.getLogger(__name__)


class EmployeeProfile(http.Controller):

    @http.route('/my/profile', type='http', auth="public", website=True, csrf=True)
    def my_profile(self):
        employee = request.env.user.employee_id
        if not employee:
            return request.not_found()

        return request.render("hr_employee_profile_portal.my_profile_template", {'employee': employee})

