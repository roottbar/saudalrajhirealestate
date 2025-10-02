# -*- coding: utf-8 -*-
from datetime import timedelta, date, datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, format_datetime, format_time



class RentSaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_number = fields.Char(string='رقم عقد منصة ايجار')
    fromdate = fields.Datetime(string='From Date', default=fields.Datetime.now, copy=False, required=True)
    todate = fields.Datetime(string='To Date', default=fields.Datetime.now, copy=False, required=True)
    # Fields in Contract Info Tab
    order_contract = fields.Binary(string='العقد')
    invoice_terms = fields.Selection(
        [('monthly', 'شهري'), ('qua-year', '3 شهور'), ('half-year', '6 أشهر'), ('year', 'سنوي')],
        string='Invoice Terms',
        default='monthly')
    order_contract_invoice = fields.One2many('rent.sale.invoices', 'sale_order_id', string='العقد')
    contract_total_payment = fields.Float(string='Total Contract')
    contract_total_fees = fields.Float(string='Total Fees')
    brand_nameplate_allowed = fields.Boolean(string='Nameplate Allowed')
    contract_hegira_date = fields.Char(string='التاريخ الهجري')
    contract_penalties = fields.Float(string='الجزائات')
    contract_extra_maintenance_cost = fields.Float(string='تكلفة الصيانة الاضافية')
    contractor_pen = fields.Char(string='رسوم متأخرات')
    amount_remain = fields.Float(string='اجمالي المتبقي', compute='_get_remain')
    invoice_number = fields.Integer(string='Number Of Invoices')
    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
                                 readonly="state in ('cancel', 'done')", copy=True,
                                 auto_join=True)

    order_property_state = fields.One2many('rent.sale.state', 'sale_order_id', string='الحالة')

    # بنود الاستلام
    door_good = fields.Boolean('جيد')
    door_bad = fields.Boolean('سئ')
    door_comment = fields.Char('حدد')
    wall_good = fields.Boolean('جيد')
    wall_bad = fields.Boolean('سئ')
    wall_comment = fields.Char('حدد')
    window_good = fields.Boolean('جيد')
    window_bad = fields.Boolean('سئ')
    window_comment = fields.Char('حدد')
    water_good = fields.Boolean('جيد')
    water_bad = fields.Boolean('سئ')
    water_comment = fields.Char('حدد')
    elec_good = fields.Boolean('جيد')
    elec_bad = fields.Boolean('سئ')
    elec_comment = fields.Char('حدد')
    rdoor_good = fields.Boolean('جيد')
    rdoor_bad = fields.Boolean('سئ')
    rdoor_comment = fields.Char('حدد')
    rwall_good = fields.Boolean('جيد')
    rwall_bad = fields.Boolean('سئ')
    rwall_comment = fields.Char('حدد')
    rwindow_good = fields.Boolean('جيد')
    rwindow_bad = fields.Boolean('سئ')
    rwindow_comment = fields.Char('حدد')
    rwater_good = fields.Boolean('جيد')
    rwater_bad = fields.Boolean('سئ')
    rwater_comment = fields.Char('حدد')
    relec_good = fields.Boolean('جيد')
    relec_bad = fields.Boolean('سئ')
    relec_comment = fields.Char('حدد')
    customer_accept = fields.Boolean('نعم')
    customer_refused = fields.Boolean('لا')
    notes = fields.Text('الملاحظات')
    rnotes = fields.Text('الملاحظات')
    mangement_accept = fields.Boolean('نعم')
    mangement_refused = fields.Boolean('لا')
    manage_note = fields.Text('ملاحظة')
    rmanage_note = fields.Text('ملاحظة')
    is_cost = fields.Boolean('نعم')
    is_no_cost = fields.Boolean('لا')
    is_amount_rem = fields.Boolean('نعم')
    is_no_amount_rem = fields.Boolean('لا')
    amount_rem = fields.Float('المبلغ المتبقي')
    iselec_remain = fields.Boolean('نعم')
    isnotelec_remain = fields.Boolean('لا')

    def open_return(self):
        status = "return"
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        lines_to_return = self.order_line.filtered(
            lambda r: r.state in ['sale', 'done', 'occupied'] and r.is_rental and float_compare(r.qty_delivered, r.qty_returned, precision_digits=precision) > 0)
        return self._open_rental_wizard(status, lines_to_return.ids)
    def _get_remain(self):
        for record in self:
            amount = 0
            invoices_paid = self.env['account.move'].sudo().search(
                [('invoice_origin', '=', record.name), ('payment_state', 'in', ['paid', 'in_payment'])])
            for line in invoices_paid:
                amount += line.amount_total
            record.amount_remain = record.amount_total - amount

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                # fees_price = 0.0 fees_price = line.price_subtotal + line.insurance_value + line.contract_admin_fees
                # + line.contract_service_fees + line.contract_admin_sub_fees + line.contract_service_sub_fees
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def create_order_invoices(self):
        for rec in self:
            if rec.invoice_number <= 0:
                raise UserError(_('من فضلك اكتب عدد الفواتير'))
            rec.order_contract_invoice = False
            fromdate = rec.fromdate
            d1 = rec.fromdate
            d2 = rec.todate
            total_contract_period = d2 - d1

            if total_contract_period.days <= 0:
                raise UserError(_('يجب اختيار مدة العقد بصورة صحيحة'))

            diff = 0
            diff = total_contract_period.days / rec.invoice_number
            diff = round(diff, 0)
            # if abs(total_contract_period.days) % abs(rec.invoice_number) >0:
            #     raise UserError(_('يجب كتابة عدد فواتير مناسب لمدة العقد'))
            #

            for i in range(1, rec.invoice_number + 1):

                total_other_amount = sum((
                                                 i.insurance_value + i.contract_admin_fees + i.contract_service_fees + i.contract_admin_sub_fees + i.contract_service_sub_fees)
                                         for i in rec.order_line)
                taxed_total_other_amount = sum(
                    (i.contract_admin_sub_fees + i.contract_service_sub_fees) for i in rec.order_line)

                total_property_amount_without_tax = sum((i.product_uom_qty * i.price_unit) for i in rec.order_line)

                property_amount_per_inv = total_property_amount_without_tax / rec.invoice_number

                total_tax_first_inv = sum(
                    (property_amount_per_inv + taxed_total_other_amount) * (tax.amount / 100) for tax in
                    rec.order_line.tax_id)
                total_tax = sum((property_amount_per_inv) * (tax.amount / 100) for tax in rec.order_line.tax_id)

                todate = fromdate + relativedelta(days=diff)

                if i == 1:
                    amount = property_amount_per_inv + total_other_amount + total_tax_first_inv
                if i == rec.invoice_number:
                    amount = total_property_amount_without_tax - sum(rec.order_contract_invoice.mapped('amount'))
                else:
                    amount = property_amount_per_inv + total_tax
                if amount > 0:
                    sale_invoices = self.env['rent.sale.invoices'].create({
                        'name': "فاتورة رقم " + str(i),
                        'sequence': i,
                        'fromdate': fromdate,
                        'todate': rec.todate if rec.invoice_number == i else todate,
                        'amount': amount,
                        'sale_order_id': rec.id,
                    })
                fromdate = todate + relativedelta(days=1)

    @api.onchange("fromdate", "todate")
    def onchang_contract_dates(self):
        self.get_invoice_number()

    def get_invoice_number(self):
        diff = relativedelta(self.todate, self.fromdate)
        m = month = 0
        if diff.years != 0:
            m = diff.years * 12
        if diff.months != 0:
            month = diff.months
        if diff.days > 0:
            month +=1
        self.invoice_number = month + m
        self.invoice_number = month

    def action_confirm(self):
        if self.invoice_number == 0:
            # self.get_invoice_number()
            raise UserError(_('من فضلك اكتب عدد الفواتير'))
        result = super(RentSaleOrder, self).action_confirm()
        if self.is_rental_order:
            self.create_order_invoices()
        return result

    def write(self, vals):
        """تطبيق قيود التعديل على fromdate و todate عند حالة occupied"""
        # التحقق من وجود سطور في حالة occupied
        occupied_lines = self.order_line.filtered(
            lambda line: hasattr(line, 'state') and line.state == 'occupied'
        )
        
        if occupied_lines and ('fromdate' in vals or 'todate' in vals):
            raise UserError(_('لا يمكن تعديل تاريخ البداية أو النهاية عندما تكون الحالة occupied'))
        
        return super(RentSaleOrder, self).write(vals)

    full_invoiced = fields.Boolean(string="Fully Invoiced", compute="_compute_full_invoiced", store=True)
    no_of_invoiced = fields.Integer(string=" الفواتير المفوترة", compute="compute_no_invoiced")
    no_of_not_invoiced = fields.Integer(string=" الفواتير الغير مفوترة", compute="compute_no_invoiced")
    no_of_invoiced_amount = fields.Float(string="المبالغ المفوترة", compute="compute_no_invoiced")
    no_of_not_invoiced_amount = fields.Float(string="المبالغ الغير مفوترة", compute="compute_no_invoiced")
    no_of_posted_invoiced = fields.Float(string="الفواتير المرحلة", compute="compute_no_invoiced")
    no_of_posted_invoiced_amount = fields.Float(string="مبالغ الفواتير المرحلة", compute="compute_no_invoiced")

    no_of_paid_invoiced = fields.Float(string="الفواتر المدفوعة ", compute="compute_no_invoiced")
    no_of_paid_invoiced_amount = fields.Float(string="مبالغ  الفواتير المدفوعة", compute="compute_no_invoiced")

    
    
    
    # ('payment_state', '!=', 'paid')
    
    @api.depends('order_contract_invoice.status', 'order_contract_invoice.amount')
    def compute_no_invoiced(self):
        for order in self:
            order.no_of_invoiced = 0
            order.no_of_not_invoiced = 0
            order.no_of_invoiced_amount = 0
            order.no_of_not_invoiced_amount = 0
            order.no_of_posted_invoiced = 0
            order.no_of_paid_invoiced = 0
            order.no_of_paid_invoiced_amount = 0

            order.no_of_invoiced = len(order.order_contract_invoice.filtered(lambda s: s.status == 'invoiced'))
            order.no_of_invoiced_amount = sum(order.order_contract_invoice.filtered(lambda s: s.status == 'invoiced').mapped('amount'))

            order.no_of_not_invoiced = len(order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced'))
            order.no_of_not_invoiced_amount = sum(order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced').mapped('amount'))

            order.no_of_posted_invoiced = len(order.invoice_ids.filtered(lambda s: s.state == 'posted'))
            order.no_of_posted_invoiced_amount = sum(order.invoice_ids.filtered(lambda s: s.state == 'posted').mapped('amount_total'))

    
            order.no_of_paid_invoiced = len(order.invoice_ids.filtered(lambda s: s.payment_state == 'paid'))
            order.no_of_paid_invoiced_amount = sum(order.invoice_ids.filtered(lambda s: s.payment_state == 'paid').mapped('amount_total'))

    @api.depends('order_contract_invoice.status')
    def _compute_full_invoiced(self):
        for order in self:
            order.full_invoiced = False
            not_invoiced = order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced')
            if not not_invoiced and len(order.order_contract_invoice) > 0:
                order.full_invoiced = True

    @api.model
    def create(self, vals):
        result = super(RentSaleOrder, self).create(vals)
        if result.invoice_number <= 0 and result.is_rental_order:
            raise UserError(_('من فضلك اكتب عدد الفواتير'))
        return result

    # @api.model_create_multi
    # def create(self, vals_list):
    #     order_lines_list = []
    #     res = super(RentSaleOrder, self).create(vals_list)
    #
    #     # if res.invoice_terms == 'monthly':
    #     #
    #     # elif res.invoice_terms == 'half-year':
    #     # elif res.invoice_terms == 'qua-year':
    #     # elif res.invoice_terms == 'year':
    #     product_admin = self.env['product.template'].sudo().search([('name', '=', 'رسوم ادارية')])
    #     product_admin.list_price = res.contract_admin_fees
    #     product_admin.standard_price = res.contract_admin_fees
    #     product_product_admin = self.env['product.product'].sudo().search([('product_tmpl_id', '=', product_admin.id)])
    #     if res.contract_admin_fees > 0:
    #         order_lines_list.append((0, 0, {
    #             'name': 'رسوم ادارية',
    #             'product_id': product_product_admin.id,
    #             'price_unit': res.contract_admin_fees,
    #             'is_rental': True,
    #             'pickup_date': res.order_line[0].pickup_date,
    #             'return_date': res.order_line[0].return_date,
    #             'price_subtotal': res.contract_admin_fees
    #         }))
    #     product_service = self.env['product.template'].sudo().search([('name', '=', 'رسوم خدمات')])
    #     product_service.list_price = res.contract_service_fees
    #     product_service.standard_price = res.contract_service_fees
    #     product_product_service = self.env['product.product'].sudo().search(
    #         [('product_tmpl_id', '=', product_service.id)])
    #     if res.contract_service_fees > 0:
    #         order_lines_list.append((0, 0, {
    #             'name': 'رسوم خدمات',
    #             'product_id': product_product_service.id,
    #             'price_unit': res.contract_service_fees,
    #             'is_rental': True,
    #             'pickup_date': res.order_line[0].pickup_date,
    #             'return_date': res.order_line[0].return_date,
    #             'price_subtotal': res.contract_service_fees
    #         }))
    #     product_sub_admin = self.env['product.template'].sudo().search([('name', '=', 'رسوم ادارية خاضعة')])
    #     product_sub_admin.list_price = res.contract_admin_sub_fees
    #     product_sub_admin.standard_price = res.contract_admin_sub_fees
    #     product_product_sub_admin = self.env['product.product'].sudo().search(
    #         [('product_tmpl_id', '=', product_sub_admin.id)])
    #     if res.contract_admin_sub_fees > 0:
    #         order_lines_list.append((0, 0, {
    #             'name': 'رسوم ادارية خاضعة',
    #             'product_id': product_product_sub_admin.id,
    #             'price_unit': res.contract_admin_sub_fees,
    #             'is_rental': True,
    #             'pickup_date': res.order_line[0].pickup_date,
    #             'return_date': res.order_line[0].return_date,
    #             'price_subtotal': res.contract_admin_sub_fees
    #         }))
    #     product_sub_service = self.env['product.template'].sudo().search([('name', '=', 'رسوم خدمات خاضعة')])
    #     product_sub_service.list_price = res.contract_service_sub_fees
    #     product_sub_service.standard_price = res.contract_service_sub_fees
    #     product_product_sub_service = self.env['product.product'].sudo().search(
    #         [('product_tmpl_id', '=', product_sub_service.id)])
    #     if res.contract_service_sub_fees > 0:
    #         order_lines_list.append((0, 0, {
    #             'name': 'رسوم خدمات خاضعة',
    #             'product_id': product_product_sub_service.id,
    #             'price_unit': res.contract_service_sub_fees,
    #             'is_rental': True,
    #             'pickup_date': res.order_line[0].pickup_date,
    #             'return_date': res.order_line[0].return_date,
    #             'price_subtotal': res.contract_service_sub_fees
    #         }))
    #     product_service = self.env['product.template'].sudo().search([('name', '=', 'تـأمين')])
    #     product_service.list_price = res.insurance_value
    #     product_service.standard_price = res.insurance_value
    #     product_product_service = self.env['product.product'].sudo().search(
    #         [('product_tmpl_id', '=', product_service.id)])
    #
    #     if res.insurance_value > 0:
    #         order_lines_list.append((0, 0, {
    #             'name': 'تـأمين',
    #             'product_id': product_product_service.id,
    #             'price_unit': res.insurance_value,
    #             'is_rental': True,
    #             'pickup_date': res.order_line[0].pickup_date,
    #             'return_date': res.order_line[0].return_date,
    #             'price_subtotal': res.insurance_value
    #         }))
    #     print(order_lines_list)
    #     res.update({
    #
    #         'order_line': order_lines_list
    #
    #     })
    #
    #     return res


class RentSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    property_number = fields.Many2one('rent.property', string='العقار')
    pickup_date = fields.Datetime(string="Pickup", related='order_id.fromdate', store=True)
    return_date = fields.Datetime(string="Return", related='order_id.todate', store=True)
    insurance_value = fields.Float(string='قيمة التأمين')
    contract_admin_fees = fields.Float(string='رسوم ادارية')
    contract_service_fees = fields.Float(string='رسوم الخدمات')
    contract_admin_sub_fees = fields.Float(string='رسوم ادارية خاضعة')
    contract_service_sub_fees = fields.Float(string='رسوم الخدمات خاضعة')
    fromdate = fields.Datetime(related="order_id.fromdate", store=1)
    todate = fields.Datetime(related="order_id.todate", store=1)

    def search_property_address_area(self, operator, value):
        return [('property_address_area', 'ilike', value)]

    property_address_area = fields.Many2one(comodel_name='operating.unit', string='الفرع',
                                            compute="get_property_number_fields", store=1)
    property_address_build2 = fields.Many2one(comodel_name='rent.property.build', string='المجمع',
                                              related="property_number.property_address_build", store=1)
    # property_address_build = fields.Many2one(comodel_name='rent.property.build', string='المجمع',compute="get_property_number_fields2", store=1)
    # property_number = fields.Many2one(comodel_name='rent.property', string='العقار')
    partner_id = fields.Many2one(related='order_id.partner_id')

    @api.depends('property_number')
    def get_property_number_fields(self):
        for rec in self:
            rec.property_address_area = rec.property_number.property_address_area.id if rec.property_number else False

    # @api.depends('property_number')
    # def get_property_number_fields2(self):
    #     for rec in self:
    #         rec.property_address_build = rec.property_number.property_address_build.id if rec.property_number else False

    unit_state = fields.Char(related='product_id.unit_state', store=1)
    amount_paid = fields.Float(compute="get_amount_paid")
    amount_due = fields.Float(compute="get_amount_paid")
    unit_expenses = fields.Float(string="المصروفات", compute="get_unit_expenses")
    unit_revenues = fields.Float(string="الإيرادات", compute="get_unit_revenues")
    analytic_account_id = fields.Many2one('account.analytic.account', string='الحساب التحليلي', related='product_id.analytic_account', store=True)
    # apartment_insurance = fields.Float(related='order_id.apartment_insurance')
    @api.depends('order_id', 'product_id')
    def get_amount_paid(self):
        for rec in self:
            # حساب المبلغ المدفوع
            # مجموع المبالغ للفواتير في حالة مدفوع لنفس امر المبيعات
            paid_invoices_amount = sum(
                invoice.amount_total for invoice in rec.order_id.invoice_ids.filtered(
                    lambda inv: inv.payment_state == 'paid'
                )
            )
            
            # زائد المدفوع جزئيا المبلغ المسدد (المبلغ الكلي - المبلغ المتبقي)
            partially_paid_amount = sum(
                (invoice.amount_total - invoice.amount_residual) for invoice in rec.order_id.invoice_ids.filtered(
                    lambda inv: inv.payment_state == 'partial'
                )
            )
            
            rec.amount_paid = paid_invoices_amount + partially_paid_amount
            
            # حساب المبلغ المستحق
            # مجموع المبالغ المتبقية للفواتير في حالة غير مدفوع لنفس امر المبيعات
            unpaid_invoices_amount = sum(
                invoice.amount_total for invoice in rec.order_id.invoice_ids.filtered(
                    lambda inv: inv.payment_state == 'not_paid'
                )
            )
            
            # زائد المتبقي من الفواتير المدفوعة جزئيا المتبقي منها غير مدفوع
            partially_unpaid_amount = sum(
                invoice.amount_residual for invoice in rec.order_id.invoice_ids.filtered(
                    lambda inv: inv.payment_state == 'partial'
                )
            )
            
            rec.amount_due = unpaid_invoices_amount + partially_unpaid_amount
    @api.depends('product_id', 'analytic_account_id')
    def get_unit_expenses(self):
        """حساب المصروفات للحساب التحليلي للعقار من فواتير الموردين"""
        for rec in self:
            if not rec.analytic_account_id:
                rec.unit_expenses = 0.0
                continue
                
            try:
                # البحث عن فواتير الموردين المرتبطة بنفس الحساب التحليلي للعقار
                expense_lines = self.env['account.move.line'].search([
                    ('move_id.move_type', '=', 'in_invoice'),  # فواتير الموردين
                    ('analytic_account_id', '=', rec.analytic_account_id.id),  # نفس الحساب التحليلي للعقار
                    ('move_id.state', '=', 'posted'),  # فواتير مرحلة
                    ('account_id.user_type_id.name', 'in', ['Expenses', 'Cost of Revenue'])  # حسابات المصروفات
                ])
                
                # حساب إجمالي المصروفات من الجانب المدين
                rec.unit_expenses = sum(expense_lines.mapped('debit')) or 0.0
            except Exception as e:
                rec.unit_expenses = 0.0

    @api.depends('product_id', 'analytic_account_id')
    def get_unit_revenues(self):
        """حساب الإيرادات للحساب التحليلي للعقار من فواتير العملاء"""
        for rec in self:
            if not rec.analytic_account_id:
                rec.unit_revenues = 0.0
                continue
                
            try:
                # البحث عن فواتير العملاء المرتبطة بنفس الحساب التحليلي للعقار
                revenue_lines = self.env['account.move.line'].search([
                    ('move_id.move_type', '=', 'out_invoice'),  # فواتير العملاء
                    ('analytic_account_id', '=', rec.analytic_account_id.id),  # نفس الحساب التحليلي للعقار
                    ('move_id.state', '=', 'posted'),  # فواتير مرحلة
                    ('move_id.payment_state', 'in', ['paid', 'in_payment']),  # مدفوعة أو قيد الدفع
                    ('account_id.user_type_id.name', 'in', ['Income', 'Other Income'])  # حسابات الإيرادات
                ])
                
                # حساب إجمالي الإيرادات من الجانب الدائن
                rec.unit_revenues = sum(revenue_lines.mapped('credit')) or 0.0
            except Exception as e:
                rec.unit_revenues = 0.0

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        return {'domain': {'property_number': [('property_address_area.id', '=', self.operating_unit_id.id)]}}


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit + line.insurance_value + line.contract_admin_fees + line.contract_service_fees + line.contract_admin_sub_fees + line.contract_service_sub_fees * (
                    1 - (line.discount or 0.0) / 100.0)
            price_tax = line.price_unit + line.contract_admin_sub_fees + line.contract_service_sub_fees * (
                    1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price_tax, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': price,
                # 'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    def get_rental_order_line_description(self):
        return ""
    @api.depends('return_date')
    def _compute_is_late(self):
        now = fields.Datetime.now()
        
        for line in self:
            if not line.return_date:
                line.is_late = False
                continue
                
            try:
                line.is_late = line.return_date < now
            except (TypeError, ValueError):
                line.is_late = False










# # -*- coding: utf-8 -*-
# from datetime import timedelta, date, datetime

# from dateutil.relativedelta import relativedelta

# from odoo import models, fields, api, _
# from odoo.exceptions import UserError
# from odoo.tools import float_compare, format_datetime, format_time



# class RentSaleOrder(models.Model):
#     _inherit = 'sale.order'

#     contract_number = fields.Char(string='رقم عقد منصة ايجار')
#     fromdate = fields.Datetime(string='From Date', default=fields.Datetime.now, copy=False, required=True)
#     todate = fields.Datetime(string='To Date', default=fields.Datetime.now, copy=False, required=True)
#     # Fields in Contract Info Tab
#     order_contract = fields.Binary(string='العقد')
#     invoice_terms = fields.Selection(
#         [('monthly', 'شهري'), ('qua-year', '3 شهور'), ('half-year', '6 أشهر'), ('year', 'سنوي')],
#         string='Invoice Terms',
#         default='monthly')
#     order_contract_invoice = fields.One2many('rent.sale.invoices', 'sale_order_id', string='العقد')
#     contract_total_payment = fields.Float(string='Total Contract')
#     contract_total_fees = fields.Float(string='Total Fees')
#     brand_nameplate_allowed = fields.Boolean(string='Nameplate Allowed')
#     contract_hegira_date = fields.Char(string='التاريخ الهجري')
#     contract_penalties = fields.Float(string='الجزائات')
#     contract_extra_maintenance_cost = fields.Float(string='تكلفة الصيانة الاضافية')
#     contractor_pen = fields.Char(string='رسوم متأخرات')
#     amount_remain = fields.Float(string='اجمالي المتبقي', compute='_get_remain')
#     invoice_number = fields.Integer(string='Number Of Invoices')
#     order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
#                                  readonly="state in ('cancel', 'done')", copy=True,
#                                  auto_join=True)

#     order_property_state = fields.One2many('rent.sale.state', 'sale_order_id', string='الحالة')

#     # بنود الاستلام
#     door_good = fields.Boolean('جيد')
#     door_bad = fields.Boolean('سئ')
#     door_comment = fields.Char('حدد')
#     wall_good = fields.Boolean('جيد')
#     wall_bad = fields.Boolean('سئ')
#     wall_comment = fields.Char('حدد')
#     window_good = fields.Boolean('جيد')
#     window_bad = fields.Boolean('سئ')
#     window_comment = fields.Char('حدد')
#     water_good = fields.Boolean('جيد')
#     water_bad = fields.Boolean('سئ')
#     water_comment = fields.Char('حدد')
#     elec_good = fields.Boolean('جيد')
#     elec_bad = fields.Boolean('سئ')
#     elec_comment = fields.Char('حدد')
#     rdoor_good = fields.Boolean('جيد')
#     rdoor_bad = fields.Boolean('سئ')
#     rdoor_comment = fields.Char('حدد')
#     rwall_good = fields.Boolean('جيد')
#     rwall_bad = fields.Boolean('سئ')
#     rwall_comment = fields.Char('حدد')
#     rwindow_good = fields.Boolean('جيد')
#     rwindow_bad = fields.Boolean('سئ')
#     rwindow_comment = fields.Char('حدد')
#     rwater_good = fields.Boolean('جيد')
#     rwater_bad = fields.Boolean('سئ')
#     rwater_comment = fields.Char('حدد')
#     relec_good = fields.Boolean('جيد')
#     relec_bad = fields.Boolean('سئ')
#     relec_comment = fields.Char('حدد')
#     customer_accept = fields.Boolean('نعم')
#     customer_refused = fields.Boolean('لا')
#     notes = fields.Text('الملاحظات')
#     rnotes = fields.Text('الملاحظات')
#     mangement_accept = fields.Boolean('نعم')
#     mangement_refused = fields.Boolean('لا')
#     manage_note = fields.Text('ملاحظة')
#     rmanage_note = fields.Text('ملاحظة')
#     is_cost = fields.Boolean('نعم')
#     is_no_cost = fields.Boolean('لا')
#     is_amount_rem = fields.Boolean('نعم')
#     is_no_amount_rem = fields.Boolean('لا')
#     amount_rem = fields.Float('المبلغ المتبقي')
#     iselec_remain = fields.Boolean('نعم')
#     isnotelec_remain = fields.Boolean('لا')

#     def open_return(self):
#         status = "return"
#         precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#         lines_to_return = self.order_line.filtered(
#             lambda r: r.state in ['sale', 'done', 'occupied'] and r.is_rental and float_compare(r.qty_delivered, r.qty_returned, precision_digits=precision) > 0)
#         return self._open_rental_wizard(status, lines_to_return.ids)
#     def _get_remain(self):
#         for record in self:
#             amount = 0
#             invoices_paid = self.env['account.move'].sudo().search(
#                 [('invoice_origin', '=', record.name), ('payment_state', 'in', ['paid', 'in_payment'])])
#             for line in invoices_paid:
#                 amount += line.amount_total
#             record.amount_remain = record.amount_total - amount

#     @api.depends('order_line.price_total')
#     def _amount_all(self):
#         """
#         Compute the total amounts of the SO.
#         """
#         for order in self:
#             amount_untaxed = amount_tax = 0.0
#             for line in order.order_line:
#                 # fees_price = 0.0 fees_price = line.price_subtotal + line.insurance_value + line.contract_admin_fees
#                 # + line.contract_service_fees + line.contract_admin_sub_fees + line.contract_service_sub_fees
#                 amount_untaxed += line.price_subtotal
#                 amount_tax += line.price_tax
#             order.update({
#                 'amount_untaxed': amount_untaxed,
#                 'amount_tax': amount_tax,
#                 'amount_total': amount_untaxed + amount_tax,
#             })

#     def create_order_invoices(self):
#         for rec in self:
#             if rec.invoice_number <= 0:
#                 raise UserError(_('من فضلك اكتب عدد الفواتير'))
#             rec.order_contract_invoice = False
#             fromdate = rec.fromdate
#             d1 = rec.fromdate
#             d2 = rec.todate
#             total_contract_period = d2 - d1

#             if total_contract_period.days <= 0:
#                 raise UserError(_('يجب اختيار مدة العقد بصورة صحيحة'))

#             diff = 0
#             diff = total_contract_period.days / rec.invoice_number
#             diff = round(diff, 0)
#             # if abs(total_contract_period.days) % abs(rec.invoice_number) >0:
#             #     raise UserError(_('يجب كتابة عدد فواتير مناسب لمدة العقد'))
#             #

#             for i in range(1, rec.invoice_number + 1):

#                 total_other_amount = sum((
#                                                  i.insurance_value + i.contract_admin_fees + i.contract_service_fees + i.contract_admin_sub_fees + i.contract_service_sub_fees)
#                                          for i in rec.order_line)
#                 taxed_total_other_amount = sum(
#                     (i.contract_admin_sub_fees + i.contract_service_sub_fees) for i in rec.order_line)

#                 total_property_amount_without_tax = sum((i.product_uom_qty * i.price_unit) for i in rec.order_line)

#                 property_amount_per_inv = total_property_amount_without_tax / rec.invoice_number

#                 total_tax_first_inv = sum(
#                     (property_amount_per_inv + taxed_total_other_amount) * (tax.amount / 100) for tax in
#                     rec.order_line.tax_id)
#                 total_tax = sum((property_amount_per_inv) * (tax.amount / 100) for tax in rec.order_line.tax_id)

#                 todate = fromdate + relativedelta(days=diff)

#                 if i == 1:
#                     amount = property_amount_per_inv + total_other_amount + total_tax_first_inv
#                 if i == rec.invoice_number:
#                     amount = total_property_amount_without_tax - sum(rec.order_contract_invoice.mapped('amount'))
#                 else:
#                     amount = property_amount_per_inv + total_tax
#                 if amount > 0:
#                     sale_invoices = self.env['rent.sale.invoices'].create({
#                         'name': "فاتورة رقم " + str(i),
#                         'sequence': i,
#                         'fromdate': fromdate,
#                         'todate': rec.todate if rec.invoice_number == i else todate,
#                         'amount': amount,
#                         'sale_order_id': rec.id,
#                     })
#                 fromdate = todate + relativedelta(days=1)

#     @api.onchange("fromdate", "todate")
#     def onchang_contract_dates(self):
#         self.get_invoice_number()

#     def get_invoice_number(self):
#         diff = relativedelta(self.todate, self.fromdate)
#         m = month = 0
#         if diff.years != 0:
#             m = diff.years * 12
#         if diff.months != 0:
#             month = diff.months
#         if diff.days > 0:
#             month +=1
#         self.invoice_number = month + m
#         self.invoice_number = month

#     def action_confirm(self):
#         if self.invoice_number == 0:
#             # self.get_invoice_number()
#             raise UserError(_('من فضلك اكتب عدد الفواتير'))
#         result = super(RentSaleOrder, self).action_confirm()
#         if self.is_rental_order:
#             self.create_order_invoices()
#         return result

#     full_invoiced = fields.Boolean(string="Fully Invoiced", compute="_compute_full_invoiced", store=True)
#     no_of_invoiced = fields.Integer(string=" الفواتير المفوترة", compute="compute_no_invoiced")
#     no_of_not_invoiced = fields.Integer(string=" الفواتير الغير مفوترة", compute="compute_no_invoiced")
#     no_of_invoiced_amount = fields.Float(string="المبالغ المفوترة", compute="compute_no_invoiced")
#     no_of_not_invoiced_amount = fields.Float(string="المبالغ الغير مفوترة", compute="compute_no_invoiced")
#     no_of_posted_invoiced = fields.Float(string="الفواتير المرحلة", compute="compute_no_invoiced")
#     no_of_posted_invoiced_amount = fields.Float(string="مبالغ الفواتير المرحلة", compute="compute_no_invoiced")

#     no_of_paid_invoiced = fields.Float(string="الفواتر المدفوعة ", compute="compute_no_invoiced")
#     no_of_paid_invoiced_amount = fields.Float(string="مبالغ  الفواتير المدفوعة", compute="compute_no_invoiced")

    
    
    
#     # ('payment_state', '!=', 'paid')
    
#     @api.depends('order_contract_invoice.status', 'order_contract_invoice.amount')
#     def compute_no_invoiced(self):
#         for order in self:
#             order.no_of_invoiced = 0
#             order.no_of_not_invoiced = 0
#             order.no_of_invoiced_amount = 0
#             order.no_of_not_invoiced_amount = 0
#             order.no_of_posted_invoiced = 0
#             order.no_of_paid_invoiced = 0
#             order.no_of_paid_invoiced_amount = 0

#             order.no_of_invoiced = len(order.order_contract_invoice.filtered(lambda s: s.status == 'invoiced'))
#             order.no_of_invoiced_amount = sum(order.order_contract_invoice.filtered(lambda s: s.status == 'invoiced').mapped('amount'))

#             order.no_of_not_invoiced = len(order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced'))
#             order.no_of_not_invoiced_amount = sum(order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced').mapped('amount'))

#             order.no_of_posted_invoiced = len(order.invoice_ids.filtered(lambda s: s.state == 'posted'))
#             order.no_of_posted_invoiced_amount = sum(order.invoice_ids.filtered(lambda s: s.state == 'posted').mapped('amount_total'))

    
#             order.no_of_paid_invoiced = len(order.invoice_ids.filtered(lambda s: s.payment_state == 'paid'))
#             order.no_of_paid_invoiced_amount = sum(order.invoice_ids.filtered(lambda s: s.payment_state == 'paid').mapped('amount_total'))

#     @api.depends('order_contract_invoice.status')
#     def _compute_full_invoiced(self):
#         for order in self:
#             order.full_invoiced = False
#             not_invoiced = order.order_contract_invoice.filtered(lambda s: s.status == 'uninvoiced')
#             if not not_invoiced and len(order.order_contract_invoice) > 0:
#                 order.full_invoiced = True

#     @api.model
#     def create(self, vals):
#         result = super(RentSaleOrder, self).create(vals)
#         if result.invoice_number <= 0 and result.is_rental_order:
#             raise UserError(_('من فضلك اكتب عدد الفواتير'))
#         return result

#     # @api.model_create_multi
#     # def create(self, vals_list):
#     #     order_lines_list = []
#     #     res = super(RentSaleOrder, self).create(vals_list)
#     #
#     #     # if res.invoice_terms == 'monthly':
#     #     #
#     #     # elif res.invoice_terms == 'half-year':
#     #     # elif res.invoice_terms == 'qua-year':
#     #     # elif res.invoice_terms == 'year':
#     #     product_admin = self.env['product.template'].sudo().search([('name', '=', 'رسوم ادارية')])
#     #     product_admin.list_price = res.contract_admin_fees
#     #     product_admin.standard_price = res.contract_admin_fees
#     #     product_product_admin = self.env['product.product'].sudo().search([('product_tmpl_id', '=', product_admin.id)])
#     #     if res.contract_admin_fees > 0:
#     #         order_lines_list.append((0, 0, {
#     #             'name': 'رسوم ادارية',
#     #             'product_id': product_product_admin.id,
#     #             'price_unit': res.contract_admin_fees,
#     #             'is_rental': True,
#     #             'pickup_date': res.order_line[0].pickup_date,
#     #             'return_date': res.order_line[0].return_date,
#     #             'price_subtotal': res.contract_admin_fees
#     #         }))
#     #     product_service = self.env['product.template'].sudo().search([('name', '=', 'رسوم خدمات')])
#     #     product_service.list_price = res.contract_service_fees
#     #     product_service.standard_price = res.contract_service_fees
#     #     product_product_service = self.env['product.product'].sudo().search(
#     #         [('product_tmpl_id', '=', product_service.id)])
#     #     if res.contract_service_fees > 0:
#     #         order_lines_list.append((0, 0, {
#     #             'name': 'رسوم خدمات',
#     #             'product_id': product_product_service.id,
#     #             'price_unit': res.contract_service_fees,
#     #             'is_rental': True,
#     #             'pickup_date': res.order_line[0].pickup_date,
#     #             'return_date': res.order_line[0].return_date,
#     #             'price_subtotal': res.contract_service_fees
#     #         }))
#     #     product_sub_admin = self.env['product.template'].sudo().search([('name', '=', 'رسوم ادارية خاضعة')])
#     #     product_sub_admin.list_price = res.contract_admin_sub_fees
#     #     product_sub_admin.standard_price = res.contract_admin_sub_fees
#     #     product_product_sub_admin = self.env['product.product'].sudo().search(
#     #         [('product_tmpl_id', '=', product_sub_admin.id)])
#     #     if res.contract_admin_sub_fees > 0:
#     #         order_lines_list.append((0, 0, {
#     #             'name': 'رسوم ادارية خاضعة',
#     #             'product_id': product_product_sub_admin.id,
#     #             'price_unit': res.contract_admin_sub_fees,
#     #             'is_rental': True,
#     #             'pickup_date': res.order_line[0].pickup_date,
#     #             'return_date': res.order_line[0].return_date,
#     #             'price_subtotal': res.contract_admin_sub_fees
#     #         }))
#     #     product_sub_service = self.env['product.template'].sudo().search([('name', '=', 'رسوم خدمات خاضعة')])
#     #     product_sub_service.list_price = res.contract_service_sub_fees
#     #     product_sub_service.standard_price = res.contract_service_sub_fees
#     #     product_product_sub_service = self.env['product.product'].sudo().search(
#     #         [('product_tmpl_id', '=', product_sub_service.id)])
#     #     if res.contract_service_sub_fees > 0:
#     #         order_lines_list.append((0, 0, {
#     #             'name': 'رسوم خدمات خاضعة',
#     #             'product_id': product_product_sub_service.id,
#     #             'price_unit': res.contract_service_sub_fees,
#     #             'is_rental': True,
#     #             'pickup_date': res.order_line[0].pickup_date,
#     #             'return_date': res.order_line[0].return_date,
#     #             'price_subtotal': res.contract_service_sub_fees
#     #         }))
#     #     product_service = self.env['product.template'].sudo().search([('name', '=', 'تـأمين')])
#     #     product_service.list_price = res.insurance_value
#     #     product_service.standard_price = res.insurance_value
#     #     product_product_service = self.env['product.product'].sudo().search(
#     #         [('product_tmpl_id', '=', product_service.id)])
#     #
#     #     if res.insurance_value > 0:
#     #         order_lines_list.append((0, 0, {
#     #             'name': 'تـأمين',
#     #             'product_id': product_product_service.id,
#     #             'price_unit': res.insurance_value,
#     #             'is_rental': True,
#     #             'pickup_date': res.order_line[0].pickup_date,
#     #             'return_date': res.order_line[0].return_date,
#     #             'price_subtotal': res.insurance_value
#     #         }))
#     #     print(order_lines_list)
#     #     res.update({
#     #
#     #         'order_line': order_lines_list
#     #
#     #     })
#     #
#     #     return res


# class RentSaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'

#     property_number = fields.Many2one('rent.property', string='العقار')
#     pickup_date = fields.Datetime(string="Pickup", related='order_id.fromdate', store=True)
#     return_date = fields.Datetime(string="Return", related='order_id.todate', store=True)
#     insurance_value = fields.Float(string='قيمة التأمين')
#     contract_admin_fees = fields.Float(string='رسوم ادارية')
#     contract_service_fees = fields.Float(string='رسوم الخدمات')
#     contract_admin_sub_fees = fields.Float(string='رسوم ادارية خاضعة')
#     contract_service_sub_fees = fields.Float(string='رسوم الخدمات خاضعة')
#     fromdate = fields.Datetime(related="order_id.fromdate", store=1)
#     todate = fields.Datetime(related="order_id.todate", store=1)

#     def search_property_address_area(self, operator, value):
#         return [('property_address_area', 'ilike', value)]

#     property_address_area = fields.Many2one(comodel_name='operating.unit', string='الفرع',
#                                             compute="get_property_number_fields", store=1)
#     property_address_build2 = fields.Many2one(comodel_name='rent.property.build', string='المجمع',
#                                               related="property_number.property_address_build", store=1)
#     # property_address_build = fields.Many2one(comodel_name='rent.property.build', string='المجمع',compute="get_property_number_fields2", store=1)
#     # property_number = fields.Many2one(comodel_name='rent.property', string='العقار')
#     partner_id = fields.Many2one(related='order_id.partner_id')

#     @api.depends('property_number')
#     def get_property_number_fields(self):
#         for rec in self:
#             rec.property_address_area = rec.property_number.property_address_area.id if rec.property_number else False

#     # @api.depends('property_number')
#     # def get_property_number_fields2(self):
#     #     for rec in self:
#     #         rec.property_address_build = rec.property_number.property_address_build.id if rec.property_number else False

#     unit_state = fields.Char(related='product_id.unit_state', store=1)
#     amount_paid = fields.Float(compute="get_amount_paid")
#     amount_due = fields.Float(compute="get_amount_paid")
#     unit_expenses = fields.Float(string="المصروفات", compute="get_unit_expenses")
#     unit_revenues = fields.Float(string="الإيرادات", compute="get_unit_revenues")
#     analytic_account_id = fields.Many2one('account.analytic.account', string='الحساب التحليلي', related='product_id.analytic_account', store=True)
#     # apartment_insurance = fields.Float(related='order_id.apartment_insurance')
#     @api.depends('order_id', 'product_id')
#     def get_amount_paid(self):
#         for rec in self:
#             # حساب المبلغ المدفوع
#             # مجموع المبالغ للفواتير في حالة مدفوع لنفس امر المبيعات
#             paid_invoices_amount = sum(
#                 invoice.amount_total for invoice in rec.order_id.invoice_ids.filtered(
#                     lambda inv: inv.payment_state == 'paid'
#                 )
#             )
            
#             # زائد المدفوع جزئيا المبلغ المسدد (المبلغ الكلي - المبلغ المتبقي)
#             partially_paid_amount = sum(
#                 (invoice.amount_total - invoice.amount_residual) for invoice in rec.order_id.invoice_ids.filtered(
#                     lambda inv: inv.payment_state == 'partial'
#                 )
#             )
            
#             rec.amount_paid = paid_invoices_amount + partially_paid_amount
            
#             # حساب المبلغ المستحق
#             # مجموع المبالغ المتبقية للفواتير في حالة غير مدفوع لنفس امر المبيعات
#             unpaid_invoices_amount = sum(
#                 invoice.amount_total for invoice in rec.order_id.invoice_ids.filtered(
#                     lambda inv: inv.payment_state == 'not_paid'
#                 )
#             )
            
#             # زائد المتبقي من الفواتير المدفوعة جزئيا المتبقي منها غير مدفوع
#             partially_unpaid_amount = sum(
#                 invoice.amount_residual for invoice in rec.order_id.invoice_ids.filtered(
#                     lambda inv: inv.payment_state == 'partial'
#                 )
#             )
            
#             rec.amount_due = unpaid_invoices_amount + partially_unpaid_amount

#     @api.depends('product_id')
#     def get_unit_expenses(self):
#         """حساب المصروفات لنفس الوحدة"""
#         for rec in self:
#             # البحث عن جميع الفواتير المتعلقة بنفس الوحدة (المنتج) كمصروفات
#             expenses = self.env['account.move'].search([
#                 ('move_type', '=', 'in_invoice'),  # فواتير الموردين (مصروفات)
#                 ('unit_number', '=', rec.product_id.id),  # نفس الوحدة
#                 ('state', '=', 'posted')  # فواتير مرحلة
#             ])
#             rec.unit_expenses = sum(expenses.mapped('amount_total'))

#     @api.depends('product_id')
#     def get_unit_revenues(self):
#         """حساب الإيرادات لنفس الوحدة"""
#         for rec in self:
#             # البحث عن جميع الفواتير المتعلقة بنفس الوحدة (المنتج) كإيرادات
#             revenues = self.env['account.move'].search([
#                 ('move_type', '=', 'out_invoice'),  # فواتير العملاء (إيرادات)
#                 ('unit_number', '=', rec.product_id.id),  # نفس الوحدة
#                 ('state', '=', 'posted'),  # فواتير مرحلة
#                 ('payment_state', 'in', ['paid', 'in_payment'])  # مدفوعة أو قيد الدفع
#             ])
#             rec.unit_revenues = sum(revenues.mapped('amount_total'))

#     @api.onchange('operating_unit_id')
#     def _onchange_operating_unit_id(self):
#         return {'domain': {'property_number': [('property_address_area.id', '=', self.operating_unit_id.id)]}}

#     @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
#     def _compute_amount(self):
#         """
#         Compute the amounts of the SO line.
#         """
#         for line in self:
#             price = line.price_unit + line.insurance_value + line.contract_admin_fees + line.contract_service_fees + line.contract_admin_sub_fees + line.contract_service_sub_fees * (
#                     1 - (line.discount or 0.0) / 100.0)
#             price_tax = line.price_unit + line.contract_admin_sub_fees + line.contract_service_sub_fees * (
#                     1 - (line.discount or 0.0) / 100.0)
#             taxes = line.tax_id.compute_all(price_tax, line.order_id.currency_id, line.product_uom_qty,
#                                             product=line.product_id, partner=line.order_id.partner_shipping_id)
#             line.update({
#                 'price_tax': taxes['total_included'] - taxes['total_excluded'],
#                 'price_total': taxes['total_included'],
#                 'price_subtotal': price,
#                 # 'price_subtotal': taxes['total_excluded'],
#             })
#             if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
#                     'account.group_account_manager'):
#                 line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

#     def get_rental_order_line_description(self):
#         return ""
#     @api.depends('return_date')
#     def _compute_is_late(self):
#         now = fields.Datetime.now()
        
#         for line in self:
#             if not line.return_date:
#                 line.is_late = False
#                 continue
                
#             try:
#                 line.is_late = line.return_date < now
#             except (TypeError, ValueError):
#                 line.is_late = False
#     # @api.depends('return_date')
#     # def _compute_is_late(self):
#     #     now = fields.Date.today()
#     #     for line in self:
#     #         # By default, an order line is considered late only if it has one hour of delay
#     #         line.is_late = line.return_date and line.return_date < now

