import binascii
from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomCustomerPortal(CustomerPortal):

    @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, order_id, access_token=None, name=None, signature=None):
        # استدعاء الدالة الأصلية من CustomerPortal
        res = super(CustomCustomerPortal, self).portal_quote_accept(order_id)

        access_token = access_token or request.httprequest.args.get('access_token')

        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error):
            return {'error': _('Invalid signature data.')}

        # إذا لم يكن هناك دفعة مطلوبة
        if not order_sudo.has_to_be_paid():
            order_sudo.action_confirm()
            order_sudo._send_order_confirmation_mail()

        # توليد ملف PDF للطلب
        pdf = request.env.ref('sale.action_report_saleorder').with_user(SUPERUSER_ID)._render_qweb_pdf([order_sudo.id])[0]

        # إضافة رسالة على الطلب مع المرفق
        order_sudo.message_post(
            body=_('Order signed by %s' % name),
            attachments=[('%s.pdf' % order_sudo.name, pdf)],
            **({'token': access_token} if access_token else {})
        )

        # إعادة توجيه للعميل مع رسالة النجاح
        query_string = '&message=sign_ok'
        if order_sudo.has_to_be_paid(True):
            query_string += '#allow_payment=yes'

        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }
