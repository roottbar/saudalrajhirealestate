# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MaterialPurchaseRequisition(models.Model):
    _name = 'material.purchase.requisition'
    _description = 'Purchase Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    name = fields.Char(string='Number', index=True, readonly=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting IR Approval'),
        ('approve', 'Approved'),
        ('stock', 'Purchase Order Created'),
        ('receive', 'Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        default='draft',
        tracking=True,
    )
    request_date = fields.Date(string='Requisition Date', default=fields.Date.today(), required=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True, copy=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1), required=True, copy=True)
    approve_manager_id = fields.Many2one('hr.employee', string='Department Manager', readonly=True)
    reject_manager_id = fields.Many2one('hr.employee', string='Department Manager Reject', readonly=True)
    approve_employee_id = fields.Many2one('hr.employee', string='Approved by', readonly=True)
    reject_employee_id = fields.Many2one('hr.employee', string='Rejected by', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True)
    location_id = fields.Many2one('stock.location', string='Source Location')
    dest_location_id = fields.Many2one('stock.location', string='Destination Location')
    requisition_line_ids = fields.One2many('material.purchase.requisition.line', 'requisition_id', string='Purchase Requisition Lines')
    date_end = fields.Date(string='Requisition Deadline', readonly=True, help='Last date for the product to be needed')
    date_done = fields.Date(string='Date Done', readonly=True, help='Date of Completion of Purchase Requisition')
    managerapp_date = fields.Date(string='Department Approval Date', readonly=True)
    manareject_date = fields.Date(string='Department Manager Reject Date', readonly=True)
    userreject_date = fields.Date(string='Rejected Date', readonly=True)
    userrapp_date = fields.Date(string='Approved Date', readonly=True)
    receive_date = fields.Date(string='Received Date', readonly=True)
    reason = fields.Text(string='Reason for Requisitions')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    delivery_picking_id = fields.Many2one('stock.picking', string='Internal Picking', readonly=True)
    requisiton_responsible_id = fields.Many2one('hr.employee', string='Requisition Responsible')
    employee_confirm_id = fields.Many2one('hr.employee', string='Confirmed by', readonly=True)
    confirm_date = fields.Date(string='Confirmed Date', readonly=True)
    purchase_order_ids = fields.One2many('purchase.order', 'custom_requisition_id', string='Purchase Orders')
    custom_picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.requisition.seq')
        return super().create(vals)

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel', 'reject'):
                raise UserError(_('You cannot delete a Purchase Requisition which is not draft, cancelled, or rejected.'))
        return super().unlink()

    def requisition_confirm(self):
        for rec in self:
            rec.employee_confirm_id = rec.employee_id.id
            rec.confirm_date = fields.Date.today()
            rec.state = 'dept_confirm'
            manager_mail_template = self.env.ref('material_purchase_requisitions.email_confirm_material_purchase_requistion', raise_if_not_found=False)
            if manager_mail_template:
                manager_mail_template.send_mail(rec.id)

    def requisition_reject(self):
        for rec in self:
            rec.state = 'reject'
            rec.reject_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.userreject_date = fields.Date.today()

    def manager_approve(self):
        for rec in self:
            rec.managerapp_date = fields.Date.today()
            rec.approve_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            employee_mail_template = self.env.ref('material_purchase_requisitions.email_purchase_requisition_iruser_custom', raise_if_not_found=False)
            email_iruser_template = self.env.ref('material_purchase_requisitions.email_purchase_requisition', raise_if_not_found=False)
            if employee_mail_template:
                employee_mail_template.sudo().send_mail(rec.id)
            if email_iruser_template:
                email_iruser_template.sudo().send_mail(rec.id)
            rec.state = 'ir_approve'

    def user_approve(self):
        for rec in self:
            rec.userrapp_date = fields.Date.today()
            rec.approve_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.state = 'approve'

    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.onchange('employee_id')
    def set_department(self):
        for rec in self:
            rec.department_id = rec.employee_id.sudo().department_id.id
            rec.dest_location_id = rec.employee_id.sudo().dest_location_id.id or rec.employee_id.sudo().department_id.dest_location_id.id
