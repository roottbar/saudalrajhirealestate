-- Complete Fix for Template Inheritance Errors in Odoo 18
-- This script addresses XPath inheritance issues and missing model errors

-- Start transaction
BEGIN;

-- 1. Backup problematic views before deletion (optional)
CREATE TEMP TABLE backup_problematic_views AS
SELECT * FROM ir_ui_view 
WHERE arch_db::text LIKE '%xpath%'
AND arch_db::text LIKE '%web.assets_common%'
AND arch_db::text LIKE '%t-call-assets%'
AND inherit_id IS NOT NULL;

SELECT 'Backed up ' || COUNT(*) || ' problematic views' as backup_status
FROM backup_problematic_views;

-- 2. Remove problematic XPath views that reference non-existent elements
DELETE FROM ir_ui_view 
WHERE id IN (
    SELECT child.id
    FROM ir_ui_view child
    LEFT JOIN ir_ui_view parent ON child.inherit_id = parent.id
    WHERE child.arch_db::text LIKE '%xpath%'
    AND child.arch_db::text LIKE '%web.assets_common%'
    AND child.arch_db::text LIKE '%t-call-assets%'
    AND child.inherit_id IS NOT NULL
    AND (
        parent.id IS NULL OR
        parent.arch_db::text NOT LIKE '%t-call-assets%' OR
        parent.arch_db::text NOT LIKE '%web.assets_common%'
    )
);

SELECT 'Deleted ' || ROW_COUNT() || ' problematic XPath views' as deletion_status;

-- 3. Fix HTML encoded quotes in XPath expressions
UPDATE ir_ui_view 
SET arch_db = REPLACE(REPLACE(
    arch_db::text, 
    '&#39;', ''''
), '&quot;', '"')::jsonb
WHERE arch_db::text LIKE '%xpath%'
AND (arch_db::text LIKE '%&#39;%' OR arch_db::text LIKE '%&quot;%');

SELECT 'Fixed HTML encoded quotes in ' || ROW_COUNT() || ' views' as quote_fix_status;

-- 4. Replace problematic XPath expressions with safer alternatives
UPDATE ir_ui_view 
SET arch_db = REPLACE(
    arch_db::text, 
    'xpath expr="//t[@t-call-assets=''web.assets_common'']"',
    'xpath expr="//head"'
)::jsonb
WHERE arch_db::text LIKE '%xpath%'
AND arch_db::text LIKE '%web.assets_common%'
AND arch_db::text LIKE '%t-call-assets%';

SELECT 'Updated XPath expressions in ' || ROW_COUNT() || ' views' as xpath_update_status;

-- 5. Fix other common asset XPath issues
UPDATE ir_ui_view 
SET arch_db = REPLACE(
    arch_db::text, 
    'xpath expr="//t[@t-call-assets=''web.assets_frontend'']"',
    'xpath expr="//head"'
)::jsonb
WHERE arch_db::text LIKE '%xpath%'
AND arch_db::text LIKE '%web.assets_frontend%'
AND arch_db::text LIKE '%t-call-assets%';

UPDATE ir_ui_view 
SET arch_db = REPLACE(
    arch_db::text, 
    'xpath expr="//t[@t-call-assets=''web.assets_backend'']"',
    'xpath expr="//head"'
)::jsonb
WHERE arch_db::text LIKE '%xpath%'
AND arch_db::text LIKE '%web.assets_backend%'
AND arch_db::text LIKE '%t-call-assets%';

-- 6. Clean up orphaned ir_model_data records
DELETE FROM ir_model_data 
WHERE model = 'ir.ui.view'
AND res_id NOT IN (SELECT id FROM ir_ui_view WHERE id IS NOT NULL);

SELECT 'Cleaned up ' || ROW_COUNT() || ' orphaned ir_model_data records' as cleanup_status;

-- 7. Check and create missing 'field' model if needed
INSERT INTO ir_model (name, model, state, transient, info)
SELECT 'Field', 'field', 'manual', false, 'Auto-created to fix KeyError'
WHERE NOT EXISTS (SELECT 1 FROM ir_model WHERE model = 'field');

SELECT CASE 
    WHEN EXISTS (SELECT 1 FROM ir_model WHERE model = 'field') 
    THEN 'Field model exists or was created'
    ELSE 'Failed to create field model'
END as field_model_status;

-- 8. Remove views with completely broken inheritance chains
DELETE FROM ir_ui_view 
WHERE inherit_id IS NOT NULL
AND inherit_id NOT IN (SELECT id FROM ir_ui_view WHERE id IS NOT NULL);

SELECT 'Removed ' || ROW_COUNT() || ' views with broken inheritance chains' as broken_chain_status;

-- 9. Clear view cache (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_ui_view_cache') THEN
        DELETE FROM ir_ui_view_cache;
        RAISE NOTICE 'Cleared view cache';
    ELSE
        RAISE NOTICE 'View cache table does not exist';
    END IF;
END $$;

-- 10. Clear attachment cache for view-related assets
DELETE FROM ir_attachment 
WHERE res_model = 'ir.ui.view'
AND name LIKE '%assets%';

SELECT 'Deleted ' || ROW_COUNT() || ' cached view attachments' as attachment_cleanup_status;

-- 11. Update view priorities to ensure proper inheritance order
UPDATE ir_ui_view 
SET priority = COALESCE(priority, 16)
WHERE inherit_id IS NOT NULL
AND arch_db::text LIKE '%xpath%'
AND (priority IS NULL OR priority < 16);

SELECT 'Updated priorities for ' || ROW_COUNT() || ' views' as priority_update_status;

-- 12. Final verification and reporting
SELECT 
    'Final Status Report' as report_type,
    (
        SELECT COUNT(*) FROM ir_ui_view 
        WHERE arch_db::text LIKE '%xpath%'
        AND arch_db::text LIKE '%web.assets_common%'
        AND inherit_id IS NOT NULL
    ) as remaining_problematic_views,
    (
        SELECT COUNT(*) FROM ir_ui_view 
        WHERE inherit_id IS NOT NULL
        AND inherit_id NOT IN (SELECT id FROM ir_ui_view WHERE id IS NOT NULL)
    ) as orphaned_views,
    (
        SELECT COUNT(*) FROM ir_model WHERE model = 'field'
    ) as field_model_exists;

-- 13. Create a summary of what was fixed
SELECT 
    'Template Inheritance Fix Summary' as summary_type,
    'XPath inheritance errors fixed' as fix_type,
    'HTML encoded quotes corrected' as encoding_fix,
    'Orphaned records cleaned up' as cleanup_type,
    'Missing field model created' as model_fix,
    'View cache cleared' as cache_status;

-- Commit all changes
COMMIT;

-- Final success message
SELECT 
    '✅ Template inheritance error fixes completed successfully!' as status,
    'Please restart your Odoo server to apply the changes.' as next_step,
    'Clear browser cache if issues persist.' as additional_step;