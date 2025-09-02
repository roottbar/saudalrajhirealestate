#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct cleanup script for problematic views in Odoo
This script directly connects to the database and removes problematic views
"""

import psycopg2
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_problematic_views():
    """
    Direct database cleanup of problematic views
    """
    try:
        # Database connection parameters - UPDATE THESE WITH YOUR ACTUAL VALUES
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'your_database_name',  # Replace with actual database name
            'user': 'odoo',  # Replace with actual username
            'password': 'your_password'  # Replace with actual password
        }
        
        logger.info("Connecting to database...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Find problematic views
        query = """
        SELECT id, name, arch_db 
        FROM ir_ui_view 
        WHERE model = 'sale.order' 
        AND (
            arch_db ILIKE '%<field name="transferred_id"%' OR
            arch_db ILIKE '%<field name="locked"%' OR
            arch_db ILIKE '%<field name="authorized_transaction_ids"%' OR
            arch_db ILIKE '%<field name="subscription_state"%' OR
            arch_db ILIKE '%<button name="payment_action_capture"%' OR
            arch_db ILIKE '%<button name="payment_action_void"%' OR
            arch_db ILIKE '%<button name="resume_subscription"%' OR
            arch_db ILIKE '%<button string="Resume" name="resume_subscription"%'
        )
        """
        
        cursor.execute(query)
        problematic_views = cursor.fetchall()
        
        if problematic_views:
            logger.info(f"Found {len(problematic_views)} problematic views to delete")
            
            for view_id, view_name, arch_db in problematic_views:
                logger.info(f"Deleting view: {view_name} (ID: {view_id})")
                
                # Delete the view
                delete_query = "DELETE FROM ir_ui_view WHERE id = %s"
                cursor.execute(delete_query, (view_id,))
            
            # Commit the changes
            conn.commit()
            logger.info("Successfully deleted all problematic views")
            
            # Clear cache tables
            cache_queries = [
                "DELETE FROM ir_ui_view_group_rel WHERE view_id NOT IN (SELECT id FROM ir_ui_view)",
                "DELETE FROM ir_model_data WHERE model = 'ir.ui.view' AND res_id NOT IN (SELECT id FROM ir_ui_view)"
            ]
            
            for cache_query in cache_queries:
                try:
                    cursor.execute(cache_query)
                    logger.info(f"Executed cache cleanup: {cache_query[:50]}...")
                except Exception as e:
                    logger.warning(f"Cache cleanup warning: {e}")
            
            conn.commit()
            logger.info("Cache cleanup completed")
            
        else:
            logger.info("No problematic views found")
        
        cursor.close()
        conn.close()
        logger.info("Database connection closed")
        
        print("\n=== CLEANUP COMPLETED ===")
        print("Please restart your Odoo service now to apply changes.")
        print("Then upgrade the rent_customize module.")
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=== Odoo Problematic Views Cleanup ===")
    print("WARNING: This script will directly modify your database.")
    print("Make sure to backup your database before running this script.")
    print("")
    
    # Ask for confirmation
    confirm = input("Do you want to continue? (yes/no): ").lower().strip()
    if confirm in ['yes', 'y']:
        print("\nBefore running this script:")
        print("1. Update the database connection parameters in the script")
        print("2. Make sure Odoo service is stopped")
        print("3. Backup your database")
        print("")
        
        final_confirm = input("Have you completed the above steps? (yes/no): ").lower().strip()
        if final_confirm in ['yes', 'y']:
            cleanup_problematic_views()
        else:
            print("Please complete the preparation steps first.")
    else:
        print("Operation cancelled.")