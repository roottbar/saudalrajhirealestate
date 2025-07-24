# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import api, fields, models
from io import BytesIO
import xlsxwriter
import base64


class ActivityReport(models.TransientModel):

    _name = "activity.report.wizard"
    _description = "activity report wizard"
    activity_type_ids = fields.Many2many(
        "mail.activity.type", string="Activity Type", require=True
    )
    range_type = fields.Selection(
        [("greater_than", ">"), ("less_than", "<"), ("equal_to", "=")],
        string="Range Type",
        require=True,
    )
    due_date = fields.Date(string="Due Date", require=True)
    user_ids = fields.Many2many(
        "res.users", string="User Id", require=True, domain=[("share", "=", False)]
    )

    def action_Excel(self):
        if self.range_type == "less_than":
            activity_ids = self.env["mail.activity"].search(
                [
                    ("activity_type_id", "in", self.activity_type_ids.ids),
                    ("date_deadline", "<", self.due_date),
                    ("user_id", "in", self.user_ids.ids),
                ]
            )

        elif self.range_type == "greater_than":
            activity_ids = self.env["mail.activity"].search(
                [
                    ("activity_type_id", "in", self.activity_type_ids.ids),
                    ("date_deadline", ">", self.due_date),
                    ("user_id", "in", self.user_ids.ids),
                ]
            )

        elif self.range_type == "equal_to":
            activity_ids = self.env["mail.activity"].search(
                [
                    ("activity_type_id", "in", self.activity_type_ids.ids),
                    ("date_deadline", "=", self.due_date),
                    ("user_id", "in", self.user_ids.ids),
                ]
            )

        fp = BytesIO()
        file_name = "activity.xlsx"
        workbook = xlsxwriter.Workbook(fp, {"in_memory": True})
        worksheet = workbook.add_worksheet()
        new_data = "Activity Report"
        worksheet.write(0, 0, new_data)
        cell_format = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True}
        )
        worksheet.merge_range("A1:E3", new_data, cell_format)
        cell_format.set_bg_color("#D3D3D3")

        my_list = [
            "Activity Created On",
            "Activity Type",
            "Due Date of Activity",
            "Summary",
            "Assigned To",
        ]
        cell_format1 = workbook.add_format({"bold": True})
        for col_num, data in enumerate(my_list):
            worksheet.write(4, col_num, data, cell_format1)

        cell_format2 = workbook.add_format()
        cell_format2.set_num_format("dd/mm/yy")

        row = 5
        for activity in activity_ids:
            worksheet.write(row, 0, activity.create_date, cell_format2)
            worksheet.write(row, 1, activity.activity_type_id.name)
            worksheet.write(row, 2, activity.date_deadline, cell_format2)
            worksheet.write(row, 3, activity.summary)
            worksheet.write(row, 4, activity.user_id.name)
            row += 1

        workbook.close()
        attachment_id = self.env["ir.attachment"].create(
            {
                "name": file_name,
                "type": "binary",
                "datas": base64.encodebytes(fp.getvalue()),
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s/%s/datas/%s"
                   % ("ir.attachment", attachment_id.id, file_name),
            "target": "self",
        }

    def action_Pdf(self):
        if self.range_type == "less_than":
            activity_ids = self.env["mail.activity"].search(
                [
                    ("activity_type_id", "in", self.activity_type_ids.ids),
                    ("date_deadline", "<", self.due_date),
                    ("user_id", "in", self.user_ids.ids),
                ]
            )

        elif self.range_type == "greater_than":
            activity_ids = self.env["mail.activity"].search(
                [
                    ("activity_type_id", "in", self.activity_type_ids.ids),
                    ("date_deadline", ">", self.due_date),
                    ("user_id", "in", self.user_ids.ids),
                ]
            )

        elif self.range_type == "equal_to":
            activity_ids = self.env["mail.activity"].search(
                [
                    ("activity_type_id", "in", self.activity_type_ids.ids),
                    ("date_deadline", "=", self.due_date),
                    ("user_id", "in", self.user_ids.ids),
                ]
            )

        data = {
            "activity_ids": activity_ids.ids,
        }

        return self.env.ref("cr_activity_report.action_report_activity").report_action(
            self, data=data
        )
