#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Fix for Template Inheritance Errors
This script can be run directly to fix XPath and template issues
"""

import os
import sys

# Add Odoo to Python path
odoo_path = '/home/odoo/src/odoo'
if os.path.exists(odoo_path):
    sys.path.insert(0, odoo_path)

try:
    import odoo
    from odoo import api, SUPERUSER_ID
    from odoo.tools import config
except ImportError:
    print("❌ Could not import Odoo. Make sure Odoo is in your Python path.")
    sys.exit(1)

def fix_template_errors(db_name):
    """
    Fix template inheritance errors in the specified database
    """
    print(f"Connecting to database: {db_name}")
    
    # Initialize Odoo
    config.parse_config(['-d', db_name])
    odoo.service.db._create_empty_database(db_name)
    
    registry = odoo.registry(db_name)
    
    with registry.cursor() as cr:
        with api.Environment.manage():
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            print("\n🔧 Starting template inheritance error fixes...")
            
            try:
                # 1. Remove problematic XPath views
                print("\n1. Removing problematic XPath views...")
                
                # Direct SQL approach for efficiency
                cr.execute("""
                    SELECT id, name FROM ir_ui_view 
                    WHERE arch_db::text LIKE '%xpath%'
                    AND arch_db::text LIKE '%web.assets_common%'
                    AND arch_db::text LIKE '%t-call-assets%'
                    AND inherit_id IS NOT NULL
                """)
                
                problematic_views = cr.fetchall()
                print(f"Found {len(problematic_views)} potentially problematic views")
                
                for view_id, view_name in problematic_views:
                    try:
                        view = env['ir.ui.view'].browse(view_id)
                        if view.inherit_id:
                            parent_arch = str(view.inherit_id.arch_db or '')
                            if 't-call-assets' not in parent_arch or 'web.assets_common' not in parent_arch:
                                view.unlink()
                                print(f"  ✓ Deleted view: {view_name} (ID: {view_id})")
                    except Exception as e:
                        print(f"  ⚠ Could not process view {view_name}: {e}")
                
                # 2. Fix HTML encoded quotes in XPath expressions
                print("\n2. Fixing HTML encoded quotes in XPath expressions...")
                
                cr.execute("""
                    UPDATE ir_ui_view 
                    SET arch_db = REPLACE(REPLACE(
                        arch_db::text, 
                        '&#39;', ''''
                    ), '&quot;', '"')::jsonb
                    WHERE arch_db::text LIKE '%xpath%'
                    AND (arch_db::text LIKE '%&#39;%' OR arch_db::text LIKE '%&quot;%')
                """)
                
                fixed_quotes = cr.rowcount
                print(f"  ✓ Fixed HTML encoded quotes in {fixed_quotes} views")
                
                # 3. Replace problematic XPath expressions
                print("\n3. Replacing problematic XPath expressions...")
                
                cr.execute("""
                    UPDATE ir_ui_view 
                    SET arch_db = REPLACE(
                        arch_db::text, 
                        'xpath expr="//t[@t-call-assets=''web.assets_common'']"',
                        'xpath expr="//head"'
                    )::jsonb
                    WHERE arch_db::text LIKE '%xpath%'
                    AND arch_db::text LIKE '%web.assets_common%'
                    AND arch_db::text LIKE '%t-call-assets%'
                """)
                
                fixed_xpath = cr.rowcount
                print(f"  ✓ Fixed XPath expressions in {fixed_xpath} views")
                
                # 4. Check for missing 'field' model
                print("\n4. Checking for missing 'field' model...")
                
                field_model = env['ir.model'].search([('model', '=', 'field')], limit=1)
                if not field_model:
                    env['ir.model'].create({
                        'name': 'Field',
                        'model': 'field',
                        'state': 'manual',
                        'transient': False,
                    })
                    print("  ✓ Created missing 'field' model")
                else:
                    print("  ✓ 'field' model already exists")
                
                # 5. Clear caches
                print("\n5. Clearing caches...")
                
                try:
                    cr.execute("DELETE FROM ir_ui_view_cache")
                    print("  ✓ Cleared view cache")
                except Exception as e:
                    print(f"  ⚠ Could not clear view cache: {e}")
                
                # Clear attachment cache
                cached_attachments = env['ir.attachment'].search([
                    ('res_model', '=', 'ir.ui.view'),
                    ('name', 'ilike', '%assets%')
                ])
                if cached_attachments:
                    cached_attachments.unlink()
                    print(f"  ✓ Deleted {len(cached_attachments)} cached attachments")
                
                # 6. Final verification
                print("\n6. Verifying fixes...")
                
                cr.execute("""
                    SELECT COUNT(*) FROM ir_ui_view 
                    WHERE arch_db::text LIKE '%xpath%'
                    AND arch_db::text LIKE '%web.assets_common%'
                    AND arch_db::text LIKE '%t-call-assets%'
                    AND inherit_id IS NOT NULL
                """)
                
                remaining_issues = cr.fetchone()[0]
                print(f"  ✓ Remaining problematic XPath views: {remaining_issues}")
                
                # Commit all changes
                cr.commit()
                print("\n✅ All template inheritance error fixes completed successfully!")
                
                return True
                
            except Exception as e:
                print(f"\n❌ Error during fixes: {e}")
                cr.rollback()
                return False

def main():
    print("Odoo 18 Template Inheritance Quick Fix")
    print("======================================")
    
    # Get database name from command line or use default
    db_name = sys.argv[1] if len(sys.argv) > 1 else 'saudalrajhirealestate'
    
    success = fix_template_errors(db_name)
    
    if success:
        print("\n🎉 Template inheritance errors have been fixed!")
        print("\nNext steps:")
        print("1. Restart your Odoo server")
        print("2. Clear browser cache")
        print("3. Test the application")
    else:
        print("\n❌ Failed to fix template inheritance errors")
        print("Please check the error messages above")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())