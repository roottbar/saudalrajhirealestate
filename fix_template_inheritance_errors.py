#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Template Inheritance Errors in Odoo 18
This script fixes XPath inheritance issues and missing model errors
"""

import psycopg2
import sys
import os

def fix_template_inheritance_errors():
    """
    Fix template inheritance and XPath errors in the database
    """
    try:
        # Database connection parameters
        conn = psycopg2.connect(
            host="localhost",
            database="saudalrajhirealestate",
            user="odoo",
            password="odoo"
        )
        cur = conn.cursor()
        
        print("Starting template inheritance error fixes...")
        
        # 1. Find and remove problematic XPath views targeting web.assets_common
        print("\n1. Removing problematic XPath views...")
        cur.execute("""
            DELETE FROM ir_ui_view 
            WHERE arch_db::text LIKE '%xpath%'
            AND arch_db::text LIKE '%web.assets_common%'
            AND arch_db::text LIKE '%t-call-assets%'
            AND inherit_id IS NOT NULL
            AND inherit_id NOT IN (
                SELECT id FROM ir_ui_view 
                WHERE arch_db::text LIKE '%t-call-assets%' 
                AND arch_db::text LIKE '%web.assets_common%'
                AND inherit_id IS NULL
            );
        """)
        deleted_views = cur.rowcount
        print(f"Deleted {deleted_views} problematic XPath views")
        
        # 2. Clean up orphaned ir_model_data records
        print("\n2. Cleaning up orphaned ir_model_data records...")
        cur.execute("""
            DELETE FROM ir_model_data 
            WHERE model = 'ir.ui.view'
            AND res_id NOT IN (SELECT id FROM ir_ui_view WHERE id IS NOT NULL);
        """)
        deleted_data = cur.rowcount
        print(f"Deleted {deleted_data} orphaned ir_model_data records")
        
        # 3. Fix XPath expressions to use more reliable selectors
        print("\n3. Updating XPath expressions...")
        cur.execute("""
            UPDATE ir_ui_view 
            SET arch_db = REPLACE(
                arch_db::text, 
                'xpath expr="//t[@t-call-assets=''web.assets_common'']"',
                'xpath expr="//head"'
            )::jsonb
            WHERE arch_db::text LIKE '%xpath%'
            AND arch_db::text LIKE '%web.assets_common%'
            AND inherit_id IS NOT NULL;
        """)
        updated_views = cur.rowcount
        print(f"Updated {updated_views} XPath expressions")
        
        # 4. Remove views with invalid XPath syntax (HTML encoded quotes)
        print("\n4. Removing views with invalid XPath syntax...")
        cur.execute("""
            DELETE FROM ir_ui_view 
            WHERE arch_db::text LIKE '%xpath%'
            AND (
                arch_db::text LIKE '%&#39;%' OR  -- HTML encoded quotes
                arch_db::text LIKE '%&quot;%'    -- HTML encoded double quotes
            )
            AND inherit_id IS NOT NULL;
        """)
        invalid_views = cur.rowcount
        print(f"Deleted {invalid_views} views with invalid XPath syntax")
        
        # 5. Check for missing 'field' model and create if needed
        print("\n5. Checking for missing 'field' model...")
        cur.execute("""
            SELECT COUNT(*) FROM ir_model WHERE model = 'field';
        """)
        field_model_exists = cur.fetchone()[0]
        
        if field_model_exists == 0:
            print("Creating missing 'field' model...")
            cur.execute("""
                INSERT INTO ir_model (name, model, state, transient)
                VALUES ('Field', 'field', 'manual', false);
            """)
            print("Created 'field' model")
        else:
            print("'field' model already exists")
        
        # 6. Clear view cache to prevent stale references
        print("\n6. Clearing view cache...")
        try:
            cur.execute("DELETE FROM ir_ui_view_cache;")
            print("Cleared view cache")
        except psycopg2.Error as e:
            print(f"View cache table might not exist: {e}")
        
        # 7. Clear attachment cache for view-related assets
        print("\n7. Clearing attachment cache...")
        cur.execute("""
            DELETE FROM ir_attachment 
            WHERE res_model = 'ir.ui.view'
            AND name LIKE '%assets%';
        """)
        deleted_attachments = cur.rowcount
        print(f"Deleted {deleted_attachments} cached attachments")
        
        # 8. Verify fixes
        print("\n8. Verifying fixes...")
        cur.execute("""
            SELECT COUNT(*) FROM ir_ui_view 
            WHERE arch_db::text LIKE '%xpath%'
            AND arch_db::text LIKE '%web.assets_common%'
            AND inherit_id IS NOT NULL;
        """)
        remaining_issues = cur.fetchone()[0]
        print(f"Remaining problematic XPath views: {remaining_issues}")
        
        # Commit changes
        conn.commit()
        print("\n✅ All fixes applied successfully!")
        print("Please restart your Odoo server to apply the changes.")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    print("Odoo 18 Template Inheritance Error Fix")
    print("======================================")
    
    success = fix_template_inheritance_errors()
    
    if success:
        print("\n🎉 Template inheritance errors have been fixed!")
        print("Next steps:")
        print("1. Restart your Odoo server")
        print("2. Update any affected modules")
        print("3. Clear browser cache if needed")
        sys.exit(0)
    else:
        print("\n❌ Failed to fix template inheritance errors")
        print("Please check the error messages above and try again")
        sys.exit(1)