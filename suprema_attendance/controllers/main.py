from odoo import http
from odoo.http import request

class SupremaController(http.Controller):
    @http.route('/suprema/device/status', type='json', auth='user')
    def device_status(self, device_id):
        device = request.env['suprema.device'].browse(device_id)
        if not device.exists():
            return {'error': 'Device not found'}
        
        try:
            conn = device.connect_device()
            status = conn.get_device_status()
            conn.disconnect()
            return {'status': status}
        except Exception as e:
            return {'error': str(e)}