from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    go4whatsapp_url = fields.Char(string="Go4Whatsapp URL")
    template_id = fields.Char(string="Template ID")
    org_id = fields.Char(string="Organization ID")
    Subscription_expire_date = fields.Datetime(
        string='Subscription Expire Date'
    )
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['go4whatsapp_url'] = get_param('go4whatsapp_url')
        res['template_id'] = get_param('template_id')
        res['org_id'] = get_param('org_id')
        res['Subscription_expire_date'] = get_param('Subscription_expire_date')
        return res

    @api.model
    def set_values(self):
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('go4whatsapp_url',
                  self.go4whatsapp_url)
        set_param('template_id',
                  self.template_id)
        set_param('org_id',
                  self.org_id)
        set_param('Subscription_expire_date',self.Subscription_expire_date)
        
        super(ResConfigSettings, self).set_values()
    
