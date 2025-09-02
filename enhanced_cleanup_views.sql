-- Enhanced SQL cleanup for problematic views in sale.order model
-- This script uses multiple search patterns to find problematic views
-- WARNING: Make sure to backup your database before running this script

-- First, let's examine the actual content of views to understand the structure
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
ORDER BY name;

-- Show a sample of the problematic content
SELECT 
    id,
    name,
    SUBSTRING(arch_db FROM POSITION('transferred_id' IN arch_db) - 50 FOR 200) as sample_content
FROM ir_ui_view 
WHERE model = 'sale.order'
AND arch_db LIKE '%transferred_id%'
LIMIT 5;

-- Delete views with broader search patterns
DELETE FROM ir_ui_view 
WHERE model = 'sale.order' 
AND (
    -- Search for field references
    arch_db LIKE '%transferred_id%' OR
    arch_db LIKE '%"locked"%' OR
    arch_db LIKE '%authorized_transaction_ids%' OR
    arch_db LIKE '%subscription_state%' OR
    -- Search for button references
    arch_db LIKE '%payment_action_capture%' OR
    arch_db LIKE '%payment_action_void%' OR
    arch_db LIKE '%resume_subscription%' OR
    -- Search for specific patterns
    arch_db LIKE '%name="transferred_id"%' OR
    arch_db LIKE '%name="locked"%' OR
    arch_db LIKE '%name="authorized_transaction_ids"%' OR
    arch_db LIKE '%name="payment_action_capture"%' OR
    arch_db LIKE '%name="payment_action_void"%' OR
    arch_db LIKE '%name="resume_subscription"%'
);

-- Alternative approach: Delete specific views by name if they contain problematic content
DELETE FROM ir_ui_view 
WHERE model = 'sale.order'
AND name IN (
    SELECT name 
    FROM ir_ui_view 
    WHERE model = 'sale.order'
    AND (
        arch_db ~ '.*transferred_id.*' OR
        arch_db ~ '.*locked.*' OR
        arch_db ~ '.*authorized_transaction_ids.*' OR
        arch_db ~ '.*payment_action_capture.*' OR
        arch_db ~ '.*payment_action_void.*' OR
        arch_db ~ '.*resume_subscription.*'
    )
);

-- Clean up orphaned relations
DELETE FROM ir_ui_view_group_rel 
WHERE view_id NOT IN (SELECT id FROM ir_ui_view);

-- Clean up orphaned model data
DELETE FROM ir_model_data 
WHERE model = 'ir.ui.view' 
AND res_id NOT IN (SELECT id FROM ir_ui_view);

-- Final verification - show remaining views count
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
WHERE model = 'sale.order';

-- Show completion message
SELECT 'ENHANCED CLEANUP COMPLETED - Please restart Odoo service and upgrade rent_customize module' as next_steps;