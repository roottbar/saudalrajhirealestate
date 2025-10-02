# -*- coding: utf-8 -*-

import io
import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools.misc import xlsxwriter


class ReportExcelExport(http.Controller):

    @http.route('/base_dynamic_reports/export/xlsx', type='http', auth="user")
    def index(self, data, token):
        params = json.loads(data)
        response_data = self.export_data(params.get('columns_header'), params.get('lines'), params.get('ws_name'))

        return request.make_response(response_data,
                                     headers=[('Content-Disposition', content_disposition(params.get('filename'))),
                                              ('Content-Type', self.content_type)],
                                     cookies={'fileToken': token})

    @property
    def content_type(self):
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def export_data(self, columns_header, lines, ws_name):
        # add data in worksheet
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(ws_name)

        # styles
        header_style = workbook.add_format({'bold': True, 'font': 'Arial', 'bottom': 2})

        # level 0 style
        level0_style = workbook.add_format(
            {'bold': True, 'font': 'Arial', 'font_size': 13, 'color': '#666666', 'bottom': 6})

        # level 1 style
        level1_style = workbook.add_format(
            {'bold': True, 'font': 'Arial', 'font_size': 13, 'color': '#666666', 'bottom': 1})

        # level 2 style
        level2_style = workbook.add_format({'bold': True, 'font': 'Arial', 'font_size': 12, 'color': '#666666'})
        level2_first_style = workbook.add_format(
            {'bold': True, 'font': 'Arial', 'font_size': 12, 'color': '#666666', 'align': 'left', 'indent': 1})

        # level 3 style
        level3_style = workbook.add_format({'font': 'Arial', 'font_size': 12, 'color': '#666666'})
        level3_first_style = workbook.add_format(
            {'font': 'Arial', 'font_size': 12, 'color': '#666666', 'align': 'left', 'indent': 2})

        worksheet.set_column(0, 0, 50)

        col = 0
        row = 0
        for column_header in columns_header:
            worksheet.write(row, col, column_header, header_style)
            col += 1

        col = 0
        row += 1
        for line in lines:
            level = line['level']
            section = line['section']

            if level == 0:
                cell_format = level0_style
                cell_first_format = level0_style

                if section:
                    worksheet.write_blank(row, 0, '')
                    row += 1

            elif level == 1:
                cell_format = level1_style
                cell_first_format = level1_style
            elif level == 2:
                cell_format = level2_style
                cell_first_format = level2_first_style
            else:
                cell_format = level3_style
                cell_first_format = level3_first_style

            for line_data in line['data']:
                if col == 0:
                    worksheet.write(row, col, line_data['value'], cell_first_format)
                else:
                    worksheet.write(row, col, line_data['value'], cell_format)

                col += line_data['colspan']

            col = 0
            row += 1

        workbook.close()
        return output.getvalue()
