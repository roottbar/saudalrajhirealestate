#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to clear problematic views from Odoo database
This removes cached views that reference non-existent fields
"""

import psycopg2
import sys
import os

def clear_problematic_views():
    """
    Clear views that reference fields not yet registered in sale.order model
    """
    try:
        # Database connection parameters - adjust as needed
        conn = psycopg2.connect(
            host="localhost",
            database="odoo18",
            user="odoo",
            password="odoo"
        )
        
        cur = conn.cursor()
        
        print("Clearing problematic views...")
        
        # Find problematic views
        cur.execute("""
            SELECT id, name, model, arch_db 
            FROM ir_ui_view 
            WHERE model = 'sale.order' 
            AND (
                arch_db LIKE '%transferred_id%' 
                OR arch_db LIKE '%locked%' 
                OR arch_db LIKE '%authorized_transaction_ids%'
                OR arch_db LIKE '%payment_action_capture%'
                OR arch_db LIKE '%payment_action_void%'
                OR arch_db LIKE '%resume_subscription%'
                OR arch_db LIKE '%subscription_state%'
            )
            AND name NOT LIKE '%rent_customize%'
        """)
        
        problematic_views = cur.fetchall()
        
        if problematic_views:
            print(f"Found {len(problematic_views)} problematic views:")
            for view in problematic_views:
                print(f"  - ID: {view[0]}, Name: {view[1]}")
            
            # Delete problematic views
            cur.execute("""
                DELETE FROM ir_ui_view 
                WHERE model = 'sale.order' 
                AND (
                    arch_db LIKE '%transferred_id%' 
                    OR arch_db LIKE '%locked%' 
                    OR arch_db LIKE '%authorized_transaction_ids%'
                    OR arch_db LIKE '%payment_action_capture%'
                    OR arch_db LIKE '%payment_action_void%'
                    OR arch_db LIKE '%resume_subscription%'
                    OR arch_db LIKE '%subscription_state%'
                )
                AND name NOT LIKE '%rent_customize%'
            """)
            
            print(f"Deleted {cur.rowcount} problematic views")
            
            # Clean up orphaned view group relations
            cur.execute("""
                DELETE FROM ir_ui_view_group_rel 
                WHERE view_id NOT IN (SELECT id FROM ir_ui_view)
            """)
            
            print(f"Cleaned up {cur.rowcount} orphaned view relations")
            
        else:
            print("No problematic views found")
        
        # Commit changes
        conn.commit()
        print("Database cleanup completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    success = clear_problematic_views()
    sys.exit(0 if success else 1)