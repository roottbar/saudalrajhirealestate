from . import account_move
from . import account_asset
# NOTE (Odoo 18): Base model 'account.analytic.report' no longer exists.
# This customization inherits that model and breaks registry load.
# Temporarily disabled to unblock deployment; rework needed against 'account.report'.
# from . import account_analytic_report
