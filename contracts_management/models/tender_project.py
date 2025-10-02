# -*- coding: utf-8 -*-
import json

from odoo import models, fields, api, _
# from odoo.addons.sale_timesheet.models.project_overview import _to_action_data as to_action
from odoo.exceptions import UserError


class TenderProjectCategory(models.Model):
    _name = "tender.project.category"
    _description = "Tender Project Category"
    _parent_store = True
    _rec_name = "complete_name"
    _order = "complete_name"

    name = fields.Char("Name", required=True, index=True, translate=True, copy=False)
    complete_name = fields.Char("Complete Name", compute="_compute_complete_name", store=True)
    parent_id = fields.Many2one("tender.project.category", "Parent Category", index=True, ondelete="cascade")
    child_id = fields.One2many("tender.project.category", "parent_id", "Child Categories")
    parent_path = fields.Char(index=True)

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = "%s / %s" % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class TenderProject(models.Model):
    _name = "tender.project"
    _description = "Tender Projects"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name", required=True, index=True, translate=True, copy=False, tracking=True)
    ref = fields.Char(string="Reference", copy=False, tracking=True)
    partner_id = fields.Many2one("res.partner", required=True, string="Customer", index=True, copy=False,
                                 check_company=True, tracking=True,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    category_id = fields.Many2one("tender.project.category", "Category", required=True, index=True, copy=False,
                                  tracking=True)
    currency_id = fields.Many2one("res.currency", "Currency", required=True, copy=False, tracking=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one("res.company", "Company", required=True, index=True, copy=False, tracking=True,
                                 default=lambda self: self.env.user.company_id.id)
    auto_generated_reference = fields.Boolean("Auto Generated Reference", copy=False)
    color = fields.Integer(string="Color Index", copy=False)
    allow_planning = fields.Boolean("Planning", copy=False)
    tender_contracts_count = fields.Integer(compute="_compute_tender_contracts_count", string="Tender Contracts Count")

    def _compute_tender_contracts_count(self):
        tender_contract_obj = self.env["tender.contract"]
        for tender_project in self:
            tender_project.tender_contracts_count = tender_contract_obj.search_count(
                [("tender_project_id", "=", tender_project.id)])

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if args is None:
            args = []
        domain = args + ["|", ("name", operator, name), ("ref", operator, name)]
        return self._search(domain, limit=limit, access_rights_uid=name_get_uid)

    def write(self, vals):
        if len(vals) != 1 or (len(vals) == 1 and not ("color" in vals.keys() or "access_token" in vals.keys())):
            for tender_project in self:
                if tender_project.tender_contracts_count > 0:
                    raise UserError(_("You cannot modify project %s has already contracts") % tender_project.name)

        res = super(TenderProject, self).write(vals)
        return res

    def unlink(self):
        planning_obj = self.env["planning.slot"].sudo()
        for tender_project in self:
            if tender_project.tender_contracts_count > 0:
                raise UserError(_("You cannot delete project %s has already contracts") % tender_project.name)

            planning_count = planning_obj.search_count([("tender_project_id", "=", tender_project.id)])
            if planning_count > 0:
                raise UserError(_("You cannot delete project %s has already plannings") % tender_project.name)

        return super(TenderProject, self).unlink()

    def generate_reference(self):
        sequence_obj = self.env["ir.sequence"]
        for tender_project in self:
            if tender_project.auto_generated_reference:
                continue

            if tender_project.tender_contracts_count > 0:
                raise UserError(
                    _("You cannot generate reference for project %s has already contracts") % tender_project.name)

            tender_project.write({
                "ref": sequence_obj.next_by_code("tender.project"),
                "auto_generated_reference": True
            })
        return True

    def action_overview(self):
        action = self.sudo().env.ref("contracts_management.action_tender_projects_overview")
        result = action.read()[0]

        result["context"] = {
            "active_id": self.id,
            "active_ids": self.ids,
            "search_default_name": self.name,
        }

        return result

    def _qweb_prepare_qcontext(self, view_id, domain):
        values = super()._qweb_prepare_qcontext(view_id, domain)

        # get tender projects
        tender_projects = self.search(domain)

        # get data of template
        values.update(tender_projects._prepare_values())

        # get actions of template
        values["actions"] = tender_projects._prepare_actions()

        return values

    def _prepare_values(self):
        currency = self.env.company.currency_id

        values = {
            "projects": self,
            "currency": currency,
            "stat_buttons": self._get_stat_button()
        }

        # set total expected value,actual value and net profit of tender contracts per customer
        customers = {}
        total_expected_value = 0
        total_actual_value = 0
        tender_contract_obj = self.env["tender.contract"]
        for customer in self.mapped("partner_id"):
            tender_contracts = tender_contract_obj.search([("partner_id", "=", customer.id)])
            if tender_contracts:
                customers[customer.id] = {
                    "customer_id": customer.id,
                    "customer_name": customer.name,
                    "customer_contracts_count": len(tender_contracts),
                    "open_contracts_count": tender_contract_obj.search_count(
                        [("id", "in", tender_contracts.ids), ("state", "=", "open")]),
                    "in_progress_contracts_count": tender_contract_obj.search_count(
                        [("id", "in", tender_contracts.ids), ("state", "=", "in progress")]),
                    "closed_contracts_count": tender_contract_obj.search_count(
                        [("id", "in", tender_contracts.ids), ("state", "=", "closed")])
                }

                total_expected_value += sum(tender_contract.expected_value for tender_contract in tender_contracts)
                total_actual_value += sum(tender_contract.actual_value for tender_contract in tender_contracts)
        values.update({
            "customers": customers,
            "total_expected_value": total_expected_value,
            "total_actual_value": total_actual_value
        })
        return values

    def _get_stat_button(self):
        stat_buttons = []
        stat_buttons.append({
            "name": _("Contracts"),
            "count": sum(self.mapped("tender_contracts_count")),
            "icon": "fa fa-book",
            "action": _to_action_data("tender.contract", domain=[("tender_project_id", "in", self.ids)],
                                context={"create": False, "edit": False, "delete": False})
        })
        return stat_buttons

    def _prepare_actions(self):
        actions = []

        if len(self) == 1:
            actions.append({
                "label": _("Create New Contract"),
                "action_id": "contracts_management.open_create_tender_contract_for_project",
                "context": json.dumps({"default_tender_project_id": self.id}),
            })
        return actions

def _to_action_data(model=None, *, action=None, views=None, res_id=None, domain=None, context=None):
    # pass in either action or (model, views)
    if action:
        assert model is None and views is None
        act = {
            field: value
            for field, value in action.sudo().read()[0].items()
            if field in action._get_readable_fields()
        }
        act = clean_action(act, env=action.env)
        model = act['res_model']
        views = act['views']
    # FIXME: search-view-id, possibly help?
    descr = {
        'data-model': model,
        'data-views': json.dumps(views),
    }
    if context is not None: # otherwise copy action's?
        descr['data-context'] = json.dumps(context)
    if res_id:
        descr['data-res-id'] = res_id
    elif domain:
        descr['data-domain'] = json.dumps(domain)
    return descr
