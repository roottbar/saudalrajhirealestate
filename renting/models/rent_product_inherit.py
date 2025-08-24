# -*- coding: utf-8 -*-

from odoo import api, models, fields


class RentProduct(models.Model):
    _inherit = 'product.template'

    unit_number = fields.Char(string='رقم الوحدة')
    unit_area = fields.Char(string='مساحة الوحدة')
    unit_floor_number = fields.Char(string='رقم الطابق')
    unit_rooms_number = fields.Char(string='عدد الغرف')
    unit_state = fields.Char(compute='_get_state', string='الحالة', default='شاغرة')

    rent_unit_area = fields.Float(string='المساحة')

    furniture_bedroom = fields.Boolean(string='غرفة نوم')
    furniture_bedroom_no = fields.Integer(string=' عدد غرف النوم')
    furniture_bathroom = fields.Boolean(string='حمام')
    furniture_bathroom_no = fields.Integer(string=' عدد الحمام')
    furniture_reception = fields.Boolean(string='ريسيبشن')
    furniture_reception_no = fields.Integer(string=' عدد الريسيبشن')
    furniture_kitchen = fields.Boolean(string='مطبخ')
    furniture_service_room = fields.Boolean(string='غرفة خدم')
    furniture_inventory = fields.Boolean(string='مخزن')
    furniture_inventory_no = fields.Integer(string=' عدد المخازن')
    furniture_setting_room = fields.Boolean(string='غرفة المعيشة')
    furniture_setting_room_no = fields.Integer(string=' عدد غرف المعيشة')
    furniture_central_air_conditioner = fields.Boolean(string='تكييف مركزي')
    furniture_split_air_conditioner = fields.Boolean(string='تكييف سبليت')
    furniture_split_air_conditioner_no = fields.Integer(string=' عدد تكييف سبليت')
    furniture_evaporator_cooler = fields.Boolean(string='مدخنة')
    furniture_evaporator_cooler_no = fields.Integer(string=' عدد المداخن')
    furniture_kitchen_installed = fields.Boolean(string='مطبخ مجهز')
    furniture_locker_installed = fields.Boolean(string='غرفة ملابس')
    furniture_locker_installed_no = fields.Integer(string=' عدد غرف الملابس')

    unit_construction_date = fields.Date(string='تاريخ الانشاء')

    rent_config_unit_overlook_id = fields.Many2one('rent.config.unit.overlooks', string='Unit Overlooking', copy=True)
    rent_config_unit_type_id = fields.Many2one('rent.config.unit.types', string='Unit type', copy=True)
    rent_config_unit_purpose_id = fields.Many2one('rent.config.unit.purposes', string='Unit Purpose', copy=True)
    rent_config_unit_finish_id = fields.Many2one('rent.config.unit.finishes', string='Unit Finish', copy=True)

    property_id = fields.Many2one('rent.property', string='عمارة', copy=True)
    property_address_build = fields.Many2one('rent.property.build', string='المجمع',
                                             related='property_id.property_address_build', store=True, index=True)
    property_address_city = fields.Many2one('rent.property.city', string='المدينة',
                                            related='property_id.property_address_city', store=True)
    country = fields.Many2one('res.country', string='الدولة', related='property_id.country', store=True, index=True)
    operating_unit = fields.Many2many('operating.unit', string='الفرع ')

    entry_number = fields.Char('عدد المداخل')
    entry_overlook = fields.Char('المداخل تطل علي')

    unit_gas = fields.Char(string='رقم عداد الغاز')
    unit_electricity = fields.Char(string='رقم عداد الكهرباء')
    unit_water = fields.Char(string='رقم عداد المياه')

    unit_expenses_count = fields.Integer(string='Total Expenses', compute='_unit_expenses_count', readonly=True)
    unit_sales_count = fields.Integer(string='Total Sales', compute='_unit_sales_count', readonly=True)
    unit_price = fields.Float(string='قيمة الوحدة', compute='_get_unit_price')
    unit_price_unit = fields.Char(string='مدة تأجير الوحدة')
    state_id = fields.Char()
    analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي', readonly=True)
    ref_analytic_account = fields.Char(string='رقم اشارة الحساب التحليلي', readonly=True)
    property_analytic_account = fields.Many2one('account.analytic.account', string='الحساب التحليلي للعقار',
                                                related='property_id.analytic_account')
    
    # إزالة الحقل المسبب للمشكلة مؤقتاً
    # property_analytic_account_parent = fields.Many2one(
    #     'account.analytic.plan',
    #     string='مجموعة الحساب التحليلي للعقار',
    #     compute='_compute_property_analytic_account_parent',
    #     store=False
    # )

    # @api.depends('property_id.analytic_account')
    # def _compute_property_analytic_account_parent(self):
    #     for rec in self:
    #         rec.property_analytic_account_parent = False
    #         if rec.property_id and rec.property_id.analytic_account:
    #             analytic_account = rec.property_id.analytic_account
    #             possible_fields = ['plan_id', 'category_id', 'parent_id', 'group_id']
    #             for field_name in possible_fields:
    #                 if hasattr(analytic_account, field_name):
    #                     field_value = getattr(analytic_account, field_name)
    #                     if field_value:
    #                         rec.property_analytic_account_parent = field_value
    #                         break

    @api.model_create_multi
    def create(self, vals_list):
        records = super(RentProduct, self).create(vals_list)
        
        for rec in records:
            if rec.property_id and rec.property_id.ref_analytic_account and rec.unit_number:
                rec.ref_analytic_account = f"{rec.property_id.ref_analytic_account}-{rec.unit_number}"
                
                # التحقق من عدم وجود حساب تحليلي مكرر
                existing_account = self.env['account.analytic.account'].sudo().search([
                    ('code', '=', rec.ref_analytic_account)
                ], limit=1)
                
                if existing_account:
                    rec.analytic_account = existing_account
                else:
                    # إنشاء الحساب التحليلي بدون الاعتماد على مجموعة محددة
                    analytic_account = self.env['account.analytic.account'].sudo().create({
                        'name': rec.name,
                        'code': rec.ref_analytic_account,
                    })
                    rec.analytic_account = analytic_account
        
        return records

    def _get_unit_price(self):
        for rec in self:
            prices = []
            units = []
            for price in rec.rental_pricing_ids:
                prices.append(price.price)
                units.append(price.unit)
            if len(prices) > 0:
                rec.unit_price = prices[0]
            if len(units) > 0:
                rec.unit_price_unit = units[0]
            else:
                rec.unit_price = 0
                rec.unit_price_unit = ''

    partner_id = fields.Many2one('res.partner', compute="get_sale_data", string='العميل')
    amount_paid = fields.Float(compute="get_sale_data", string='المبلغ المدفوع')
    amount_due = fields.Float(compute="get_sale_data", string='المبلغ المستحق')
    contract_admin_fees = fields.Float(compute="get_sale_data", string='رسوم إدارية')
    contract_service_fees = fields.Float(compute="get_sale_data", string='رسوم الخدمات')
    insurance_value = fields.Float(compute="get_sale_data", string='قيمة التأمين')
    fromdate = fields.Datetime(compute="get_sale_data", string='تاريخ الإستلام')
    todate = fields.Datetime(compute="get_sale_data", string='تاريخ التسليم')
    last_sale_id = fields.Many2one('sale.order', compute="get_sale_data")
    operating_unit_id = fields.Many2one('operating.unit', string='الفرع ')
    contract_total = fields.Float(compute="get_sale_data", string='قيمة العقد')

    def get_sale_data(self):
        for rec in self:
            order_line_id = rec.env['sale.order.line'].sudo().search([
                ('product_id', '=', rec.id)
            ], limit=1, order='id desc')
            
            if order_line_id and order_line_id.order_id:
                order = order_line_id.order_id
                rec.partner_id = order.partner_id.id
                rec.last_sale_id = order.id
                rec.contract_admin_fees = order_line_id.contract_admin_fees or 0
                rec.insurance_value = order_line_id.insurance_value or 0
                rec.contract_service_fees = order_line_id.contract_service_fees or 0
                rec.fromdate = order.fromdate
                rec.operating_unit_id = order.operating_unit_id.id
                rec.todate = order.todate
                
                # حساب المبلغ المدفوع
                paid_amount = 0
                if order.invoice_ids:
                    for invoice in order.invoice_ids:
                        if invoice.payment_state == 'paid':
                            for line in invoice.invoice_line_ids:
                                if line.product_id == rec.product_variant_id:
                                    paid_amount += line.price_subtotal
                rec.amount_paid = paid_amount
                
                rec.contract_total = order.amount_total or 0
                rec.amount_due = (order.amount_total - paid_amount) if order.amount_total else 0
            else:
                # تعيين القيم الافتراضية إذا لم يكن هناك طلب
                rec.partner_id = False
                rec.last_sale_id = False
                rec.contract_admin_fees = 0
                rec.insurance_value = 0
                rec.contract_service_fees = 0
                rec.fromdate = False
                rec.operating_unit_id = False
                rec.todate = False
                rec.amount_paid = 0
                rec.contract_total = 0
                rec.amount_due = 0

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(RentProduct, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'amount_paid' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_amount_paid = 0.0
                    for record in lines:
                        total_amount_paid += record.amount_paid
                    line['amount_paid'] = total_amount_paid
        if 'amount_due' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_amount_due = 0.0
                    for record in lines:
                        total_amount_due += record.amount_due
                    line['amount_due'] = total_amount_due
        if 'contract_admin_fees' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_contract_admin_fees = 0.0
                    for record in lines:
                        total_contract_admin_fees += record.contract_admin_fees
                    line['contract_admin_fees'] = total_contract_admin_fees
        if 'contract_service_fees' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_contract_service_fees = 0.0
                    for record in lines:
                        total_contract_service_fees += record.contract_service_fees
                    line['contract_service_fees'] = total_contract_service_fees
        if 'insurance_value' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_insurance_value = 0.0
                    for record in lines:
                        total_insurance_value += record.insurance_value
                    line['insurance_value'] = total_insurance_value
        return res

    def _get_state(self):
        for rec in self:
            rec.unit_state = 'شاغرة'
            rec.state_id = 'شاغرة'
            order = rec.env['sale.order.line'].sudo().search([
                ('product_id', '=', rec.id),
                ('property_number', '=', rec.property_id.property_name)
            ])
            if order:
                if order[0].order_id.rental_status == 'pickup':
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                elif order[0].order_id.rental_status == 'return':
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                elif order[0].order_id.rental_status == 'returned':
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
                elif order[0].order_id.rental_status == 'cancel':
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
            else:
                rec.state_id = 'شاغرة'
                rec.unit_state = 'شاغرة'

    def get_unit_maintenance(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'صيانات',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': {'default_move_type': 'in_invoice', 'default_journal_id': 2,
                        'default_property_name': self.property_id.id,
                        'default_unit_number': self.id, 'default_analytic_account': self.analytic_account.id},
        }

    def _unit_sales_count(self):
        self.unit_sales_count = self.env['sale.order.line'].search_count([
            ('product_id', '=', self.id),
            ('property_number', '=', self.property_id.property_name)])

    def unit_sales(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'ايجارات',
            'view_mode': 'form',
            'view_id': self.env.ref('sale_renting.rental_order_primary_form_view').id,
            'res_model': 'sale.order',
            'context': {'default_is_rental_order': True, 'default_property_name': self.property_id.id,
                        'default_unit_number': self.id, 'default_analytic_account_id': self.analytic_account.id},
        }
