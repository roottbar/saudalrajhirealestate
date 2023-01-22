from odoo import models, fields


class PurchaseRequestRejectWizard(models.TransientModel):
    _name = 'purchase.request.reject.wizard'
    _description = 'Purchase Request Reject Wizard'

    reject_reason = fields.Text("Reason", required=True)

    def action_reject(self):
        purchase_request = self.env["purchase.request"].browse(self._context["active_id"])

        if purchase_request.state != "to_approve":
            return

        vals = {"state": "rejected"}
        if self.reject_reason:
            notes = ""
            if purchase_request.notes:
                notes = purchase_request.notes + "\n"
            notes += self.reject_reason

            vals.update({"notes": notes})

        purchase_request.write(vals)

        return True
