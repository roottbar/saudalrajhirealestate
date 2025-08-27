# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import hashlib
import json
import odoo
from odoo import api, models
from odoo.addons.web.controllers.main import HomeStaticTemplateHelpers
from odoo.http import request
from odoo.tools import ustr


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super().session_info()
        if request.session.uid:
            user = request.env.user
            # expose the active branch id while preserving Odoo 18's default payload
            res['branch_id'] = user.branch_id.id if getattr(user, 'branch_id', False) else None
        return res
        version_info = odoo.service.common.exp_version()

        user_context = request.session.get_context() if request.session.uid else {}


        IrConfigSudo = self.env['ir.config_parameter'].sudo()
        max_file_upload_size = int(IrConfigSudo.get_param(
            'web.max_file_upload_size',
            default=128 * 1024 * 1024,  # 128MiB
        ))
        mods = odoo.conf.server_wide_modules or []
        if request.db:
            mods = list(request.registry._init_modules) + mods
        lang = user_context.get("lang")
        translation_hash = request.env['ir.translation'].sudo().get_web_translations_hash(mods, lang)

        session_info = {
            "uid": request.session.uid,
            "is_system": user._is_system() if request.session.uid else False,
            "is_admin": user._is_admin() if request.session.uid else False,
            "user_context": request.session.get_context() if request.session.uid else {},
            "db": request.session.db,
            "server_version": version_info.get('server_version'),
            "server_version_info": version_info.get('server_version_info'),
            "name": user.name,
            "username": user.login,
            "partner_display_name": user.partner_id.display_name,
            "company_id": user.company_id.id if request.session.uid else None,
            # YTI TODO: Remove this from the user context
            "branch_id": user.branch_id.id if request.session.uid else None,
            "partner_id": user.partner_id.id if request.session.uid and user.partner_id else None,
            "web.base.url": self.env['ir.config_parameter'].sudo().get_param('web.base.url', default=''),
            "cache_hashes": {
                "translations": translation_hash,
            },
        }
        if self.env.user.has_group('base.group_user'):
            # the following is only useful in the context of a webclient bootstrapping
            # but is still included in some other calls (e.g. '/web/session/authenticate')
            # to avoid access errors and unnecessary information, it is only included for users
            # with access to the backend ('internal'-type users)
            qweb_checksum = HomeStaticTemplateHelpers.get_qweb_templates_checksum(debug=request.session.debug, bundle="web.assets_qweb")
            menus = request.env['ir.ui.menu'].load_menus(request.session.debug)
            ordered_menus = {str(k): v for k, v in menus.items()}
            menu_json_utf8 = json.dumps(ordered_menus, default=ustr, sort_keys=True).encode()
            session_info['cache_hashes'].update({
                "load_menus": hashlib.sha512(menu_json_utf8).hexdigest()[:64], # sha512/256
                "qweb": qweb_checksum,
            })
            session_info.update({
                # current_company should be default_company
                "user_companies": {
                    'current_company': user.company_id.id,
                    'allowed_companies': {
                        comp.id: {
                            'id': comp.id,
                            'name': comp.name,
                            'sequence': comp.sequence,
                        } for comp in user.company_ids
                    },
                },
                "show_effect": True,
                "display_switch_company_menu": user.has_group('base.group_multi_company') and len(user.company_ids) > 1,
            })
        return session_info

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
