# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
import requests
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
import json    
from odoo import http,SUPERUSER_ID
import os
from datetime import datetime, timedelta,date
import re
import mimetypes

class SaleOrder(models.Model):
    _inherit ="sale.order"
    
    
    def action_confirm(self):
        api_flag = self._context.get('api', False)
        res = super(SaleOrder, self).action_confirm()
        self.send_pdf_for_whatsapp(self)
        return res
        
    
    def send_pdf_for_whatsapp(self):
        api_flag=True
        # Fetch the subscription expiry date from config
        expiry_str = self.env['ir.config_parameter'].sudo().get_param('Subscription_expire_date')
        
        if expiry_str:
            expiry_date = fields.Date.from_string(expiry_str)
            today = date.today()
            if expiry_date < today:

                url = f'{self.env["ir.config_parameter"].sudo().get_param("go4whatsapp_url")}/getCurentPlanDetailByOrg'
                payload = json.dumps({
                "orgId": self.env["ir.config_parameter"].sudo().get_param("org_id")
                })
                headers = {
                'authorization': self.env.user.go4whatsapp_access_token,
                'Content-Type': 'application/json',
                'Cookie': 'HttpOnly'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                expiry_date_str = response.json().get("getCurentPlanDetailByuser")[0]["expiryDate"]

                # Convert to date object
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()

                # Store in system parameter
                self.env['ir.config_parameter'].sudo().set_param('Subscription_expire_date', expiry_date.isoformat())

                expiry_str = self.env['ir.config_parameter'].sudo().get_param('Subscription_expire_date')
                if expiry_date < today:
                  raise UserError(("Your plan has expired. Please check your WhatsApp Go subscription plan."))

        else:
            raise UserError(("Subscription expiry date not set. Please configure your WhatsApp Go plan."))
        if self.env.user.go4whatsapp_access_token or api_flag == True:
            try:
                endpoint = "/sendDocumentINOddo"
                # Ensure the data is properly decoded as binary data

                report = self.env.ref('sale.action_report_saleorder')

                # Render the report as PDF
                pdf_content, content_type = report._render_qweb_pdf(self.ids)

                # Create directory if it doesn't exist
                pdf_directory = os.path.join(os.getcwd(), 'pdf_reports')
                os.makedirs(pdf_directory, exist_ok=True)

                # Define PDF file path
                file_path = os.path.join(pdf_directory, f'{self.name}.pdf')

                # Write the PDF content to the file
                with open(file_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_content)


                # data = self.env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', [self.id])[0]

                # # Get current directory and define the file path
                # current_directory = os.getcwd()
                # pdf_directory = f'{current_directory}/pdf_reports'
                # os.makedirs(pdf_directory, exist_ok=True)
                # file_path = f'{pdf_directory}/{self.name}.pdf'

                # # Write binary data to the file
                # with open(file_path, 'wb') as file:
                #     file.write(data)

                # Validate MIME type of the PDF
                
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type != "application/pdf":
                    raise UserError("Generated file is not a valid PDF.")

                # Validate partner details
                if not self.partner_id.country_id:
                    raise UserError('Please select country from customer')
                if not self.partner_id.mobile:
                    raise UserError('Invalid Number')

                mobile_no = f"{self.partner_id.mobile}"

                # Get the Go4Whatsapp URL from the configuration parameters
                setting_object = self.env["ir.config_parameter"].sudo()
                url = setting_object.get_param("go4whatsapp_url") + endpoint
                template_id = setting_object.get_param("template_id")
                org_id = setting_object.get_param("org_id")

                # import pdb;pdb.set_trace()
                files=[
                ('file',(f'{self.name}.pdf',open(file_path,'rb'),'application/pdf'))
                ]
                
                payload = {
                    "moNumber": mobile_no,
                    "templatedId": template_id,
                    "orgId": org_id,
                    "userName": self.partner_id.name,
                    "documentType": "quotation"
                }
                
                headers = {
                    # 'Authorization': f'Bearer {self.env.user.go4whatsapp_access_token}',
                    # 'Content-Type': 'application/pdf'
                }

                response = requests.request("POST", url, headers=headers, data=payload, files=files)

                print(response.text)

                print("Request Headers:", headers)
                print("Request Payload:", payload)
                print("File Info:", files)
                print("Response Status Code:", response.status_code)
                print("Response Text:", response.text)

                if response.status_code == 200:
                    print("File sent successfully.", response.json())
                else:
                    print("Failed to send file:", response.status_code, response.text)

            except Exception as e:
                print(f"Error: {e}")
                raise UserError(f'Failed to send the data: {e}')
        else:
            raise AccessError("Please login on Go4Whatsapp. Go to Settings-> Users & Companies -> Users -> Under Go4whatsapp tab click on the login button.")

        
class AccountMove(models.Model):
    _inherit ="account.move"
    
    followup_date = fields.Date()
    
    def action_post(self):
        res = super(AccountMove, self).action_post()
        
        today = datetime.today()
        
        if self.invoice_date_due:
            self.followup_date = self.invoice_date_due
        
        elif self.invoice_payment_term_id:
            if "immediate payment" in self.invoice_payment_term_id.name.lower() or "immediate settlement" in self.invoice_payment_term_id.name.lower():
                self.followup_date = today
            
            elif "end of following month" in self.invoice_payment_term_id.name.lower():
                next_month = today.replace(day=28) + timedelta(days=4)
                end_of_next_month = next_month.replace(day=calendar.monthrange(next_month.year, next_month.month)[1])
                self.followup_date = end_of_next_month
            
            elif re.search(r"\d+ days after end of next month", self.invoice_payment_term_id.name.lower()):
                days_match = re.search(r"(\d+)", self.invoice_payment_term_id.name)
                days = int(days_match.group(1)) if days_match else 0
                next_month = today.replace(day=28) + timedelta(days=4)
                end_of_next_month = next_month.replace(day=calendar.monthrange(next_month.year, next_month.month)[1])
                self.followup_date = end_of_next_month
            
            elif re.search(r"\d+% now, balance \d+ days", self.invoice_payment_term_id.name.lower()):
                days_match = re.search(r"balance (\d+)", self.invoice_payment_term_id.name.lower())
                days = int(days_match.group(1)) if days_match else 0
                self.followup_date = today + timedelta(days=days)
            
            elif "15th of next month" in self.invoice_payment_term_id.name.lower():
                next_month = today.replace(day=28) + timedelta(days=4)
                fifteenth_next_month = next_month.replace(day=15)
                self.followup_date =  fifteenth_next_month
            
            elif re.search(r"end of \d+ year", self.invoice_payment_term_id.name.lower()):
                # Extract number of years and calculate end of that future year
                years_match = re.search(r"end of (\d+) year", self.invoice_payment_term_id.name.lower())
                years = int(years_match.group(1)) if years_match else 0
                future_year = today.year + years
                self.followup_date =  datetime(future_year, 12, 31)
            
            elif "end of year" in self.invoice_payment_term_id.name.lower() or "close of the year" in self.invoice_payment_term_id.name.lower():
                self.followup_date =  datetime(today.year, 12, 31)
            
            elif re.search(r"\d+ days", self.invoice_payment_term_id.name.lower()):
                days_match = re.search(r"(\d+) days", self.invoice_payment_term_id.name.lower())
                days = int(days_match.group(1)) if days_match else 0
                self.followup_date = today + timedelta(days=days)
            
            elif "two days from now" in self.invoice_payment_term_id.name.lower():
                self.followup_date =  today + timedelta(days=2)

            else:
                raise ValueError("Could not determine expected date from sentence.")
            
        return res
    
    # def action_post(self):
    #     res = super(AccountMove, self).action_post()
    #     print("..................",self)
    #     self.send_pdf_for_whatsapp()
    #     return res
        
    
    def send_followup_report(self):
        today = datetime.today()
        
        due_invoices = self.env["account.move"].search([("followup_date", "=", today), ("payment_state", "not in", ["paid"])])
        
        for invoice in due_invoices:
            invoice.send_pdf_for_whatsapp()
    
    def send_pdf_for_whatsapp(self):

        # Fetch the subscription expiry date from config
        expiry_str = self.env['ir.config_parameter'].sudo().get_param('Subscription_expire_date')
        
        if expiry_str:
            expiry_date = fields.Date.from_string(expiry_str)
            today = date.today()
            if expiry_date < today:

                url = f'{self.env["ir.config_parameter"].sudo().get_param("go4whatsapp_url")}/getCurentPlanDetailByOrg'
                payload = json.dumps({
                "orgId": self.env["ir.config_parameter"].sudo().get_param("org_id")
                })
                headers = {
                'authorization': self.env.user.go4whatsapp_access_token,
                'Content-Type': 'application/json',
                'Cookie': 'HttpOnly'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                expiry_date_str = response.json().get("getCurentPlanDetailByuser")[0]["expiryDate"]

                # Convert to date object
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()

                # Store in system parameter
                self.env['ir.config_parameter'].sudo().set_param('Subscription_expire_date', expiry_date.isoformat())

                expiry_str = self.env['ir.config_parameter'].sudo().get_param('Subscription_expire_date')
                if expiry_date < today:
                  raise UserError(("Your plan has expired. Please check your WhatsApp Go subscription plan."))

        else:
            raise UserError(("Subscription expiry date not set. Please configure your WhatsApp Go plan."))
        
        if self.env.user.go4whatsapp_access_token:
            try:
                endpoint = "/sendDocumentINOddo"

                report = self.env.ref('account.account_invoices')  # Replace with actual report ID if needed

                pdf_content, content_type = report._render_qweb_pdf(self.ids)

                # Sanitize invoice name for file system (remove/replace slashes)
                safe_name = re.sub(r'[\\/:"*?<>|]+', "_", self.name or f'invoice_{self.id}')

                # Create PDF directory
                pdf_directory = os.path.join(os.getcwd(), 'pdf_reports')
                os.makedirs(pdf_directory, exist_ok=True)

                # Build full path to save the PDF
                file_path = os.path.join(pdf_directory, f'{safe_name}.pdf')

                # Save the PDF file
                with open(file_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_content)


                # Get the Go4Whatsapp URL from the configuration parameters
                setting_object = self.env["ir.config_parameter"].sudo()
                url = setting_object.get_param("go4whatsapp_url")+endpoint
                template_id = setting_object.get_param("template_id")
                org_id = setting_object.get_param("org_id")
                mobile_no = f"{self.partner_id.mobile}"
                 
                if not self.partner_id.country_id:
                    raise UserError('Please select country from customer')
                
                if not self.partner_id.mobile:
                    raise UserError('Invalid Number')
                
                # Define headers with the access token for authorization
                headers = {
                    # 'Authorization': f'Bearer {self.env.user.go4whatsapp_access_token}',
                    # 'Content-Type': 'application/pdf'
                }

                files=[
                ('file',(f'{self.id}.pdf',open(file_path,'rb'),'application/pdf'))
                ]
                
                payload = {
                    "moNumber": mobile_no,
                    "templatedId": template_id,
                    "orgId": org_id,
                    "userName": self.partner_id.name,
                    "documentType": "quotation"
                }
                print("Payload ", payload)
                
                response = requests.request("POST", url, headers=headers, data=payload, files=files)
                
                if response.status_code == 200:
                    print("File sent successfully.", response.json())
                else:
                    print("Failed to send file:", response.status_code, response.text)

            except Exception as e:
                print(f"Error: {e}")
                raise UserError(f'Failed to send the data: {e}')
        else:
            raise AccessError("Please login on Go4Whatsapp. Go to Settings-> Users & Companies -> Users -> Under Go4whatsapp tab click on the login button.")

        
# class AccountPayment(models.Model):
#     _inherit = "account.payment" 
    
#     def create(self, vals):
#         res = super(AccountPayment, self).create(vals)
#         if self.env.user.go4whatsapp_access_token:
#             endpoint = "/sendDocumentINOddo"
#             print(vals)
            
#             setting_object = self.env["ir.config_parameter"].sudo()
#             url = setting_object.get_param("go4whatsapp_url")+endpoint
#             template_id = setting_object.get_param("template_id")
#             org_id = setting_object.get_param("org_id")
#             mobile_no = f"+{self.partner_id.country_id.phone_code}{self.partner_id.mobile}"
                
#             if not self.partner_id.country_id:
#                 raise UserError('Please select country from customer')
            
#             if not self.partner_id.mobile:
#                 raise UserError('Invalid Number')
            
#             amount_total = "{:.2f}".format(res.amount_total)
            
#             message = f'''
#                 Hello {res.partner_id.name},
#                 We have successfully received your payment of {amount_total} for Invoice {res.name}.
#                 Thank you for your prompt payment.
#             '''
#             headers = {
#                 # 'Authorization': f'Bearer {self.env.user.go4whatsapp_access_token}'
#             }
#             url = self.env["ir.config_parameter"].sudo().get_param("go4whatsapp_url")
#             # payload = {"mobileNo": self.partner_id.mobile, "message": message}
            
#             payload = {
#                         "moNumber": mobile_no,
#                         "templatedId": template_id,
#                         "orgId": org_id,
#                         "userName": self.partner_id.name,
#                         "documentType": "quotation"
#                     }
#             response = requests.post(url, data=payload,  headers=headers)
            
#         else:
#             raise AccessError("Please login on Go4Whatsapp  Settings-> Users & Companies -> Users -> Under Go4whatsapp tab click on button for login.")
#         return res 
    
class ResUsers(models.Model):
    _inherit = "res.users"
    
    go4whatsapp_access_token = fields.Text()

    def open_whatsapp_login_form(self):
        
        return {
            'name': 'Go4Whatsapp Login',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'whatsapp.login',
            'target' : 'new'
        }
            
    
class LoginGo4Whatsapp(models.TransientModel):
    _name = "whatsapp.login"
    
    mobileNo = fields.Char(string="Mobile Number")
    isSocial = fields.Boolean(string="Is Socail")
    email = fields.Char(string="Email")


    def action_open_registration(self):


        import jwt
        import datetime

        """ Redirects to the registration page with a JWT token """
        secret_key = "OdooSecretKey"  # Replace with actual secret key
        payload = {
            "key": "OdooLead",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        base_url = "https://app.go4whatsup.com/registration"
        url = f"{base_url}?token={token}"

        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": url
        }
    
    
    def open_otp_verify_form(self):
        
        url = f'{self.env["ir.config_parameter"].sudo().get_param("go4whatsapp_url")}/oddoSignInUser'
        payload = {"mobileNo":self.mobileNo, "isSocial": False, "email": self.email}
        response = requests.post(url, data=payload)
        
        if response.json().get("ErrorCode") == 200:
            self.env.user.mobile = self.mobileNo
            return {
                'name': 'OTP Verify',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'otp.verify',
                'context': {'default_mobileNo': self.mobileNo},
                'target' : 'new'
            }
        else:
            raise UserError(response.json().get("ErrorMessage"))


class OTPVerify(models.TransientModel):
    _name = "otp.verify"
    
    mobileNo = fields.Char(string="Mobile Number", required=True)
    otp = fields.Char(string="OTP", required=True)
    
    def set_user_access_token(self):
        
        url = f'{self.env["ir.config_parameter"].sudo().get_param("go4whatsapp_url")}/oddoVerifyOtp'
        payload = {"mobileNo": self.mobileNo, "otp":self.otp}
        
        response = requests.post(url, data=payload)

        if response.json().get("ErrorCode") == 200:
            self.env.user.go4whatsapp_access_token = response.json().get("VerifyOtp").get("authtoken")
            self.env['ir.config_parameter'].sudo().set_param('org_id',response.json().get("VerifyOtp", {}).get("userDetail", [{}])[0].get("orgId"))
            self.env['ir.config_parameter'].sudo().set_param('template_id',"676a8bd7773ff7359741c764")
        
            url = f'{self.env["ir.config_parameter"].sudo().get_param("go4whatsapp_url")}/getCurentPlanDetailByOrg'

            payload = json.dumps({
            "orgId": self.env["ir.config_parameter"].sudo().get_param("org_id")
            })
            headers = {
            'authorization': response.json().get("VerifyOtp").get("authtoken"),
            'Content-Type': 'application/json',
            'Cookie': 'HttpOnly'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            expiry_date_str = response.json().get("getCurentPlanDetailByuser")[0]["expiryDate"]

            # Convert to date object
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()

            # Store in system parameter
            self.env['ir.config_parameter'].sudo().set_param('Subscription_expire_date', expiry_date.isoformat())

            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Login is confirmed',
                    'type': 'rainbow_man',
                    }
                }
        else:
            raise UserError(response.json().get("ErrorMessage"))
        

            
            