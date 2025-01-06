
import base64
from odoo import api, fields, models, _
from collections import defaultdict
from odoo.addons.base.models.res_partner import _tz_get
import pytz
from datetime import datetime
from ..zk import ZK
from odoo.exceptions import UserError, ValidationError
import re
import requests
import json


class BiostarApi(models.Model):
    _name = 'biostar.api'
    _description = 'Biostar 2 Api'

    name = fields.Char(string='Name', required=True)
    device_ip = fields.Char(string='Device IP')
    port = fields.Integer(string='Port')
    device_id = fields.Char(string='Device Id', null=True, blank=True)
    serial_number = fields.Char('Serial Number')
    device_password = fields.Char(string='Device Password', null=True, blank=True)
    time_zone = fields.Selection(_tz_get, string='Timezone', default=lambda self: self.env.user.tz or 'GMT')
    state = fields.Selection([('not_connected', 'Not Connected'),
                              ('connected', 'Connected')],
                             default='not_connected')
    bs_session_id = fields.Text(string='bs session id')

    def check_connection(self):
        protocols = ["https", "http"]
        ports = [443, 80]

        payload = json.dumps({
            "User": {
                "login_id": self.device_id,
                "password": self.device_password,
            }
        })
        headers = {
            'Content-Type': 'application/json'
        }

        for protocol in protocols:
            url = f"{protocol}://{self.device_ip}/api/login"
            try:
                response = requests.post(url, headers=headers, data=payload, timeout=10, verify=False)

                if response.status_code == 200:
                    bs_session_id = response.headers.get('bs-session-id')
                    if bs_session_id:
                        self.write({
                            'bs_session_id': bs_session_id,
                            'state': 'connected',
                        })
                        return True

                    else:
                        raise UserError(
                            _("Connection successful but 'bs-session-id' is missing in the response headers."))
                else:
                    print(f"Failed with status code {response.status_code}: {url}")
            except requests.exceptions.RequestException as e:
                print(f"Connection error to {url}: {e}")
        self.write({'state': 'not_connected'})
        raise UserError(_("Failed to connect to the device at IP: %s") % self.device_ip)

    def test_device_connection(self):
        ip = self.device_ip
        port = self.port
        password = self.device_password
        zk = ZK(ip, port, password=password)
        try:
            conn = zk.connect()
            if conn:
                raise UserError(_("Connection Success"))
            else:
                raise ValidationError(_("Connection Failed"))
        except Exception as e:
            # print(e)
            raise UserError(_(e))



