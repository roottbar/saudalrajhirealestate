from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from hijri_converter import Hijri, Gregorian




class RentalLetterTemplate(models.Model):
    _name = 'rental.letter.template'
    _description = 'Rental Letter Templates'
    _rec_name='ref'

    ref = fields.Char(string='Reference')
    subject = fields.Selection([('option1','اخلاء عقار'),
                                ('option2', 'تسليم العين المؤجرة من المستأجر'),
                                ('option3', 'استلام العين المؤجرة من المستأجر'),
                                ('option4', 'تنازل عن عقد ايجار'),
                                ('option5','طلب تأجير تجاري'),
                                ('option6','طلب تأجير فردي'),
                                ('option7', 'تحديث القيمة الإيجارية'),
                                ('option8', 'مطالبة بسداد متأخرات'),
                                ('option9', 'إشعار بإنهاء التعاقد'),
                                ],string='Subject',required=True)

    today_date = fields.Date(string='Today Date', default= fields.Date.context_today)
    assigner = fields.Many2one("res.partner",string='Assigner')
    national_id_assigner=fields.Char(string='National ID No. Assigner')
    city=fields.Char(string='City')

    cash_receipts=fields.Char(string='Cash Receipts No.')
    cash_receipts_date=fields.Date(string='Cash Receipts Date')
    cash_receipts_value=fields.Char(string='Cash Receipts Value')

    e_invoice = fields.Char(string='e-invoice No.')
    e_invoice_date = fields.Date(string='e-invoice Date')
    insurance_value = fields.Char(string='Insurance Value')




    delay_date = fields.Date(string='Delay Date')
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    fee = fields.Monetary(string="Charges day's rental")

    beginning_contract = fields.Date(related='partner_id.fromdate',String='Contract Date')
    contract_number = fields.Char(related='partner_id.contract_number',String='Contract Number', readonly=False)

    end_contract = fields.Date(related='partner_id.todate')
    number = fields.Char(string='Letter No.')
    maximum_repayment_period = fields.Char(string='Maximum repayment period')
    rental_value = fields.Float(string='Rental Value')
    new_rental_value = fields.Float(string='New Rental Value')
    location = fields.Char(string='Location')
    property_type = fields.Char(string='Property Type')
    change_reason = fields.Char(string='Change Reason')


    bank_id = fields.Many2one('res.bank', string='Bank')
    payment_period = fields.Char(string='Payment Period')
    bank_account = fields.Char(string='Bank Account')
    iban = fields.Char(string='IBAN')
    contract_date = fields.Date(string='Contract Date')
    new_contract_date = fields.Date(string='New Contract Date')
    eviction_period = fields.Char(string='Eviction Period')
    daily_rent_value = fields.Float(string='Daily Rent Value')
    credit_officer = fields.Char(string='Credit Officer ')
    credit_officer_opinion = fields.Text(string='Credit Officer Opinion ')
    property_manager = fields.Char(string='Property manager')
    property_manager_opinion  = fields.Text(string='Property manager Opinion')


    partner_id = fields.Many2one('sale.order',string='Customer')

    commercial_registration_number = fields.Char(string='Commercial Registration Number')
    national_address_main_center= fields.Char(string='National Address Of The Main Center')
    contact_number = fields.Char(string='Contact Number With Department')
    renting_purpose = fields.Char(string='Renting Purpose')
    nature_of_commerce = fields.Char(string='Nature of commerce')
    manager = fields.Char(string='Commissioner Director')
    manager_identity = fields.Char(string='Manager Identity')
    targeted_group = fields.Char(string='Targeted Group')


    invoice_ids = fields.Many2many('rent.due.invoice', 'letter_template_id', string='Due Invoices')

    door_good = fields.Boolean(string='جيد')
    door_bad = fields.Boolean(string='سئ')
    door_comment = fields.Char(string='حدد')
    door_note= fields.Text(string='ملاحظات')
    wall_good = fields.Boolean('جيد')
    wall_bad = fields.Boolean('سئ')
    wall_comment = fields.Char('حدد')
    wall_note= fields.Text(string='ملاحظات')
    window_good = fields.Boolean('جيد')
    window_bad = fields.Boolean('سئ')
    window_comment = fields.Char('حدد')
    window_note= fields.Text(string='ملاحظات')
    water_good = fields.Boolean('جيد')
    water_bad = fields.Boolean('سئ')
    water_comment = fields.Char('حدد')
    water_note= fields.Text(string='ملاحظات')
    elec_good = fields.Boolean('جيد')
    elec_bad = fields.Boolean('سئ')
    elec_comment = fields.Char('حدد')
    elec_note= fields.Text(string='ملاحظات')

    customer_accept = fields.Boolean('نعم')
    customer_refused = fields.Boolean('لا')

    rental_payments_yes=fields.Boolean('نعم')
    rental_payments_no=fields.Boolean('لا')
    rental_payments=fields.Monetary(string='المبلغ')

    remaining_amount_yes=fields.Boolean('نعم')
    remaining_amount_no=fields.Boolean('لا')
    remaining_amount=fields.Monetary(string='المبلغ')

    elec_yes=fields.Boolean('نعم')
    elec_no=fields.Boolean('لا')
    elec_amount=fields.Monetary(string='المبلغ')


    electricity_meter_no=fields.Char('رقم عداد الكهرباء')
    electricity_amount_due=fields.Char('المبلغ المستحق')
    elec_found = fields.Boolean('يوجد')
    elec_not_found = fields.Boolean('لا يوجد')
    elec_payment = fields.Boolean('تم السداد')
    elec_not_payment = fields.Boolean('لم يتم السداد ')

    water_meter_no = fields.Char('رقم عداد المياه')
    water_amount_due = fields.Char('المبلغ المستحق')
    water_found = fields.Boolean('يوجد')
    water_not_found = fields.Boolean('لا يوجد')
    water_payment = fields.Boolean('تم السداد')
    water_not_payment = fields.Boolean('لم يتم السداد ')

    rental_value = fields.Monetary(string="Rental Value")
    deposits_paid=fields.Monetary(string="التأمين المدفوع")
    mangement_accept = fields.Boolean('نعم')
    mangement_refused = fields.Boolean('لا')
    note = fields.Text(string='ملاحظة')

    employer = fields.Char(string='Employer')
    job = fields.Char(string='Job')
    salary_definition = fields.Char(string='Salary Definition')
    martial_status = fields.Char(string='Martial Status')
    family_members = fields.Integer(string='Family Members')
    simah_report = fields.Char(string='Simah Report')

    chief_executive=fields.Boolean('موافق')
    chief_executive_no=fields.Boolean('غير موافق')

    assignee=fields.Char(string='Assignee')
    unwillingness_to_renew = fields.Char(string='Days')
    end_contractual_relationship=fields.Date(string='Date end of the contractual relationship')
    leased_property=fields.Date(string='Date of leased property')

    vacating_the_property=fields.Char(string='Days vacating the property')
    new_rental_year=fields.Date(string='New Rental Year')
    rental_value_old = fields.Monetary(string="Rental Value")
    rental_value_new = fields.Monetary(string="Rental Value new")

    @api.model
    def create(self, vals):
        vals['ref'] = self.env["ir.sequence"].next_by_code('letters.sequence')
        return super(RentalLetterTemplate, self).create(vals)

    def get_date_hijri(self, gregorian_date):
        hijri_date = ''
        if gregorian_date:
            day = gregorian_date.day
            month = gregorian_date.month
            year = gregorian_date.year
            hijri_date = Gregorian(year, month, day).to_hijri()
        return hijri_date

    def get_date_name(self,gregorian_date):
        days_name = {
            '0':'الاثنين',
            '1':'الثلاثاء',
            '2':'الاربعاء',
            '3':'الخميس',
            '4':'الجمعة',
            '5':'السبت',
            '6':'الاحد',
        }
        day_name = self.today_date.weekday()
        return days_name[str(day_name)]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def name_get(self):
        if not self._context.get('letter'):
            return super(SaleOrder, self).name_get()
        res = []
        for record in self:
         name = str(record.partner_id.name)+"["+ record.name +"]"
         res.append((record.id, name))
        return res


class RentDueInvoice(models.Model):
    _name = 'rent.due.invoice'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    amount = fields.Float(string='Amount')
    tax_amount = fields.Float(string='Tax Amount')
    total=fields.Float(string='Total')
    letter_template_id = fields.Many2one('rental.letter.template')

    # @api.depends('amount','tax_amount')
    # def _compute_price(self):
    #     for line in self:






