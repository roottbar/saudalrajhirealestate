
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
        payload = json.dumps({
            "User": {
                "login_id": self.device_id,
                "password": self.device_password,
            }
        })
        headers = {'Content-Type': 'application/json'}

        for protocol in protocols:
            url = f"{protocol}://{self.device_ip}/api/login"
            print(f"Attempting connection to: {url}")
            print(f"Payload: {payload}")

            try:
                response = requests.request("POST", url, headers=headers, data=payload, verify=False)
                print(f"Response Status: {response.status_code}")
                print(f"Response Text: {response.text}")

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
                    if response.status_code == 401:
                        raise UserError(_("Unauthorized: Check your device credentials."))
                    elif response.status_code == 403:
                        raise UserError(_("Forbidden: Access denied to the device."))
                    else:
                        raise UserError(_("Failed to connect: %s") % response.text)
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                raise UserError(_("Failed to connect due to a network error: %s") % str(e))

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



