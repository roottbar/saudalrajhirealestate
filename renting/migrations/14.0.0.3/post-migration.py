import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, Version):
    _logger.info("//////////////////////////////////////////")
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        sale_order_ids = env['sale.order'].search([('is_rental_order', '=', True)])
        _logger.info("-----------sale_order_ids-------------" + str(sale_order_ids))
        # _logger.info("-----------sale_order_ids-------------")
        for s in sale_order_ids:
          # for line in s.order_line.filtered(lambda line: line.property_number == False):

          _logger.info("-----------property_number-------------before-----" + str(s.no_of_invoiced))
          s.compute_no_invoiced()
          _logger.info("-----------property_number-------------after-----" + str(s.no_of_invoiced))
