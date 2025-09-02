#!/usr/bin/env python3
"""
Final cleanup script for problematic views in sale.order
This script connects directly to PostgreSQL and removes problematic views
"""

import psycopg2
import sys

# Database connection parameters - UPDATE THESE WITH YOUR ACTUAL VALUES
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'rajhirealestateodoo-saudalrajhirealestate-odooup18-23349594',
    'user': 'your_username',  # UPDATE THIS
    'password': 'your_password'  # UPDATE THIS
}

def connect_to_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def analyze_problematic_views(cursor):
    """Analyze current problematic views"""
    print("\n=== ANALYZING PROBLEMATIC VIEWS ===")
    
    query = """
    SELECT 
        id, 
        name, 
        model,
        LENGTH(arch_db::text) as arch_length,
        CASE 
            WHEN arch_db::text LIKE '%transferred_id%' THEN 'Contains transferred_id'
            WHEN arch_db::text LIKE '%locked%' THEN 'Contains locked'
            WHEN arch_db::text LIKE '%authorized_transaction_ids%' THEN 'Contains authorized_transaction_ids'
            WHEN arch_db::text LIKE '%subscription_state%' THEN 'Contains subscription_state'
            WHEN arch_db::text LIKE '%payment_action_capture%' THEN 'Contains payment_action_capture'
            WHEN arch_db::text LIKE '%payment_action_void%' THEN 'Contains payment_action_void'
            WHEN arch_db::text LIKE '%resume_subscription%' THEN 'Contains resume_subscription'
            ELSE 'Other issue'
        END as issue_type
    FROM ir_ui_view 
    WHERE model = 'sale.order' 
    AND (
        arch_db::text LIKE '%transferred_id%' OR
        arch_db::text LIKE '%locked%' OR
        arch_db::text LIKE '%authorized_transaction_ids%' OR
        arch_db::text LIKE '%subscription_state%' OR
        arch_db::text LIKE '%payment_action_capture%' OR
        arch_db::text LIKE '%payment_action_void%' OR
        arch_db::text LIKE '%resume_subscription%'
    )
    ORDER BY name;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"Found {len(results)} problematic views:")
        for row in results:
            print(f"  ID: {row[0]}, Name: {row[1]}, Issue: {row[4]}")
    else:
        print("No problematic views found.")
    
    return len(results)

def delete_problematic_views(cursor):
    """Delete problematic views using LIKE patterns"""
    print("\n=== DELETING PROBLEMATIC VIEWS ===")
    
    # First deletion using LIKE patterns
    delete_query1 = """
    DELETE FROM ir_ui_view 
    WHERE model = 'sale.order' 
    AND (
        arch_db::text LIKE '%transferred_id%' OR
        arch_db::text LIKE '%locked%' OR
        arch_db::text LIKE '%authorized_transaction_ids%' OR
        arch_db::text LIKE '%subscription_state%' OR
        arch_db::text LIKE '%payment_action_capture%' OR
        arch_db::text LIKE '%payment_action_void%' OR
        arch_db::text LIKE '%resume_subscription%'
    );
    """
    
    cursor.execute(delete_query1)
    deleted1 = cursor.rowcount
    print(f"Deleted {deleted1} views using LIKE patterns")
    
    # Second deletion using regex patterns for more precision
    delete_query2 = """
    DELETE FROM ir_ui_view 
    WHERE model = 'sale.order' 
    AND (
        arch_db::text ~ '.*<field[^>]*name="transferred_id".*' OR
        arch_db::text ~ '.*<field[^>]*name="locked".*' OR
        arch_db::text ~ '.*<field[^>]*name="authorized_transaction_ids".*' OR
        arch_db::text ~ '.*<field[^>]*name="subscription_state".*' OR
        arch_db::text ~ '.*<button[^>]*name="payment_action_capture".*' OR
        arch_db::text ~ '.*<button[^>]*name="payment_action_void".*' OR
        arch_db::text ~ '.*<button[^>]*name="resume_subscription".*'
    );
    """
    
    cursor.execute(delete_query2)
    deleted2 = cursor.rowcount
    print(f"Deleted {deleted2} additional views using regex patterns")
    
    return deleted1 + deleted2

def cleanup_orphaned_data(cursor):
    """Clean up orphaned view-group relations and model data"""
    print("\n=== CLEANING UP ORPHANED DATA ===")
    
    # Clean up orphaned view-group relations
    cursor.execute("""
        DELETE FROM ir_ui_view_group_rel 
        WHERE view_id NOT IN (SELECT id FROM ir_ui_view);
    """)
    orphaned_relations = cursor.rowcount
    print(f"Deleted {orphaned_relations} orphaned view-group relations")
    
    # Clean up orphaned model data
    cursor.execute("""
        DELETE FROM ir_model_data 
        WHERE model = 'ir.ui.view' 
        AND res_id NOT IN (SELECT id FROM ir_ui_view);
    """)
    orphaned_model_data = cursor.rowcount
    print(f"Deleted {orphaned_model_data} orphaned model data records")

def final_verification(cursor):
    """Final verification of remaining problematic views"""
    print("\n=== FINAL VERIFICATION ===")
    
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN arch_db::text LIKE '%transferred_id%' OR 
                            arch_db::text LIKE '%locked%' OR 
                            arch_db::text LIKE '%authorized_transaction_ids%' OR 
                            arch_db::text LIKE '%subscription_state%' OR 
                            arch_db::text LIKE '%payment_action_capture%' OR 
                            arch_db::text LIKE '%payment_action_void%' OR 
                            arch_db::text LIKE '%resume_subscription%' THEN 1 END) as remaining_problematic_views
        FROM ir_ui_view 
        WHERE model = 'sale.order';
    """)
    
    result = cursor.fetchone()
    remaining = result[0] if result else 0
    
    print(f"Remaining problematic views: {remaining}")
    return remaining

def main():
    """Main execution function"""
    print("Starting final cleanup of problematic views...")
    print("WARNING: Make sure Odoo service is stopped before running this script!")
    
    # Connect to database
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        # Analyze current state
        initial_count = analyze_problematic_views(cursor)
        
        if initial_count == 0:
            print("\nNo problematic views found. Cleanup not needed.")
            return
        
        # Delete problematic views
        total_deleted = delete_problematic_views(cursor)
        
        # Clean up orphaned data
        cleanup_orphaned_data(cursor)
        
        # Final verification
        remaining = final_verification(cursor)
        
        # Commit changes
        conn.commit()
        
        print(f"\n=== CLEANUP COMPLETED ===")
        print(f"Total views deleted: {total_deleted}")
        print(f"Remaining problematic views: {remaining}")
        
        if remaining == 0:
            print("\n✅ SUCCESS: All problematic views have been removed!")
            print("\nNext steps:")
            print("1. Start Odoo service")
            print("2. Upgrade rent_customize module")
            print("3. Verify that error messages are gone")
        else:
            print(f"\n⚠️  WARNING: {remaining} problematic views still remain")
            print("You may need to investigate these manually.")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("IMPORTANT: Update the database connection parameters in DB_CONFIG before running!")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    main()