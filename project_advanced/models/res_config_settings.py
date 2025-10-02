from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    duration_between_tasks = fields.Float(string="Duration")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['duration_between_tasks'] = self.env['ir.config_parameter'].sudo().get_param('project_advanced.duration_between_tasks')
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('project_advanced.duration_between_tasks', self.duration_between_tasks)
        super(ResConfigSettings, self).set_values()

