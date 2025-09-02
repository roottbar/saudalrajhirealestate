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
            clean_problematic_views(env)
        except Exception as e:
            _logger.error(f"Error during post-install hook: {e}")
            # Don't raise the exception to avoid blocking installation
            pass

def clean_problematic_views(env):
    """
    تنظيف العروض المشكلة من قاعدة البيانات
    """
    _logger.info("بدء تنظيف العروض المشكلة")
    
    try:
        # حذف العروض المشكلة
        problematic_views = env['ir.ui.view'].search([
            ('model', '=', 'sale.order'),
            '|', '|', '|', '|', '|', '|', '|',
            ('arch_db', 'ilike', '%<field name="transferred_id"%'),
            ('arch_db', 'ilike', '%<field name="locked"%'),
            ('arch_db', 'ilike', '%<field name="authorized_transaction_ids"%'),
            ('arch_db', 'ilike', '%<field name="subscription_state"%'),
            ('arch_db', 'ilike', '%<button name="payment_action_capture"%'),
            ('arch_db', 'ilike', '%<button name="payment_action_void"%'),
            ('arch_db', 'ilike', '%<button name="resume_subscription"%'),
            ('arch_db', 'ilike', '%<button string="Resume" name="resume_subscription"%')
        ])
        
        if problematic_views:
            _logger.info(f"تم العثور على {len(problematic_views)} عرض مشكل للتنظيف")
            for view in problematic_views:
                _logger.info(f"جاري حذف العرض المشكل: {view.name} (ID: {view.id})")
            
            # حذف العروض المشكلة
            problematic_views.unlink()
            _logger.info("تم تنظيف العروض المشكلة بنجاح")
        else:
            _logger.info("لم يتم العثور على عروض مشكلة")
            
        # تنظيف الكاش
        env.registry.clear_cache()
        _logger.info("تم تنظيف الكاش")
        
        # تحديث الوحدة
        module = env['ir.module.module'].search([('name', '=', 'rent_customize')])
        if module:
            module.button_immediate_upgrade()
            _logger.info("تم تحديث وحدة rent_customize")
        
    except Exception as e:
        _logger.error(f"خطأ أثناء تنظيف العروض: {e}")
        raise e

def uninstall_hook(cr, registry):
    """
    Pre-uninstall hook
    """
    _logger.info("Running uninstall hook for rent_customize")
    
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        clean_problematic_views(env)
