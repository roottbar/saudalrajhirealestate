from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enforce_ou_company_match = fields.Boolean(
        string='فرض تطابق الشركة مع الفرع (Operating Unit)',
        config_parameter='payment_enhancements_ou.enforce_ou_company_match',
        default=False,
        help='عند التفعيل، يجب أن تكون شركة الحركة مطابقة لشركة الـ Operating Unit. عند التعطيل، لا تظهر رسالة الخطأ ولا يتم فرض القيد.'
    )