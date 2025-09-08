#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to clear problematic database views that reference non-existent fields
This script should be run from the Odoo shell to clean up validation errors
"""

import psycopg2
import sys

def clear_problematic_views():
    """
    Clear database views that contain references to problematic fields
    """
    try:
        # Database connection parameters - update these as needed
        conn = psycopg2.connect(
            host="localhost",
            database="rajhirealestateodoo-saudalrajhirealestate-odooup18-23508697",
            user="odoo",
            password="odoo"
        )
        
        cur = conn.cursor()
        
        # Find and delete problematic views
        problematic_fields = [
            'transferred_id',
            'payment_action_capture', 
            'payment_action_void',
            'resume_subscription'
        ]
        
        for field in problematic_fields:
            # Search for views containing these problematic references
            cur.execute("""
                SELECT id, name FROM ir_ui_view 
                WHERE model = 'sale.order' 
                AND arch_db::text LIKE %s
            """, (f'%{field}%',))
            
            problematic_views = cur.fetchall()
            
            if problematic_views:
                print(f"Found {len(problematic_views)} views with problematic field '{field}':")
                for view_id, view_name in problematic_views:
                    print(f"  - ID: {view_id}, Name: {view_name}")
                
                # Ask for confirmation before deletion
                response = input(f"Delete these views containing '{field}'? (y/N): ")
                if response.lower() == 'y':
                    for view_id, view_name in problematic_views:
                        cur.execute("DELETE FROM ir_ui_view WHERE id = %s", (view_id,))
                        print(f"Deleted view: {view_name} (ID: {view_id})")
                    conn.commit()
                    print(f"Successfully deleted {len(problematic_views)} problematic views for field '{field}'")
                else:
                    print(f"Skipped deletion for field '{field}'")
            else:
                print(f"No problematic views found for field '{field}'")
        
        # Also clear any cached view data
        cur.execute("""
            DELETE FROM ir_model_data 
            WHERE model = 'ir.ui.view' 
            AND res_id NOT IN (SELECT id FROM ir_ui_view)
        """)
        conn.commit()
        print("Cleared orphaned view references from ir_model_data")
        
        cur.close()
        conn.close()
        print("Database cleanup completed successfully!")
        
    except Exception as e:
        print(f"Error during database cleanup: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting database view cleanup...")
    success = clear_problematic_views()
    if success:
        print("\nCleanup completed. Please restart your Odoo server.")
    else:
        print("\nCleanup failed. Please check the error messages above.")
        sys.exit(1)
