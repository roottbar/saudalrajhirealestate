# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    select_tender_project = fields.Boolean("Select Project")
    contracts_before_tender_projects_menu = fields.Boolean("Contracts Before Projects Menu")
    tender_contract_customer_account_category_id = fields.Many2one("res.partner.account.category",
                                                                   "Customer Accounting Category",
                                                                   domain=[("apply_to_tender_contract", "=", True)])
    tender_contract_journal_id = fields.Many2one("account.journal", string="Journal")
    auto_sequence_customer = fields.Boolean(string='Auto Sequence for Customer')
    group_show_tender_project = fields.Boolean(string="Show Project",
                                               implied_group="contracts_management.group_show_tender_project")

    def sequence_contracts_tender_projects_menus(self):
        tender_projects_menu = self.env.ref("contracts_management.menu_tender_projects")
        contracts_menu = self.env.ref("contracts_management.menu_tender_contracts")

        if (self.contracts_before_tender_projects_menu and tender_projects_menu.sequence < contracts_menu.sequence) or (
                not self.contracts_before_tender_projects_menu and tender_projects_menu.sequence > contracts_menu.sequence):
            sequence_contracts_menu = contracts_menu.sequence
            contracts_menu.sequence = tender_projects_menu.sequence
            tender_projects_menu.sequence = sequence_contracts_menu

    @api.onchange("group_show_tender_project")
    def onchange_group_show_tender_project(self):
        if not self.group_show_tender_project:
            self.select_tender_project = False
            self.contracts_before_tender_projects_menu = False

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()

        # get old value of order contracts and tender projects menus

        config_parameters.set_param("contracts_management.select_tender_project", self.select_tender_project)
        config_parameters.set_param("contracts_management.contracts_before_tender_projects_menu",
                                    self.contracts_before_tender_projects_menu)
        config_parameters.set_param("contracts_management.tender_contract_customer_account_category_id",
                                    self.tender_contract_customer_account_category_id.id)
        config_parameters.set_param("contracts_management.tender_contract_journal_id",
                                    self.tender_contract_journal_id.id)
        config_parameters.set_param("contracts_management.auto_sequence_customer", self.auto_sequence_customer)

        self.sequence_contracts_tender_projects_menus()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        config_parameters = self.env["ir.config_parameter"].sudo()

        tender_contract_customer_account_category_id = config_parameters.get_param(
            "contracts_management.tender_contract_customer_account_category_id", False)

        tender_contract_journal_id = config_parameters.get_param("contracts_management.tender_contract_journal_id",
                                                                 False)
        res.update(
            tender_contract_customer_account_category_id=tender_contract_customer_account_category_id and eval(
                tender_contract_customer_account_category_id) or False,
            tender_contract_journal_id=tender_contract_journal_id and eval(tender_contract_journal_id) or False,
            auto_sequence_customer=config_parameters.get_param("contracts_management.auto_sequence_customer"),
            select_tender_project=config_parameters.get_param("contracts_management.select_tender_project"),
            contracts_before_tender_projects_menu=config_parameters.get_param(
                "contracts_management.contracts_before_tender_projects_menu"),
        )
        return res
