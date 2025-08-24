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

    rent_config_unit_overlook_id = fields.Many2one(
        'rent.config.unit.overlooks', string='Unit Overlooking', copy=True
    )
    rent_config_unit_type_id = fields.Many2one(
        'rent.config.unit.types', string='Unit type', copy=True
    )
    rent_config_unit_purpose_id = fields.Many2one(
        'rent.config.unit.purposes', string='Unit Purpose', copy=True
    )
    rent_config_unit_finish_id = fields.Many2one(
        'rent.config.unit.finishes', string='Unit Finish', copy=True
    )

    property_id = fields.Many2one('rent.property', string='عمارة', copy=True)
    property_address_build = fields.Many2one(
        'rent.property.build', string='المجمع',
        related='property_id.property_address_build', store=True, index=True
    )
    property_address_city = fields.Many2one(
        'rent.property.city', string='المدينة',
        related='property_id.property_address_city', store=True
    )
    country = fields.Many2one(
        'res.country', string='الدولة',
        related='property_id.country', store=True, index=True
    )
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

    property_analytic_account = fields.Many2one(
        'account.analytic.account',
        string='الحساب التحليلي للعقار',
        related='property_id.analytic_account'
    )

    # تعديل الحقل المرتبط للبنت
    property_analytic_account_parent = fields.Many2one(
        'account.analytic.account',
        string='Parent Analytic Account',
        related='property_id.property_analytic_account_parent',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(RentProduct, self).create(vals_list)
        res.ref_analytic_account = f"{res.property_id.ref_analytic_account}-{res.unit_number}"
        analytic_account = self.env['account.analytic.account'].sudo().create({
            'name': res.name,
            'parent_id': res.property_analytic_account_parent.id,
            'code': res.ref_analytic_account
        })
        res.analytic_account = analytic_account
        return res

    def _get_unit_price(self):
        for rec in self:
            if rec.rental_pricing_ids:
                rec.unit_price = rec.rental_pricing_ids[0].price
                rec.unit_price_unit = rec.rental_pricing_ids[0].unit
            else:
                rec.unit_price = 0
                rec.unit_price_unit = ''

    # Sale/Contract related fields
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
            order_line_id = rec.env['sale.order.line'].sudo().search(
                [('product_id', '=', rec.id)], limit=1, order='id desc'
            )
            if order_line_id:
                rec.partner_id = order_line_id.order_id.partner_id.id
                rec.last_sale_id = order_line_id.order_id.id
                rec.contract_admin_fees = order_line_id.contract_admin_fees
                rec.insurance_value = order_line_id.insurance_value
                rec.contract_service_fees = order_line_id.contract_service_fees
                rec.fromdate = order_line_id.order_id.fromdate
                rec.operating_unit_id = order_line_id.order_id.operating_unit_id.id
                rec.todate = order_line_id.order_id.todate
                rec.amount_paid = sum(
                    ll.price_subtotal for ll in order_line_id.order_id.invoice_ids.invoice_line_ids
                    if ll.move_id.payment_state == 'paid' and ll.product_id == rec.product_variant_id
                )
                rec.contract_total = order_line_id.order_id.amount_total
                rec.amount_due = sum(
                    order_line_id.order_id.order_line[0].price_unit / ll.sale_order_id.invoice_number
                    for ll in order_line_id.order_id.order_contract_invoice
                    if ll.status == 'uninvoiced'
                ) if order_line_id.order_id.order_line else 0.0
            else:
                rec.partner_id = False
                rec.last_sale_id = False
                rec.contract_admin_fees = 0
                rec.contract_service_fees = 0
                rec.insurance_value = 0
                rec.fromdate = False
                rec.todate = False
                rec.operating_unit_id = False
                rec.amount_paid = 0
                rec.amount_due = 0
                rec.contract_total = 0

    def _get_state(self):
        for rec in self:
            rec.unit_state = 'شاغرة'
            rec.state_id = 'شاغرة'
            order = rec.env['sale.order.line'].sudo().search([
                ('product_id', '=', rec.id),
                ('property_number', '=', rec.property_id.property_name)
            ])
            if order:
                status = order[0].order_id.rental_status
                if status in ['pickup', 'return']:
                    rec.state_id = 'مؤجرة'
                    rec.unit_state = 'مؤجرة'
                elif status in ['returned', 'cancel']:
                    rec.state_id = 'شاغرة'
                    rec.unit_state = 'شاغرة'
            else:
                rec.state_id = 'شاغرة'
                rec.unit_state = 'شاغرة'

    # Sales/Expenses counts
    def _unit_sales_count(self):
        for rec in self:
            rec.unit_sales_count = self.env['sale.order.line'].search_count([
                ('product_id', '=', rec.id),
                ('property_number', '=', rec.property_id.property_name)
            ])
