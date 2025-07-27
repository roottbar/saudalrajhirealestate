# -*- coding: utf-8 -*-
# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    workorder = fields.Many2one(
        comodel_name='mrp.workorder', string='Work Order')
    mrp_production_id = fields.Many2one(
        'mrp.production', string='Manufacturing Order')
    final_product = fields.Many2one(
        comodel_name='product.product', string='Product to Produce',
        store=False, related='mrp_production_id.product_id')

    def name_get(self):
        if self.env.context.get('name_show_user'):
            res = []
            for task in self:
                user_name = task.user_ids[0].name if task.user_ids else 'No User'
                res.append(
                    (task.id, "[%s] %s" % (user_name, task.name)))
            return res
        return super(ProjectTask, self).name_get()