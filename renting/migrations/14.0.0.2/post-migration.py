import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, Version):
    _logger.info("//////////////////////////////////////////")
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        sale_order_ids = env['sale.order'].search([('order_line.property_number', '=', False)])
        _logger.info("-----------sale_order_ids-------------" + str(sale_order_ids))
        # _logger.info("-----------sale_order_ids-------------")
        for s in sale_order_ids:
          # for line in s.order_line.filtered(lambda line: line.property_number == False):
          for line in s.order_line:
              _logger.info("-----------property_number-------------before-----" + str(line.product_id.name) + '------' + str(line.property_number))
              line.property_number = line.product_id.product_tmpl_id.property_id.id
              _logger.info("-----------property_number-------------after-----" + str(line.product_id.name) + '------' + str(line.property_number))
