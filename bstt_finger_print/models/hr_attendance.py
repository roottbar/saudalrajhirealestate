# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    is_used_in_Payroll = fields.Boolean(string="Used with Payroll", default=False)
    inserted_by_finger_print = fields.Boolean(string="Inserted by finger pprint", default=False)