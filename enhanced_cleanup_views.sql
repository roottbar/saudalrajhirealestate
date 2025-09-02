-- Enhanced cleanup script for problematic views in sale.order
-- This script handles foreign key constraints by deleting child views first

-- First, let's analyze the current problematic views
SELECT 
    id, 
    name, 
    model,
    inherit_id,
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
ORDER BY inherit_id NULLS LAST, id;

-- Show inheritance relationships for problematic views
SELECT 
    child.id as child_id,
    child.name as child_name,
    parent.id as parent_id,
    parent.name as parent_name
FROM ir_ui_view child
JOIN ir_ui_view parent ON child.inherit_id = parent.id
WHERE parent.model = 'sale.order'
AND (
    parent.arch_db::text LIKE '%transferred_id%' OR
    parent.arch_db::text LIKE '%locked%' OR
    parent.arch_db::text LIKE '%authorized_transaction_ids%' OR
    parent.arch_db::text LIKE '%subscription_state%' OR
    parent.arch_db::text LIKE '%payment_action_capture%' OR
    parent.arch_db::text LIKE '%payment_action_void%' OR
    parent.arch_db::text LIKE '%resume_subscription%'
)
ORDER BY parent_id, child_id;

-- Step 1: Delete child views that inherit from problematic views
DELETE FROM ir_ui_view 
WHERE inherit_id IN (
    SELECT id FROM ir_ui_view 
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
);

-- Step 2: Delete problematic parent views using LIKE patterns
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

-- Step 3: Alternative deletion using regex patterns for any remaining views
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

-- Step 4: Clean up orphaned view-group relations
DELETE FROM ir_ui_view_group_rel 
WHERE view_id NOT IN (SELECT id FROM ir_ui_view);

-- Step 5: Clean up orphaned model data
DELETE FROM ir_model_data 
WHERE model = 'ir.ui.view' 
AND res_id NOT IN (SELECT id FROM ir_ui_view);

-- Final verification - count remaining problematic views
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

-- Show completion message
SELECT 'ENHANCED CLEANUP COMPLETED - Please restart Odoo service and upgrade rent_customize module' as next_steps;
