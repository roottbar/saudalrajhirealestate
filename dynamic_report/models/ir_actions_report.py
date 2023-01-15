from odoo import fields, models, api


class ActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    dynamic_report = fields.Boolean()
    template_id = fields.Many2one('report.template')
    # report_type = fields.Selection(selection_add=[("docx", "Docx")])
