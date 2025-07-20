from odoo import models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _login(self, db, login, password)
        user_id = super(ResUsers, self)._login(db, login, password)
        if user_id
            self.env['user.log'].create_log(
                user_id=user_id,
                model='res.users',
                record_id=user_id,
                action='login',
                ip_address=self.env.request.httprequest.remote_addr if hasattr(self.env, 'request') and self.env.request else None
            )
        return user_id

    def _check_credentials(self, password)
        try
            super(ResUsers, self)._check_credentials(password)
        except Exception as e
            # Log failed login attempts if neededs
            raise e

    def _invalidate_session_cache(self)
        if self.env.user and hasattr(self.env, 'request')
            self.env['user.log'].create_log(
                user_id=self.env.user.id,
                model='res.users',
                record_id=self.env.user.id,
                action='logout',
                ip_address=self.env.request.httprequest.remote_addr if hasattr(self.env, 'request') and self.env.request else None
            )
        return super(ResUsers, self)._invalidate_session_cache()
