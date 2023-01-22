import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, Version):
    _logger.info("//////////////////////////////////////////")
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        obj = env['sale.order.line'].search([('order_id.is_rental_order', '=', True)])
        sale_order_line_ids = obj.filtered(lambda o: o.order_id.fromdate < o.order_id.todate)
        _logger.info("-----------count of sale_order_line_ids-------------" + str(len(sale_order_line_ids)))
        _logger.info("-----------sale_order_line_ids-------------" + str(sale_order_line_ids))
        for rec in sale_order_line_ids:
          rec.pickup_date = rec.order_id.fromdate
          rec.return_date = rec.order_id.todate
          _logger.info("-----------pickup_date----return_date---------after--update---" + str(rec.pickup_date) +'------'+ str(rec.return_date))
