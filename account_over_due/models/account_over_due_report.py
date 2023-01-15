# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, html2plaintext
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools.translate import _


class AccountOverDuepReport(models.AbstractModel):
    _name = "account.over.due.report"
    _description = "Account Over Due Report"
    _inherit = 'account.report'

    filter_partner_id = False

    # It doesn't make sense to allow multicompany for these kind of reports
    # 1. Followup mails need to have the right headers from the right company
    # 2. Separation of business seems natural: a customer wouldn't know or care that the two companies are related
    filter_multi_company = None

    def _get_columns_name(self, options):
        """
        Override
        Return the name of the columns of the follow-ups report
        """
        headers = [{},
                   {'name': _('Date'), 'class': 'date', 'style': 'text-align:left; white-space:nowrap; border: 1px solid black'},
                   {'name': _('Description'), 'class': 'date', 'style': 'text-align:left; white-space:nowrap; border: 1px solid black'},
                   {'name': _('Total'), 'style': 'text-align:left; white-space:nowrap; border: 1px solid black'},
                   {'name': _('Payment'), 'style': 'text-align:left; white-space:nowrap; border: 1px solid black'},
                   {'name': _('Balance'), 'class': 'number o_price_total',
                    'style': 'text-align:left; white-space:nowrap; border: 1px solid black'}
                   ]
        if self.env.context.get('print_mode'):
            headers = headers[:7]  # Remove the 'Expected Date' and 'Excluded' columns
        return headers

    def _get_lines(self, options, line_id=None):
        """
        Override
        Compute and return the lines of the columns of the follow-ups report.
        """
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []

        lang_code = partner.lang if self._context.get('print_mode') else self.env.user.lang or get_lang(self.env).code
        lines = []
        res = {}
        today = fields.Date.today()
        line_num = 0
        for l in partner.unreconciled_aml_ids.filtered(lambda l: l.company_id == self.env.company):
            if l.company_id == self.env.company:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            balance = 0
            for aml in aml_recs:
                amount = aml.amount_residual_currency if aml.currency_id else aml.amount_residual
                date_due = format_date(self.env, aml.date_maturity or aml.date, lang_code=lang_code)
                total += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date',
                                'style': 'white-space:nowrap;text-align:center;color: red;'}
                if is_payment:
                    date_due = ''
                line_num += 1
                move = aml.move_id
                total_amount = move.amount_total
                balance += total_amount

                columns = [
                    date_due ,
                    move.ref or move.name,
                    formatLang(self.env, total_amount, currency_obj=currency),
                    False,
                    formatLang(self.env, balance, currency_obj=currency),
                ]
                if self.env.context.get('print_mode'):
                    columns = columns[:7]
                lines.append({
                    'id': aml.id,
                    'account_move': aml.move_id,
                    'name': aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'class': 'total font-weight-normal',
                    'style': 'font-size: 10px;border: 1px solid black',
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'columns': [type(v) == dict and v or {'name': v} for v in columns],
                })

                for payment in move._get_reconciled_info_JSON_values():
                    balance -= payment["amount"]
                    columns = [
                        payment["date"].strftime("%x"),
                        payment["ref"],
                        False,
                        formatLang(self.env, payment["amount"], currency_obj=currency),
                        formatLang(self.env, balance, currency_obj=currency),
                    ]

                    if self.env.context.get('print_mode'):
                        columns = columns[:7]

                    lines.append({
                        'id': payment["payment_id"],
                        'account_move': payment["move_id"],
                        'name': payment["ref"],
                        'caret_options': 'followup',
                        'class': 'total font-weight-normal',
                        'style': 'font-size: 10px;border: 1px solid black',
                        'move_id': payment["move_id"],
                        'type': is_payment and 'payment' or 'unreconciled_aml',
                        'unfoldable': False,
                        'columns': [type(v) == dict and v or {'name': v} for v in columns],
                    })

            total_due = formatLang(self.env, total, currency_obj=currency)
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total font-weight-normal',
                'unfoldable': False,
                'style': 'color:black;font-size: 14px;border: none',
                'level': 3,
                'columns': [{'name': v} for v in [''] * (3 if self.env.context.get('print_mode') else 3) + [
                    total >= 0 and _('Total Due') or '', total_due]],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued, currency_obj=currency)
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total font-weight-normal',
                    'unfoldable': False,
                    'style': 'color:black;font-size: 14px;border: none',
                    'level': 3,
                    'columns': [{'name': v} for v in
                                [''] * (3 if self.env.context.get('print_mode') else 3) + [_('Total Overdue'),
                                                                                           total_issued]],
                })
            # Add an empty line after the total to make a space between two currencies
        return lines

    @api.model
    def _get_sms_summary(self, options):
        partner = self.env['res.partner'].browse(options.get('partner_id'))
        level = partner.followup_level
        options = dict(options, followup_level=(level.id, level.delay))
        return self._build_followup_summary_with_field('sms_description', options)

    @api.model
    def _get_default_summary(self, options):
        return self._build_followup_summary_with_field('description', options)

    @api.model
    def _build_followup_summary_with_field(self, field, options):
        """
        Build the followup summary based on the relevent followup line.
        :param field: followup line field used as the summary "template"
        :param options: dict that should contain the followup level and the partner
        :return: the summary if a followup line exists or None
        """
        followup_line = self.get_followup_line(options)
        if followup_line:
            partner = self.env['res.partner'].browse(options['partner_id'])
            lang = partner.lang or get_lang(self.env).code
            summary = followup_line.with_context(lang=lang)[field]
            try:
                summary = summary % {'partner_name': partner.name,
                                     'date': format_date(self.env, fields.Date.today(), lang_code=partner.lang),
                                     'user_signature': html2plaintext(self.env.user.signature or ''),
                                     'company_name': self.env.company.name,
                                     'amount_due': formatLang(self.env, partner.total_due,
                                                              currency_obj=partner.currency_id),
                                     }
            except ValueError as exception:
                message = _(
                    "An error has occurred while formatting your followup letter/email. (Lang: %s, Followup Level: #%s) \n\nFull error description: %s") \
                          % (lang, followup_line.id, exception)
                raise ValueError(message)
            return summary
        raise UserError(_('You need a least one follow-up level in order to process your follow-up'))

    def _get_report_manager(self, options):
        """
        Override
        Compute and return the report manager for the partner_id in options
        """
        domain = [('report_name', '=', 'account.followup.report'), ('partner_id', '=', options.get('partner_id')),
                  ('company_id', '=', self.env.company.id)]
        existing_manager = self.env['account.report.manager'].search(domain, limit=1)
        if existing_manager and not options.get('keep_summary'):
            existing_manager.write({'summary': self._get_default_summary(options)})
        if not existing_manager:
            existing_manager = self.env['account.report.manager'].create({
                'report_name': 'account.followup.report',
                'company_id': self.env.company.id,
                'partner_id': options.get('partner_id'),
                'summary': self._get_default_summary(options)})
        return existing_manager

    def get_html(self, options, line_id=None, additional_context=None):
        """
        Override
        Compute and return the content in HTML of the followup for the partner_id in options
        """
        if additional_context is None:
            additional_context = {}
            additional_context['followup_line'] = self.get_followup_line(options)
        partner = self.env['res.partner'].browse(options['partner_id'])
        additional_context['partner'] = partner
        additional_context['lang'] = partner.lang or get_lang(self.env).code
        additional_context['invoice_address_id'] = self.env['res.partner'].browse(
            partner.address_get(['invoice'])['invoice'])
        additional_context['today'] = fields.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
        return super(AccountOverDuepReport, self).get_html(options, line_id=line_id,
                                                           additional_context=additional_context)

    def _get_report_name(self):
        """
        Override
        Return the name of the report
        """
        return _('Statement')

    def _get_reports_buttons(self):
        """
        Override
        Return an empty list because this report doesn't contain any buttons
        """
        return []

    def _get_templates(self):
        """
        Override
        Return the templates of the report
        """
        templates = super(AccountOverDuepReport, self)._get_templates()
        templates['main_template'] = 'account_over_due.template_over_due_report'
        templates['line_template'] = 'account_over_due.line_template'
        return templates

    @api.model
    def get_followup_informations(self, partner_id, options):
        """
        Return all informations needed by the view:
        - the report manager id
        - the content in HTML of the report
        - the state of the next_action
        """
        options['partner_id'] = partner_id
        partner = self.env['res.partner'].browse(partner_id)
        followup_line = partner.followup_level
        report_manager_id = self._get_report_manager(options).id
        html = self.get_html(options)
        next_action = False
        if not options.get('keep_summary'):
            next_action = partner.get_next_action(followup_line)
        infos = {
            'report_manager_id': report_manager_id,
            'html': html,
            'next_action': next_action,
        }
        if partner.followup_level:
            infos['followup_level'] = self._get_line_info(followup_line)
            options['followup_level'] = (partner.followup_level.id, partner.followup_level.delay)
        return infos

    @api.model
    def send_sms(self, options):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'name': _("Send SMS Text Message"),
            'res_model': 'sms.composer',
            'target': 'new',
            'views': [(False, "form")],
            'context': {
                'default_body': self._get_sms_summary(options),
                'default_res_model': 'res.partner',
                'default_res_id': options.get('partner_id'),
                'default_composition_mode': 'comment',
            },
        }

    def _replace_class(self):
        # OVERRIDE: When added to the chatter by mail, don't loose the table-responsive set on the followup report table.
        res = super()._replace_class()
        if self._context.get('mail'):
            res.pop(b'table-responsive', None)
        return res

    @api.model
    def send_email(self, options):
        """
        Send by mail the followup to the customer
        """
        partner = self.env['res.partner'].browse(options.get('partner_id'))
        non_blocked_amls = partner.unreconciled_aml_ids.filtered(lambda aml: not aml.blocked)
        if not non_blocked_amls:
            return True
        non_printed_invoices = partner.unpaid_invoices.filtered(lambda inv: not inv.message_main_attachment_id)
        if non_printed_invoices and partner.followup_level.join_invoices:
            raise UserError(
                _('You are trying to send a followup report to a partner for which you didn\'t print all the invoices ({})').format(
                    " ".join(non_printed_invoices.mapped('name'))))
        invoice_partner = self.env['res.partner'].browse(partner.address_get(['invoice'])['invoice'])
        email = invoice_partner.email
        options['keep_summary'] = True
        if email and email.strip():
            # When printing we need te replace the \n of the summary by <br /> tags
            body_html = self.with_context(print_mode=True, mail=True, lang=partner.lang or self.env.user.lang).get_html(
                options)
            body_html = body_html.replace(b'o_account_reports_edit_summary_pencil',
                                          b'o_account_reports_edit_summary_pencil d-none')
            start_index = body_html.find(b'<span>', body_html.find(b'<div class="o_account_reports_summary">'))
            end_index = start_index > -1 and body_html.find(b'</span>', start_index) or -1
            if end_index > -1:
                replaced_msg = body_html[start_index:end_index].replace(b'\n', b'')
                body_html = body_html[:start_index] + replaced_msg + body_html[end_index:]
            partner.with_context(mail_post_autofollow=True).message_post(
                partner_ids=[invoice_partner.id],
                body=body_html,
                subject=_('%(company)s Payment Reminder - %(customer)s', company=self.env.company.name,
                          customer=partner.name),
                subtype_id=self.env.ref('mail.mt_note').id,
                model_description=_('payment reminder'),
                email_layout_xmlid='mail.mail_notification_light',
                attachment_ids=partner.followup_level.join_invoices and partner.unpaid_invoices.message_main_attachment_id.ids or [],
            )
            return True
        raise UserError(_('Could not send mail to partner %s because it does not have any email address defined',
                          partner.display_name))

    @api.model
    def print_followups(self, records):
        """
        Print one or more followups in one PDF
        records contains either a list of records (come from an server.action) or a field 'ids' which contains a list of one id (come from JS)
        """
        res_ids = records['ids'] if 'ids' in records else records.ids  # records come from either JS or server.action
        action = self.env.ref('account_over_due.action_report_over_due').report_action(res_ids)
        if action.get('type') == 'ir.actions.report':
            for partner in self.env['res.partner'].browse(res_ids):
                partner.message_post(body=_('Over Due letter printed'))
        return action

    def _get_line_info(self, followup_line):
        return {
            'id': followup_line.id,
            'name': followup_line.name,
            'print_letter': followup_line.print_letter,
            'send_email': followup_line.send_email,
            'send_sms': followup_line.send_sms,
            'manual_action': followup_line.manual_action,
            'manual_action_note': followup_line.manual_action_note
        }

    @api.model
    def get_followup_line(self, options):

        if not options.get('followup_level'):
            partner = self.env['res.partner'].browse(options.get('partner_id'))
            options['followup_level'] = (partner.followup_level.id, partner.followup_level.delay)

        if options.get('followup_level'):
            followup_line = self.env['account_followup.followup.line'].browse(options['followup_level'][0])
            return followup_line
        return False

    @api.model
    def do_manual_action(self, options):
        msg = _('Manual action done')
        partner = self.env['res.partner'].browse(options.get('partner_id'))
        if options.get('followup_level'):
            followup_line = self.env['account_followup.followup.line'].browse(options.get('followup_level'))
            if followup_line:
                msg += '<br>' + followup_line.manual_action_note
        partner.message_post(body=msg)

    def _get_aged_partner_info(self, partner):
        data = {}
        date = fields.Date.context_today(self)
        params = {
            "account_type": "receivable",
            "partner_id": partner.id
        }

        def minus_days(date_obj, days):
            return fields.Date.to_string(date_obj - relativedelta(days=days))

        # base sql
        sql = """SELECT SUM(aml.amount_residual) AS total
                 FROM account_move_line as aml JOIN account_account as acc ON acc.id = aml.account_id
                 where aml.partner_id = %(partner_id)s AND acc.internal_type = %(account_type)s"""

        # current
        params.update({"date_from": fields.Date.to_string(date)})
        extra_sql = """ AND aml.date_maturity >=  %(date_from)s"""
        self.env.cr.execute(sql + extra_sql, params)
        result = self.env.cr.fetchall()
        data.update({"current": result[0][0] or 0.0})

        # from 1 to 31
        params.update({"date_from": minus_days(date, 30), "date_to": minus_days(date, 1)})
        extra_sql = """ AND aml.date_maturity >= %(date_from)s AND aml.date_maturity <= %(date_to)s"""
        self.env.cr.execute(sql + extra_sql, params)
        result = self.env.cr.fetchall()
        data.update({"from1to30": result[0][0] or 0.0})

        # from 31 to 60
        params.update({"date_from": minus_days(date, 60), "date_to": minus_days(date, 31)})
        extra_sql = """ AND aml.date_maturity >= %(date_from)s AND aml.date_maturity <= %(date_to)s"""
        self.env.cr.execute(sql + extra_sql, params)
        result = self.env.cr.fetchall()
        data.update({"from31to60": result[0][0] or 0.0})

        # from 61 to 90
        params.update({"date_from": minus_days(date, 90), "date_to": minus_days(date, 61)})
        extra_sql = """ AND aml.date_maturity >= %(date_from)s AND aml.date_maturity <= %(date_to)s"""
        self.env.cr.execute(sql + extra_sql, params)
        result = self.env.cr.fetchall()
        data.update({"from61to90": result[0][0] or 0.0})

        # from 91 to 121
        params.update({"date_from": minus_days(date, 120), "date_to": minus_days(date, 91)})
        extra_sql = """ AND aml.date_maturity >= %(date_from)s AND aml.date_maturity <= %(date_to)s"""
        self.env.cr.execute(sql + extra_sql, params)
        result = self.env.cr.fetchall()
        data.update({"from91to121": result[0][0] or 0.0})

        # older
        params.update({"date_to": minus_days(date, 121)})
        extra_sql = """ AND aml.date_maturity <= %(date_to)s"""
        self.env.cr.execute(sql + extra_sql, params)
        result = self.env.cr.fetchall()
        data.update({"older": result[0][0] or 0.0})
        return data
