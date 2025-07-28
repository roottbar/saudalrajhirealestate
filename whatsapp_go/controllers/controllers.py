from odoo import http, SUPERUSER_ID
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ConfirmSalesOrderController(http.Controller):

    @http.route('/confirm_order', type='json', auth='none', csrf=False)
    def confirm_order(self, **kwargs):
        data = http.request.jsonrequest
        order_name = data.get('order_name')
        if not order_name:
            return {'error': 'Missing order_name'}

        env = request.env(user=SUPERUSER_ID)
        sale_order = env['sale.order'].sudo().search([('name', '=', order_name)], limit=1)
        if not sale_order:
            return {'error': f"Sale order '{order_name}' not found"}

        if sale_order.state != 'draft':
            return {'error': f"Sale order '{order_name}' is not in draft state, current state: {sale_order.state}"}

        try:
            sale_order.with_context(mail_auto_subscribe_no_notify=True,api=True).action_confirm()
        except Exception as e:
            _logger.error(f"Error confirming order: {str(e)}")
            return {'error': str(e)}

        return {
            'message': 'Sale Order confirmed, invoice and draft payment created successfully.',
            'sale_order_id': sale_order.id,
        }
