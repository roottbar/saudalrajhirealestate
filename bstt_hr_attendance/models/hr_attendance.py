# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone, UTC, utc
from odoo.tools import format_datetime
from odoo.tools import format_time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.addons.resource.models.utils import float_to_time  
HOURS_PER_DAY = 8.0  


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    notes = fields.Char(string="Notes")
    batch_id = fields.Many2one('hr.attendance.batch')
