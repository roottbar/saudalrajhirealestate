# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """
    Post-installation hook to fix template inheritance errors
    """
    _logger.info("Starting template inheritance error fixes...")
    
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        try:
            # 1. Find and remove problematic XPath views
            _logger.info("Removing problematic XPath views...")
            problematic_views = env['ir.ui.view'].search([
                ('arch_db', 'ilike', '%xpath%'),
                ('arch_db', 'ilike', '%web.assets_common%'),
                ('arch_db', 'ilike', '%t-call-assets%'),
                ('inherit_id', '!=', False)
            ])
            
            views_to_delete = []
            for view in problematic_views:
                if view.inherit_id:
                    parent_arch = view.inherit_id.arch_db or ''
                    # Check if parent contains the target element
                    if 't-call-assets' not in parent_arch or 'web.assets_common' not in parent_arch:
                        views_to_delete.append(view.id)
            
            if views_to_delete:
                env['ir.ui.view'].browse(views_to_delete).unlink()
                _logger.info(f"Deleted {len(views_to_delete)} problematic XPath views")
            
            # 2. Fix XPath expressions with HTML encoded quotes
            _logger.info("Fixing XPath expressions with encoded quotes...")
            encoded_views = env['ir.ui.view'].search([
                ('arch_db', 'ilike', '%xpath%'),
                '|',
                ('arch_db', 'ilike', '%&#39;%'),  # HTML encoded single quotes
                ('arch_db', 'ilike', '%&quot;%')   # HTML encoded double quotes
            ])
            
            for view in encoded_views:
                try:
                    arch_str = str(view.arch_db)
                    # Replace HTML encoded quotes
                    arch_str = arch_str.replace('&#39;', "'")
                    arch_str = arch_str.replace('&quot;', '"')
                    
                    # Fix common problematic XPath expressions
                    if 'web.assets_common' in arch_str and 't-call-assets' in arch_str:
                        arch_str = arch_str.replace(
                            'xpath expr="//t[@t-call-assets=\'web.assets_common\']"',
                            'xpath expr="//head"'
                        )
                        arch_str = arch_str.replace(
                            'xpath expr="//t[@t-call-assets=\"web.assets_common\"]"',
                            'xpath expr="//head"'
                        )
                    
                    view.write({'arch_db': arch_str})
                    _logger.info(f"Fixed XPath expression in view {view.name} (ID: {view.id})")
                except Exception as e:
                    _logger.warning(f"Could not fix view {view.name} (ID: {view.id}): {e}")
            
            # 3. Check and create missing 'field' model if needed
            _logger.info("Checking for missing 'field' model...")
            field_model = env['ir.model'].search([('model', '=', 'field')], limit=1)
            if not field_model:
                _logger.info("Creating missing 'field' model...")
                env['ir.model'].create({
                    'name': 'Field',
                    'model': 'field',
                    'state': 'manual',
                    'transient': False,
                })
                _logger.info("Created 'field' model")
            
            # 4. Clear view cache
            _logger.info("Clearing view cache...")
            try:
                env.cr.execute("DELETE FROM ir_ui_view_cache")
                _logger.info("Cleared view cache")
            except Exception as e:
                _logger.warning(f"Could not clear view cache: {e}")
            
            # 5. Clear attachment cache for view-related assets
            _logger.info("Clearing attachment cache...")
            cached_attachments = env['ir.attachment'].search([
                ('res_model', '=', 'ir.ui.view'),
                ('name', 'ilike', '%assets%')
            ])
            if cached_attachments:
                cached_attachments.unlink()
                _logger.info(f"Deleted {len(cached_attachments)} cached attachments")
            
            # 6. Verify fixes
            _logger.info("Verifying fixes...")
            remaining_issues = env['ir.ui.view'].search_count([
                ('arch_db', 'ilike', '%xpath%'),
                ('arch_db', 'ilike', '%web.assets_common%'),
                ('arch_db', 'ilike', '%t-call-assets%'),
                ('inherit_id', '!=', False)
            ])
            _logger.info(f"Remaining problematic XPath views: {remaining_issues}")
            
            # Commit changes
            env.cr.commit()
            _logger.info("✅ Template inheritance error fixes completed successfully!")
            
        except Exception as e:
            _logger.error(f"❌ Error during template inheritance fixes: {e}")
            env.cr.rollback()
            raise