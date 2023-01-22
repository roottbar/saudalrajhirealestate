# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import safe_eval


class UserActionRule(models.Model):
    _name = 'user.action.rule'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "User Action Rule"

    name = fields.Char(string="Name", copy=False, required=True, tracking=True, translate=True)
    code = fields.Char(string="Code", copy=False, tracking=True)
    action_rule_line_ids = fields.One2many("user.action.rule.line", "action_rule_id", string="Lines")

    def get_action_rule_line(self, model, record):
        action_rule_lines = self.sudo().env["user.action.rule.line"].search(
            [("action_rule_id", "=", self.id), ("object_id.model", "=", model)])
        line = False
        for action_rule_line in action_rule_lines:
            if action_rule_line.filter_domain and record.id not in action_rule_line.get_records_filter_domain():
                continue

            rule = action_rule_line.rule_id
            if not rule or rule.action_check_record_value(record):
                line = action_rule_line
                break

        return line


class UserActionManagerRuleSequence(models.Model):
    _name = "user.action.manager.rule.sequence"
    _description = "User Action Manager Rule sequence"
    _order = "sequence,id"

    manager_id = fields.Many2one('res.users', copy=False, required=True)
    next_state = fields.Char(string="Next Status", copy=False)
    sequence = fields.Integer(string="Sequence", copy=False, required=True, default=1)
    action_rule_line_id = fields.Many2one('user.action.rule.line', string='Action Rule Line', required=True,
                                          ondelete="cascade")


class UserActionRuleLine(models.Model):
    _name = 'user.action.rule.line'
    _description = "User Action Rule Line"
    _order = "sequence,object_id,id"

    object_id = fields.Many2one('ir.model', string='Object', required=True, copy=False, ondelete="cascade")
    model_name = fields.Char(related="object_id.model", string='Model Name', store=True, readonly=True)
    field_rule_ids = fields.Many2many('user.action.field.rule', string='Field Rules', copy=False,
                                      domain="[('object_id', '=', object_id)]")
    is_all = fields.Boolean(string="All Managers", copy=False, default=True,
                            help='Must be all managers approve to transfer for next action')
    manager_ids = fields.Many2many('res.users', string='Managers', copy=False, required=True, domain=[
        ('share', '=', False)])
    action_rule_id = fields.Many2one('user.action.rule', string='Action Rule', required=True, ondelete="cascade")
    manager_rule_sequence_ids = fields.One2many("user.action.manager.rule.sequence", "action_rule_line_id",
                                                string="Managers Rule Sequence")
    rule_id = fields.Many2one('user.action.line.rule', string='Rule', copy=False,
                              domain="[('object_id', '=', object_id)]")
    sequence = fields.Integer(string="Sequence", copy=False, required=True, default=1)
    filter_domain = fields.Char(string="Domain", copy=False)

    @api.onchange("manager_ids")
    def onchange_managers(self):
        lines = False
        manager_ids = self.manager_ids.ids
        manager_count = len(manager_ids)
        if manager_count != 0:
            lines = []
            manager_exists = set()
            for manager_rule_sequence in self.manager_rule_sequence_ids:
                if manager_rule_sequence.manager_id.id in manager_ids:
                    manager_exists.add(manager_rule_sequence.manager_id.id)
                else:
                    lines.append((3, manager_rule_sequence.id))

            new_manager_ids = set(manager_ids) - manager_exists

            for manager_id in new_manager_ids:
                vals = {
                    "manager_id": manager_id
                }
                lines.append((0, 0, vals))
        self.manager_rule_sequence_ids = lines

    def action_manager_sequence(self):
        action = self.sudo().env.ref("user_action_rule.action_manager_sequence_wizard", False)
        result = action.read()[0]
        lines = []
        for manager_rule_sequence in self.manager_rule_sequence_ids:
            vals = {
                'manager_rule_sequence_id': manager_rule_sequence.id,
                'next_state': manager_rule_sequence.next_state,
                'sequence': manager_rule_sequence.sequence,
            }
            lines.append((0, 0, vals))
        result["context"] = {"default_lines_ids": lines}

        return result

    @api.onchange('object_id')
    def _onchange_object_id(self):
        self.field_rule_ids = False
        self.rule_id = False
        self.filter_domain = False

    def get_records_filter_domain(self):
        domain = safe_eval.safe_eval(self.sudo().filter_domain)
        records = self.env[self.model_name].search(safe_eval.safe_eval(self.sudo().filter_domain)).ids

        return records

    def check_field_rules(self, record_id):
        # check max value for every field rule
        record = self.sudo().env[self.object_id.model].browse(record_id)

        if not record:
            raise ValidationError(_("Record not found"))

        for field_rule in self.field_rule_ids:
            field_rule.action_check_record_value(record)

        return True

    def check_action_object(self, action, record_id):
        # check if all managers apply action in record
        check = True

        if self.field_rule_ids:
            self.check_field_rules(record_id)

        if self.is_all:
            managers = self.sudo().env["user.action.rule.history"].search(
                [("record_id", "=", record_id), ("action", "=", action), ("object_id", "=", self.object_id.id),
                 ("manager_id", "in", self.manager_ids.ids), ("action_rule_line_id", "=", self.id)]).mapped(
                "manager_id")

            if len(managers) != len(self.manager_ids):
                check = False
        return check

    def check_access(self, action, record_id):
        user_action_rule_history_obj = self.sudo().env["user.action.rule.history"]
        # check current have access to apply action or already apply this action for same record
        user_id = self.env.user.id

        if user_id not in self.manager_ids.ids:
            return False
        else:
            history_count = user_action_rule_history_obj.search_count([
                ("record_id", "=", record_id),
                ("action", "=", action),
                ("object_id", "=", self.object_id.id),
                ("manager_id", "=", user_id),
                ("action_rule_line_id", "=", self.id)])
            if history_count != 0:
                return False

            # check sequence order,between every manager and current user
            sequence = self.manager_rule_sequence_ids.filtered(lambda l: l.manager_id == self.env.user).sequence
            for manager_rule_sequence in self.manager_rule_sequence_ids.filtered(
                    lambda l: l.manager_id != self.env.user):
                history_count = user_action_rule_history_obj.search_count([
                    ("record_id", "=", record_id),
                    ("action", "=", action),
                    ("object_id", "=", self.object_id.id),
                    ("manager_id", "=", manager_rule_sequence.manager_id.id),
                    ("action_rule_line_id", "=", self.id)])
                if history_count == 0 and manager_rule_sequence.sequence < sequence:
                    return False

            return True


class UserActionLineRule(models.Model):
    _name = "user.action.line.rule"
    _description = "User Action Line Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True, translate=True)
    object_id = fields.Many2one('ir.model', string='Object', required=True, tracking=True,
                                ondelete="cascade")
    field_id = fields.Many2one('ir.model.fields', string="Field", required=True, tracking=True,
                               domain="[('model_id', '=', object_id), ('ttype','in',['float','integer','monetary'])]",
                               ondelete="cascade")
    field_type = fields.Selection(related="field_id.ttype", string="Field Type", readonly=True, store=True)
    min_value = fields.Float(string="Min Value", tracking=True)
    max_value = fields.Float(string="Max Value", tracking=True)
    currency_field_id = fields.Many2one('ir.model.fields', string="Currency Field", tracking=True,
                                        domain="[('model_id', '=', object_id),('relation','=','res.currency'),('ttype','=','many2one')]",
                                        ondelete="cascade")

    @api.constrains("min_value", "max_value")
    def _check_value(self):
        if self.min_value < 0:
            raise ValidationError(_("Min Value must be  positive or equal to zero"))

        if self.max_value < 0:
            raise ValidationError(_("Max Value must be positive or equal to zero"))

        if self.max_value != 0 and self.min_value > self.max_value:
            raise ValidationError(_("Min Value must must be less than or equal to Max Value"))

    @api.onchange('object_id')
    def _onchange_object_id(self):
        if self.object_id:
            self.field_id = False
            self.currency_field_id = False

    def action_check_record_value(self, record):
        # check min value and max value for record
        min_value = self.min_value
        max_value = self.max_value
        record_currency_id = self.currency_field_id and getattr(record, self.currency_field_id.name) or False
        company_currency_id = self.env.user.company_id.currency_id
        valid = True

        if min_value != 0:
            if self.field_type != "integer" and self.currency_field_id and record_currency_id and company_currency_id and record_currency_id != company_currency_id:
                min_value = company_currency_id._convert(min_value, record_currency_id, self.env.user.company_id,
                                                         fields.Date.today())

            if getattr(record, self.field_id.name) < min_value:
                valid = False

        if valid and max_value != 0:
            if self.field_type != "integer" and self.currency_field_id and record_currency_id and company_currency_id and record_currency_id != company_currency_id:
                max_value = company_currency_id._convert(max_value, record_currency_id, self.env.user.company_id,
                                                         fields.Date.today())

            if getattr(record, self.field_id.name) > max_value:
                valid = False

        return valid


class UserActionFieldRule(models.Model):
    _name = 'user.action.field.rule'
    _description = "User Action Field Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True, translate=True)
    object_id = fields.Many2one('ir.model', string='Object', required=True, tracking=True,
                                ondelete="cascade")
    field_id = fields.Many2one('ir.model.fields', string="Field", required=True, tracking=True,
                               domain="[('model_id', '=', object_id), ('ttype','in',['float','integer','monetary'])]",
                               ondelete="cascade")
    field_type = fields.Selection(related="field_id.ttype", string="Field Type", readonly=True, store=True)
    max_value = fields.Float(string="Max Value", required=True, tracking=True)
    currency_field_id = fields.Many2one('ir.model.fields', string="Currency Field", tracking=True,
                                        domain="[('model_id', '=', object_id),('relation','=','res.currency'),('ttype','=','many2one')]",
                                        ondelete="cascade")

    @api.constrains("max_value")
    def _check_max_value(self):
        if self.max_value <= 0:
            raise ValidationError(_("Max Value must be positive"))

    @api.onchange('object_id')
    def _onchange_object_id(self):
        if self.object_id:
            self.field_id = False
            self.currency_field_id = False

    def action_check_record_value(self, record):
        # check max value for record
        max_value = self.max_value
        if self.field_type != "integer" and self.currency_field_id:
            # get currency of record
            record_currency_id = getattr(record, self.currency_field_id.name)
            company_currency_id = self.env.user.company_id.currency_id
            if record_currency_id and company_currency_id and record_currency_id != company_currency_id:
                max_value = company_currency_id._convert(max_value, record_currency_id, self.env.user.company_id,
                                                         fields.Date.today())

        if getattr(record, self.field_id.name) > max_value:
            raise ValidationError(
                _("Can't approval because %s must be less than or equal to %s") % (
                    self.field_id.field_description, max_value))


class UserActionRuleHistory(models.Model):
    _name = 'user.action.rule.history'
    _description = "User Action Rule History"

    manager_id = fields.Many2one('res.users', string='Manager', required=True, copy=False)
    object_id = fields.Many2one('ir.model', string='Object', required=True, copy=False, ondelete='cascade')
    action_rule_line_id = fields.Many2one('user.action.rule.line', string='Action Rule Line', required=True, copy=False)
    action = fields.Char(string="Action", required=True, copy=False, translate=True)
    record_id = fields.Integer("Record ID", required=True, copy=False)
