# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)

        # create view custom dashboard user
        action = self.sudo().env.ref('board.open_board_my_dash_action')
        view_id = action['views'][0][0]
        res.create_user_dashboard(view_id)

        return res

    @api.model
    def user_dashboard_creation(self):
        action = self.sudo().env.ref('board.open_board_my_dash_action')
        view_id = action['views'][0][0]
        user_ids = self.env['ir.ui.view.custom'].search([]).filtered(lambda board: board.ref_id.id == view_id).mapped(
            'user_id.id')

        for user in self.search([('id', 'not in', user_ids)]):
            user.create_user_dashboard(view_id)

    @api.model
    def cron_recreate_dashboard(self):
        action = self.sudo().env.ref('board.open_board_my_dash_action')
        view_id = action['views'][0][0]
        board_ids = self.env['ir.ui.view.custom'].search([]).filtered(lambda board: board.ref_id.id == view_id)
        board_ids.unlink()

        for user in self.search([]):
            user.create_user_dashboard(view_id)

    def create_user_dashboard(self, view_id):
        lang_code = self.lang or 'en_US'
        action_dashboard = self.sudo().env.ref('petty_cash.action_petty_cash_dashboard_kanban')
        action_petty_for_review = self.sudo().env.ref('petty_cash.action_petty_cash_for_review')
        action_requests_feeding = self.sudo().env.ref('petty_cash.action_petty_cash_request_feeding')
        action_petty_cash_requests = self.sudo().env.ref('petty_cash.action_petty_cash_request')

        arch = self.custom_dashboard_user() % (
            self.id, action_dashboard.id, lang_code, action_dashboard.id, _('Dashboard'),
            self.id, action_petty_for_review.id, lang_code, action_petty_for_review.id, _('Petty Cash For Review'),
            self.id, action_requests_feeding.id, lang_code, action_requests_feeding.id, _('Requests Feeding'),
            self.id, action_petty_cash_requests.id, lang_code, action_petty_cash_requests.id, _('Requests'),
        )

        self.env['ir.ui.view.custom'].sudo().create({
            'user_id': self.id,
            'ref_id': view_id,
            'arch': arch
        })

    def custom_dashboard_user(self):
        return """
        <form string="Petty Cash Dashboard">
            <board style="1">
                <column>
                    <action context="{'group_by': [], 'uid': %s, 'dashboard_merge_domains_contexts': False, 'tz': False, 'params': {'action': %s}, 'lang': '%s'}" domain="" name="%s" string="%s" view_mode="kanban" modifiers="{}" id="action_0_0"></action>
                    <action context="{'group_by': [], 'uid': %s, 'dashboard_merge_domains_contexts': False, 'tz': False, 'params': {'action': %s}, 'lang': '%s'}" domain="" name="%s" string="%s" view_mode="list" modifiers="{}" id="action_0_1"></action>
                    <action context="{'group_by': [], 'uid': %s, 'dashboard_merge_domains_contexts': False, 'tz': False, 'params': {'action': %s}, 'lang': '%s'}" domain="" name="%s" string="%s" view_mode="list" modifiers="{}" id="action_0_2"></action>
                    <action context="{'group_by': [], 'uid': %s, 'dashboard_merge_domains_contexts': False, 'tz': False, 'params': {'action': %s}, 'lang': '%s'}" domain="" name="%s" string="%s" view_mode="list" modifiers="{}" id="action_0_3"></action>
                </column>
                <column></column>
                <column></column>
            </board>
        </form>
        """
