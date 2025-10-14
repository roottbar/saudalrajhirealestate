# -*- coding: utf-8 -*-

from odoo import models


class ReportRentalAIInsights(models.AbstractModel):
    _name = 'report.rental_ai_insights.ai_insights_report_template'
    _description = 'Report: Rental AI Insights'

    def _get_report_values(self, docids, data=None):
        docs = self.env['rental.ai.insights.wizard'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'rental.ai.insights.wizard',
            'docs': docs,
            'data': data or {},
            'o': docs[:1],
        }