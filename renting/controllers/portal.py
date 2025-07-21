# -*- coding: utf-8 -*-
import base64
import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomCustomerPortal(CustomerPortal):

    @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, order_id, access_token=None, name=None, signature=None):
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
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        if not order_sudo.has_to_be_paid():
            order_sudo.action_confirm()
            order_sudo._send_order_confirmation_mail()

        # Generate the PDF
        pdf = request.env.ref('sale.action_report_saleorder').with_user(SUPERUSER_ID)._render_qweb_pdf([order_sudo.id])[0]

        # Create the attachment
        attachment = request.env['ir.attachment'].sudo().create({
            'name': '%s.pdf' % order_sudo.name,
            'datas': base64.b64encode(pdf),
            'res_model': 'sale.order',
            'res_id': order_sudo.id,
            'type': 'binary',
            'mimetype': 'application/pdf',
        })

        # Post message with attachment
        order_sudo.message_post(
            body=_('Order signed by %s') % (name,),
            attachment_ids=[attachment.id],
        )

        query_string = '&message=sign_ok'
        if order_sudo.has_to_be_paid(True):
            query_string += '#allow_payment=yes'

        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }
