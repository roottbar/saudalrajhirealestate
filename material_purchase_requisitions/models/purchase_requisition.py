# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError

class MaterialPurchaseRequisition(models.Model):
    _name = 'material.purchase.requisition'
    _description = 'Purchase Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel', 'reject'):
                raise UserError(_('You can not delete Purchase Requisition which is not in draft or cancelled or rejected state.'))
        return super(MaterialPurchaseRequisition, self).unlink()

    name = fields.Char(string='Number', index=True, readonly=1)
    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting IR Approval'),
        ('approve', 'Approved'),
        ('stock', 'Purchase Order Created'),
        ('receive', 'Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')], default='draft', track_visibility='onchange')
    request_date = fields.Date(string='Requisition Date', default=fields.Date.today(), required=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True, copy=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1), required=True, copy=True)
    approve_manager_id = fields.Many2one('hr.employee', string='Department Manager', readonly=True, copy=False)
    reject_manager_id = fields.Many2one('hr.employee', string='Department Manager Reject', readonly=True)
    approve_employee_id = fields.Many2one('hr.employee', string='Approved by', readonly=True, copy=False)
    reject_employee_id = fields.Many2one('hr.employee', string='Rejected by', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True, copy=True)
    location_id = fields.Many2one('stock.location', string='Source Location', copy=True)
    requisition_line_ids = fields.One2many('material.purchase.requisition.line', 'requisition_id', string='Purchase Requisitions Line', copy=True)
    date_end = fields.Date(string='Requisition Deadline', readonly=True, help='Last date for the product to be needed', copy=True)
    date_done = fields.Date(string='Date Done', readonly=True, help='Date of Completion of Purchase Requisition')
    managerapp_date = fields.Date(string='Department Approval Date', readonly=True, copy=False)
    manareject_date = fields.Date(string='Department Manager Reject Date', readonly=True)
    userreject_date = fields.Date(string='Rejected Date', readonly=True, copy=False)
    userrapp_date = fields.Date(string='Approved Date', readonly=True, copy=False)
    receive_date = fields.Date(string='Received Date', readonly=True, copy=False)
    reason = fields.Text(string='Reason for Requisitions', copy=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', copy=True)
    dest_location_id = fields.Many2one('stock.location', string='Destination Location', copy=True)
    delivery_picking_id = fields.Many2one('stock.picking', string='Internal Picking', readonly=True, copy=False)
    requisiton_responsible_id = fields.Many2one('hr.employee', string='Requisition Responsible', copy=True)
    employee_confirm_id = fields.Many2one('hr.employee', string='Confirmed by', readonly=True, copy=False)
    confirm_date = fields.Date(string='Confirmed Date', readonly=True, copy=False)
    purchase_order_ids = fields.One2many('purchase.order', 'custom_requisition_id', string='Purchase Orders')
    custom_picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', copy=False)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.requisition.seq')
        return super().create(vals)

    def requisition_confirm(self):
        for rec in self:
            template = self.env.ref('material_purchase_requisitions.email_confirm_material_purchase_requistion', raise_if_not_found=False)
            rec.employee_confirm_id = rec.employee_id.id
            rec.confirm_date = fields.Date.today()
            rec.state = 'dept_confirm'
            if template:
                template.send_mail(rec.id)

    def requisition_reject(self):
        for rec in self:
            rec.state = 'reject'
            rec.reject_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.userreject_date = fields.Date.today()

    def manager_approve(self):
        for rec in self:
            rec.managerapp_date = fields.Date.today()
            rec.approve_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            template_emp = self.env.ref('material_purchase_requisitions.email_purchase_requisition_iruser_custom', raise_if_not_found=False)
            template_ir = self.env.ref('material_purchase_requisitions.email_purchase_requisition', raise_if_not_found=False)
            if template_emp:
                template_emp.sudo().send_mail(rec.id)
            if template_ir:
                template_ir.sudo().send_mail(rec.id)
            rec.state = 'ir_approve'

    def user_approve(self):
        for rec in self:
            rec.userrapp_date = fields.Date.today()
            rec.approve_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.state = 'approve'

    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def _prepare_pick_vals(self, line=False, stock_id=False):
        return {
            'product_id': line.product_id.id,
            'product_uom_qty': line.qty,
            'product_uom': line.uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.dest_location_id.id,
            'name': line.product_id.name,
            'picking_type_id': self.custom_picking_type_id.id,
            'picking_id': stock_id.id,
            'custom_requisition_line_id': line.id,
            'company_id': line.requisition_id.company_id.id,
        }

    @api.model
    def _prepare_po_line(self, line=False, purchase_order=False):
        return {
            'product_id': line.product_id.id,
            'name': line.product_id.name,
            'product_qty': line.qty,
            'product_uom': line.uom.id,
            'date_planned': fields.Date.today(),
            'price_unit': line.product_id.standard_price,
            'order_id': purchase_order.id,
            'account_analytic_id': self.analytic_account_id.id,
            'custom_requisition_line_id': line.id,
        }

    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']

        for rec in self:
            if not rec.requisition_line_ids:
                raise UserError(_('Please create some requisition lines.'))

            stock_id = False
            if any(line.requisition_type == 'internal' for line in rec.requisition_line_ids):
                if not rec.location_id:
                    raise UserError(_('Select Source location under the picking details.'))
                if not rec.custom_picking_type_id:
                    raise UserError(_('Select Picking Type under the picking details.'))
                if not rec.dest_location_id:
                    raise UserError(_('Select Destination location under the picking details.'))

                picking_vals = {
                    'partner_id': rec.employee_id.sudo().address_home_id.id,
                    'location_id': rec.location_id.id,
                    'location_dest_id': rec.dest_location_id.id,
                    'picking_type_id': rec.custom_picking_type_id.id,
                    'note': rec.reason,
                    'custom_requisition_id': rec.id,
                    'origin': rec.name,
                    'company_id': rec.company_id.id,
                }
                stock_id = stock_obj.sudo().create(picking_vals)
                rec.delivery_picking_id = stock_id.id

            po_dict = {}
            for line in rec.requisition_line_ids:
                if line.requisition_type == 'internal':
                    pick_vals = rec._prepare_pick_vals(line, stock_id)
                    move_obj.sudo().create(pick_vals)
                elif line.requisition_type == 'purchase':
                    if not line.partner_id:
                        raise UserError(_('Please enter at least one vendor on requisition lines for purchase requisition.'))
                    for partner in line.partner_id:
                        if partner not in po_dict:
                            po_vals = {
                                'partner_id': partner.id,
                                'currency_id': rec.env.user.company_id.currency_id.id,
                                'date_order': fields.Date.today(),
                                'company_id': rec.company_id.id,
                                'custom_requisition_id': rec.id,
                                'origin': rec.name,
                            }
                            purchase_order = purchase_obj.create(po_vals)
                            po_dict[partner] = purchase_order
                        else:
                            purchase_order = po_dict[partner]
                        po_line_vals = rec._prepare_po_line(line, purchase_order)
                        purchase_line_obj.sudo().create(po_line_vals)
            rec.state = 'stock'

    def action_received(self):
        for rec in self:
            rec.receive_date = fields.Date.today()
            rec.state = 'receive'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.onchange('employee_id')
    def set_department(self):
        for rec in self:
            rec.department_id = rec.employee_id.sudo().department_id.id
            rec.dest_location_id = rec.employee_id.sudo().dest_location_id.id or rec.employee_id.sudo().department_id.dest_location_id.id

    def show_picking(self):
        res = self.env.ref('stock.action_picking_tree_all').read()[0]
        res['domain'] = str([('custom_requisition_id', '=', self.id)])
        return res

    def action_show_po(self):
        res = self.env.ref('purchase.purchase_rfq').read()[0]
        res['domain'] = str([('custom_requisition_id', '=', self.id)])
        return res
