# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Fix corrupted spreadsheet.revision records with invalid res_model values
    """
    # Check if spreadsheet_revision table exists
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'spreadsheet_revision'
        )
    """)
    
    if cr.fetchone()[0]:
        # Find and fix records with invalid res_model values
        cr.execute("""
            SELECT id, res_model FROM spreadsheet_revision 
            WHERE res_model = 'field' OR res_model NOT IN (
                SELECT model FROM ir_model WHERE model IS NOT NULL
            )
        """)
        
        invalid_records = cr.fetchall()
        
        if invalid_records:
            print(f"Found {len(invalid_records)} spreadsheet revision records with invalid res_model")
            
            # Delete records with invalid res_model to prevent KeyError
            cr.execute("""
                DELETE FROM spreadsheet_revision 
                WHERE res_model = 'field' OR res_model NOT IN (
                    SELECT model FROM ir_model WHERE model IS NOT NULL
                )
            """)
            
            print(f"Cleaned up {len(invalid_records)} invalid spreadsheet revision records")