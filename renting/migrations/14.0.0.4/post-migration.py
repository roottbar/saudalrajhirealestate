import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, Version):
    _logger.info("//////////////////////////////////////////")
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        account_asset_obj = env['account.move'].search([])
        account_move_ids = account_asset_obj.filtered(lambda o: o.asset_id and o.asset_id.property_address_area and not o.operating_unit_id)
        _logger.info("-----------count of account_move_ids-------------" + str(len(account_move_ids)))
        _logger.info("-----------account_move_ids-------------" + str(account_move_ids))
        for move in account_move_ids:
          _logger.info("-----------property_number-------------before-----" + str(move.operating_unit_id))
          move.operating_unit_id = move.asset_id.property_address_area.id
          _logger.info("-----------property_number-------------after-----" + str(move.operating_unit_id))
