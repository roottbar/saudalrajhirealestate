#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced cleanup script for problematic views in Odoo
This script uses multiple search patterns and regex to find problematic views
"""

import psycopg2
import sys
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def enhanced_cleanup_problematic_views():
    """
    Enhanced database cleanup of problematic views using multiple search patterns
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
        
        # First, let's examine what we have
        logger.info("Analyzing existing views...")
        analysis_query = """
        SELECT 
            id, 
            name,
            LENGTH(arch_db) as arch_length,
            CASE 
                WHEN arch_db LIKE '%transferred_id%' THEN 'Contains transferred_id'
                WHEN arch_db LIKE '%locked%' THEN 'Contains locked'
                WHEN arch_db LIKE '%authorized_transaction_ids%' THEN 'Contains authorized_transaction_ids'
                WHEN arch_db LIKE '%payment_action_capture%' THEN 'Contains payment_action_capture'
                WHEN arch_db LIKE '%payment_action_void%' THEN 'Contains payment_action_void'
                WHEN arch_db LIKE '%resume_subscription%' THEN 'Contains resume_subscription'
                ELSE 'Clean'
            END as issue_type
        FROM ir_ui_view 
        WHERE model = 'sale.order'
        AND (
            arch_db LIKE '%transferred_id%' OR
            arch_db LIKE '%locked%' OR
            arch_db LIKE '%authorized_transaction_ids%' OR
            arch_db LIKE '%payment_action_capture%' OR
            arch_db LIKE '%payment_action_void%' OR
            arch_db LIKE '%resume_subscription%'
        )
        ORDER BY name
        """
        
        cursor.execute(analysis_query)
        problematic_candidates = cursor.fetchall()
        
        if problematic_candidates:
            logger.info(f"Found {len(problematic_candidates)} potentially problematic views")
            for view_id, view_name, arch_length, issue_type in problematic_candidates:
                logger.info(f"  - {view_name} (ID: {view_id}): {issue_type}")
        else:
            logger.info("No obviously problematic views found with basic search")
        
        # Now let's get all sale.order views and check them with Python regex
        logger.info("Performing detailed analysis with regex...")
        all_views_query = """
        SELECT id, name, arch_db 
        FROM ir_ui_view 
        WHERE model = 'sale.order'
        """
        
        cursor.execute(all_views_query)
        all_views = cursor.fetchall()
        
        # Define problematic patterns
        problematic_patterns = [
            r'<field[^>]*name=["\']transferred_id["\'][^>]*>',
            r'<field[^>]*name=["\']locked["\'][^>]*>',
            r'<field[^>]*name=["\']authorized_transaction_ids["\'][^>]*>',
            r'<field[^>]*name=["\']subscription_state["\'][^>]*>',
            r'<button[^>]*name=["\']payment_action_capture["\'][^>]*>',
            r'<button[^>]*name=["\']payment_action_void["\'][^>]*>',
            r'<button[^>]*name=["\']resume_subscription["\'][^>]*>',
            # Additional patterns
            r'transferred_id',
            r'authorized_transaction_ids',
            r'payment_action_capture',
            r'payment_action_void',
            r'resume_subscription'
        ]
        
        views_to_delete = []
        
        for view_id, view_name, arch_db in all_views:
            if arch_db:  # Make sure arch_db is not None
                for pattern in problematic_patterns:
                    if re.search(pattern, arch_db, re.IGNORECASE):
                        views_to_delete.append((view_id, view_name, pattern))
                        logger.info(f"Found problematic view: {view_name} (ID: {view_id}) - matches pattern: {pattern}")
                        break  # No need to check other patterns for this view
        
        if views_to_delete:
            logger.info(f"Found {len(views_to_delete)} problematic views to delete")
            
            # Delete the problematic views
            for view_id, view_name, pattern in views_to_delete:
                logger.info(f"Deleting view: {view_name} (ID: {view_id})")
                delete_query = "DELETE FROM ir_ui_view WHERE id = %s"
                cursor.execute(delete_query, (view_id,))
            
            # Commit the changes
            conn.commit()
            logger.info("Successfully deleted all problematic views")
            
            # Clean up orphaned relations
            cleanup_queries = [
                "DELETE FROM ir_ui_view_group_rel WHERE view_id NOT IN (SELECT id FROM ir_ui_view)",
                "DELETE FROM ir_model_data WHERE model = 'ir.ui.view' AND res_id NOT IN (SELECT id FROM ir_ui_view)"
            ]
            
            for cleanup_query in cleanup_queries:
                try:
                    cursor.execute(cleanup_query)
                    logger.info(f"Executed cleanup: {cleanup_query[:50]}...")
                except Exception as e:
                    logger.warning(f"Cleanup warning: {e}")
            
            conn.commit()
            logger.info("Cleanup completed")
            
        else:
            logger.info("No problematic views found with detailed analysis")
        
        # Final verification
        cursor.execute("""
        SELECT 
            COUNT(*) as total_sale_order_views,
            COUNT(CASE WHEN arch_db LIKE '%transferred_id%' OR 
                            arch_db LIKE '%locked%' OR 
                            arch_db LIKE '%authorized_transaction_ids%' OR 
                            arch_db LIKE '%payment_action_capture%' OR 
                            arch_db LIKE '%payment_action_void%' OR 
                            arch_db LIKE '%resume_subscription%' 
                       THEN 1 END) as remaining_problematic_views
        FROM ir_ui_view 
        WHERE model = 'sale.order'
        """)
        
        total_views, remaining_problematic = cursor.fetchone()
        logger.info(f"Final status: {total_views} total sale.order views, {remaining_problematic} potentially problematic views remaining")
        
        cursor.close()
        conn.close()
        logger.info("Database connection closed")
        
        print("\n=== ENHANCED CLEANUP COMPLETED ===")
        print(f"Deleted {len(views_to_delete) if views_to_delete else 0} problematic views")
        print(f"Remaining sale.order views: {total_views}")
        print(f"Potentially problematic views remaining: {remaining_problematic}")
        print("Please restart your Odoo service now to apply changes.")
        print("Then upgrade the rent_customize module.")
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=== Enhanced Odoo Problematic Views Cleanup ===")
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
            enhanced_cleanup_problematic_views()
        else:
            print("Please complete the preparation steps first.")
    else:
        print("Operation cancelled.")