# -*- coding: utf-8 -*-

from odoo import fields, models


class UserActionManagerSequenceWizardLine(models.TransientModel):
    _name = "user.action.manager.sequence.wizard.line"
    _description = "User Action Manager Sequence Wizard Line"

    manager_rule_sequence_id = fields.Many2one("user.action.manager.rule.sequence", string="Manager Rule Sequence")
    manager_id = fields.Many2one('res.users', related="manager_rule_sequence_id.manager_id", readonly=True, store=True)
    next_state = fields.Char(string="Next Status", copy=False)
    sequence = fields.Integer(string="Sequence", required=True, copy=False)
    manager_sequence_wizard_id = fields.Many2one('user.action.manager.sequence.wizard',
                                                 string='User Action Manager Sequence', required=True,
                                                 ondelete="cascade")


class UserActionManagerSequenceWizard(models.TransientModel):
    _name = "user.action.manager.sequence.wizard"
    _description = "User Action Manager Sequence Wizard"

    lines_ids = fields.One2many("user.action.manager.sequence.wizard.line", "manager_sequence_wizard_id",
                                string="Lines")

    def update_manager_sequence(self):
        for line in self.lines_ids:
            line.manager_rule_sequence_id.write({"sequence": line.sequence, "next_state": line.next_state})
