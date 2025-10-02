from odoo import models
from .audit_log_mixin import AuditLogMixin

class ResPartner(models.Model, AuditLogMixin):
    _inherit = 'res.partner'