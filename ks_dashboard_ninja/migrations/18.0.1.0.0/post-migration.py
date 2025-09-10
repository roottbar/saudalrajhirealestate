# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Remove orphaned restrict_user_ids field from ir_ui_menu table
    and verify spreadsheet revision cleanup
    """
    # Check if the restrict_user_ids column exists in ir_ui_menu table
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'ir_ui_menu' AND column_name = 'restrict_user_ids'
    """)
    
    if cr.fetchone():
        try:
            # Drop the orphaned column
            cr.execute("ALTER TABLE ir_ui_menu DROP COLUMN IF EXISTS restrict_user_ids")
            print("Successfully removed orphaned restrict_user_ids column from ir_ui_menu table")
        except Exception as e:
            print(f"Error removing restrict_user_ids column: {e}")
    else:
        print("Field 'restrict_user_ids' not found in ir_ui_menu table")
    
    # Verify spreadsheet revision cleanup
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'spreadsheet_revision'
        )
    """)
    
    if cr.fetchone()[0]:
        # Check for any remaining invalid res_model values
        cr.execute("""
            SELECT COUNT(*) FROM spreadsheet_revision 
            WHERE res_model = 'field' OR res_model NOT IN (
                SELECT model FROM ir_model WHERE model IS NOT NULL
            )
        """)
        
        invalid_count = cr.fetchone()[0]
        if invalid_count > 0:
            print(f"Warning: Found {invalid_count} spreadsheet revision records with invalid res_model after cleanup")
        else:
            print("Spreadsheet revision records cleanup verified successfully")