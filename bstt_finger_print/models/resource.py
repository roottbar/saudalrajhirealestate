# -*- coding:utf-8 -*-
from odoo import models, fields, api


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    checkin_2 = fields.Selection([
        ('option1', 'Accept First Check-In'),
        ('option2', 'Accept Second Check-In'),
        ('option3', 'Create Check-Out Using First Check-In Time'),
        ('option4', 'Create Check-Out Using Second Check-In Time')], string="There are 2 Check-In", default="option1")

    checkout_2 = fields.Selection([
        ('option1', 'Accept First Check-Out'),
        ('option2', 'Accept Second Check-Out'),
        ('option3', 'Create Check-In Using First Check-Out Time'),
        ('option4', 'Create Check-In Using Second Check-Out Time')], string="There are 2 Check-Out", default="option1")

    checkin_without_checkout = fields.Selection([
        ('option1', 'Add Check-Out from Shift time End'),
        ('option2', 'Add Check-Out At End of the Date'),
        ('option3', 'Except Check-In')], string="There are Check-In without Check-Out", default="option1")

    checkout_without_checkin = fields.Selection([
        ('option1', 'Add Check-In at the first of Shift'),
        ('option2', 'Add Check-In at the first of Day'),
        ('option3', 'Except Check-Out')], string="There are Check-Out Without Check-In ", default="option1")




