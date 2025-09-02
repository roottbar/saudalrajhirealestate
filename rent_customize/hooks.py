# -*- coding: utf-8 -*-
"""
Post-install hooks for rent_customize module
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """
    Post-installation hook to clean up problematic views
    """
    _logger.info("Running post-install hook for rent_customize")
    
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        try:
            # Find and delete problematic views that reference non-existent fields
            problematic_views = env['ir.ui.view'].search([
                ('model', '=', 'sale.order'),
                '|', '|', '|', '|', '|', '|',
                ('arch_db', 'ilike', '%transferred_id%'),
                ('arch_db', 'ilike', '%locked%'),
                ('arch_db', 'ilike', '%authorized_transaction_ids%'),
                ('arch_db', 'ilike', '%payment_action_capture%'),
                ('arch_db', 'ilike', '%payment_action_void%'),
                ('arch_db', 'ilike', '%resume_subscription%'),
                ('arch_db', 'ilike', '%subscription_state%'),
                ('name', 'not ilike', '%rent_customize%')
            ])
            
            if problematic_views:
                _logger.info(f"Found {len(problematic_views)} problematic views to clean up")
                for view in problematic_views:
                    _logger.info(f"Removing problematic view: {view.name} (ID: {view.id})")
                
                # Delete problematic views
                problematic_views.unlink()
                _logger.info("Problematic views cleaned up successfully")
            else:
                _logger.info("No problematic views found")
                
            # Clear registry cache to ensure clean state
            env.registry.clear_cache()
            _logger.info("Registry cache cleared")
            
        except Exception as e:
            _logger.error(f"Error during post-install hook: {e}")
            # Don't raise the exception to avoid blocking installation
            pass

def uninstall_hook(cr, registry):
    """
    Pre-uninstall hook
    """
    _logger.info("Running uninstall hook for rent_customize")