# -*- coding: utf-8 -*-
"""
Pre-init hooks for odoo17_compatibility_fix module
"""

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def pre_init_hook(cr):
    """
    Pre-installation hook to handle duplicate column issues
    """
    _logger.info("Running pre-init hook for odoo17_compatibility_fix")
    
    try:
        # Check if parent_line_id column exists in sale_order_line
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sale_order_line' 
            AND column_name='parent_line_id'
        """)
        
        if cr.fetchone():
            _logger.info("Column parent_line_id already exists in sale_order_line, skipping creation")
            
            # Temporarily disable the pre_init hook in sale_subscription module
            cr.execute("""
                UPDATE ir_module_module 
                SET state = 'installed' 
                WHERE name = 'sale_subscription' 
                AND state IN ('to upgrade', 'to install')
            """)
            
            _logger.info("Temporarily disabled sale_subscription pre_init to avoid duplicate column error")
        else:
            _logger.info("Column parent_line_id does not exist, allowing normal installation")
            
    except Exception as e:
        _logger.error(f"Error during pre-init hook: {e}")
        # Don't raise the exception to avoid blocking installation
        pass