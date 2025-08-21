from odoo import fields, api, models, _
from stdnum import iban
from odoo.exceptions import UserError, ValidationError

import logging

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    def _format_iban(self, acc_number):
        """
        This function removes all characters from given 'string' that isn't alphanumeric,
        converts it to upper case, checks checksum, and groups by 4.
        """
        res = ''
        if acc_number:
            try:
                a = iban.validate(acc_number)
            except:
                raise ValidationError(_('%s is not a valid IBAN.') % (acc_number))
            res = iban.format(a)
        return res

    @api.onchange('acc_number')
    def onchange_acc_id(self):
        if self.acc_number:
            self.acc_number = self._format_iban(self.acc_number)
