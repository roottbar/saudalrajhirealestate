# -*- coding: utf-8 -*-

import base64
from odoo import http, _, fields
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from collections import OrderedDict
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.app_website_base.controllers.main import Portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
import pytz



class Main(Portal):

    def _prepare_portal_layout_values(self):
        values = super(Portal, self)._prepare_portal_layout_values()
        values['attendance_transactions_count'] = request.env['attendance.transaction'].search_count([
            ('date', '=', datetime.today())
        ])
        return values
    @http.route(['/attendance/transactions', '/attendance/transactions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_attendance_transactions(self, page=1, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            # 'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            # 'type': {'label': _('Type'), 'order': 'holiday_status_id desc'},
        }

        # default sort by value
        # if not sortby:
        #     sortby = 'date'
        # order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('status', 'in', ['ex', 'ab', 'weekend','pr', 'leave', 'dep'])]},
            'ex': {'label': _('Exists'), 'domain': [('status', '=', 'ex')]},
            'ab': {'label': _('Absences'), 'domain': [('status', '=','ab')]},
            'leave': {'label': _('in Leave'), 'domain': [('status', '=', 'leave')]},
            'dep': {'label': _('In Deputation'), 'domain': [('status', '=', 'dep')]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'

        # count for pager
        attendance_transaction_count = values.get('attendance_transaction_count', 0)
        # make pager
        pager = portal_pager(
            url="//attendance/transactions",
            total=attendance_transaction_count,
            page=page,
            step=self._items_per_page
        )
        transactions = request.env['attendance.transaction']
        # domain = [('employee_id.user_id', '=', request.env.user.id)]
        domain = [ ('date', '=', datetime.today())]
        domain += searchbar_filters[filterby]['domain']
        attendance_transactions = transactions.search(
            domain,
            # order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        # request.session['my_time_off_history'] = time_off_requests.ids[:100]

        values.update({
            'attendance_transactions': attendance_transactions,
            'pager': pager,
            'page_name': 'attendance_transaction',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/attendance/transactions',
        })
        return request.render("hr_attendance_transaction.portal_attendance_transaction", values)

    @http.route(['/attendance_exception/<int:request_id>', '/attendance_exception'], type='http', auth="user", website=True)
    def portal_submit_attendance_exception_request(self, request_id=None, access_token=None, **post):
        values = super(Portal, self)._prepare_portal_layout_values()
        if post and request.httprequest.method == 'POST':
            exception = request.env['hr.attendance.exception']
            transaction = request.env['attendance.transaction'].browse(int(post.get('transaction_id')))
            try:
                with request.cr.savepoint():
                    check_out = False
                    if post.get('check_out'):
                        check_out = self.str_todate(post.get('check_out'))
                    vals = {
                        'employee_id':int(transaction.employee_id.id),
                        'department_id':int(transaction.employee_id.department_id.id),
                        'exception_reason':post.get('exception_reason'),
                        'exception_type':post.get('exception_type'),
                        'state':'submit',
                        'absence_date':post.get('absence_date') or False,
                        'check_out':check_out ,
                        'transaction_id':int(transaction.id)
                    }

                    exception_id = exception.create(vals)
                    if exception_id:
                        values.update({'exception_id':exception_id})
                        return request.render("hr_attendance_transaction.portal_submit_exception_request_details", values)
            except Exception as e:
                error = e or e.value or e.message or ""
                values.update({'error': error})
        else:
            transaction = request.env['attendance.transaction'].browse(request_id)
            values.update({'transaction_id': transaction.id})
        return request.render("hr_attendance_transaction.portal_submit_attendance_exception_request", values)



    def str_todate(self, datestring):
        datestring = str(datestring)
        datestring = datestring.replace("T", " ")
        datestring = datetime.strptime(
            datestring, "%Y-%m-%d %H:%M")
        local_tz = pytz.timezone(
            request.env.user.partner_id.tz or 'GMT')
        local_dt = local_tz.localize(datestring, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
        datestring = datetime.strptime(
            utc_dt, "%Y-%m-%d %H:%M:%S")
        datestring = fields.Datetime.to_string(datestring)
        return datestring