# -*- coding: utf-8 -*-
from odoo import models, fields


class ProjectTaskTemplate(models.Model):
    _name = "project.task.template"
    _description = "Project Task Templates"

    name = fields.Char(string="Name", required=True, translate=True)
    type_ids = fields.Many2many("project.task.type", string="Tasks Stages")




