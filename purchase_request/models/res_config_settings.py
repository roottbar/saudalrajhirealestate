from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approval_it_id = fields.Many2one('user.action.rule', string='Approval IT', copy=False)


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()

        config_parameters.set_param("purchase_request.approval_it_id", self.approval_it_id.id)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        config_parameters = self.env["ir.config_parameter"].sudo()

        approval_it_id = config_parameters.get_param("purchase_request.approval_it_id", False)
        res.update(
            approval_it_id=approval_it_id and eval(approval_it_id) or False,
        )
        return res
