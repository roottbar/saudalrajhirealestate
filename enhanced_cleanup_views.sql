-- Enhanced cleanup script for problematic views in sale.order
-- This script handles nested inheritance chains by recursively deleting views

-- First, let's analyze the current problematic views and their inheritance
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

-- Show complete inheritance tree for problematic views
WITH RECURSIVE inheritance_tree AS (
    -- Base case: problematic parent views
    SELECT 
        id,
        name,
        inherit_id,
        0 as level,
        ARRAY[id] as path
    FROM ir_ui_view 
    WHERE model = 'sale.order' 
    AND inherit_id IS NULL
    AND (
        arch_db::text LIKE '%transferred_id%' OR
        arch_db::text LIKE '%locked%' OR
        arch_db::text LIKE '%authorized_transaction_ids%' OR
        arch_db::text LIKE '%subscription_state%' OR
        arch_db::text LIKE '%payment_action_capture%' OR
        arch_db::text LIKE '%payment_action_void%' OR
        arch_db::text LIKE '%resume_subscription%'
    )
    
    UNION ALL
    
    -- Recursive case: child views
    SELECT 
        child.id,
        child.name,
        child.inherit_id,
        parent.level + 1,
        parent.path || child.id
    FROM ir_ui_view child
    JOIN inheritance_tree parent ON child.inherit_id = parent.id
    WHERE child.model = 'sale.order'
)
SELECT 
    level,
    id,
    name,
    inherit_id,
    path
FROM inheritance_tree
ORDER BY level DESC, id;

-- Step 1: Delete views at deepest level first (level 3 and above)
DELETE FROM ir_ui_view 
WHERE id IN (
    WITH RECURSIVE inheritance_tree AS (
        SELECT 
            id,
            name,
            inherit_id,
            0 as level
        FROM ir_ui_view 
        WHERE model = 'sale.order' 
        AND inherit_id IS NULL
        AND (
            arch_db::text LIKE '%transferred_id%' OR
            arch_db::text LIKE '%locked%' OR
            arch_db::text LIKE '%authorized_transaction_ids%' OR
            arch_db::text LIKE '%subscription_state%' OR
            arch_db::text LIKE '%payment_action_capture%' OR
            arch_db::text LIKE '%payment_action_void%' OR
            arch_db::text LIKE '%resume_subscription%'
        )
        
        UNION ALL
        
        SELECT 
            child.id,
            child.name,
            child.inherit_id,
            parent.level + 1
        FROM ir_ui_view child
        JOIN inheritance_tree parent ON child.inherit_id = parent.id
        WHERE child.model = 'sale.order'
    )
    SELECT id FROM inheritance_tree WHERE level >= 3
);

-- Step 2: Delete views at level 2
DELETE FROM ir_ui_view 
WHERE id IN (
    WITH RECURSIVE inheritance_tree AS (
        SELECT 
            id,
            name,
            inherit_id,
            0 as level
        FROM ir_ui_view 
        WHERE model = 'sale.order' 
        AND inherit_id IS NULL
        AND (
            arch_db::text LIKE '%transferred_id%' OR
            arch_db::text LIKE '%locked%' OR
            arch_db::text LIKE '%authorized_transaction_ids%' OR
            arch_db::text LIKE '%subscription_state%' OR
            arch_db::text LIKE '%payment_action_capture%' OR
            arch_db::text LIKE '%payment_action_void%' OR
            arch_db::text LIKE '%resume_subscription%'
        )
        
        UNION ALL
        
        SELECT 
            child.id,
            child.name,
            child.inherit_id,
            parent.level + 1
        FROM ir_ui_view child
        JOIN inheritance_tree parent ON child.inherit_id = parent.id
        WHERE child.model = 'sale.order'
    )
    SELECT id FROM inheritance_tree WHERE level = 2
);

-- Step 3: Delete views at level 1
DELETE FROM ir_ui_view 
WHERE id IN (
    WITH RECURSIVE inheritance_tree AS (
        SELECT 
            id,
            name,
            inherit_id,
            0 as level
        FROM ir_ui_view 
        WHERE model = 'sale.order' 
        AND inherit_id IS NULL
        AND (
            arch_db::text LIKE '%transferred_id%' OR
            arch_db::text LIKE '%locked%' OR
            arch_db::text LIKE '%authorized_transaction_ids%' OR
            arch_db::text LIKE '%subscription_state%' OR
            arch_db::text LIKE '%payment_action_capture%' OR
            arch_db::text LIKE '%payment_action_void%' OR
            arch_db::text LIKE '%resume_subscription%'
        )
        
        UNION ALL
        
        SELECT 
            child.id,
            child.name,
            child.inherit_id,
            parent.level + 1
        FROM ir_ui_view child
        JOIN inheritance_tree parent ON child.inherit_id = parent.id
        WHERE child.model = 'sale.order'
    )
    SELECT id FROM inheritance_tree WHERE level = 1
);

-- Step 4: Delete problematic parent views (level 0)
DELETE FROM ir_ui_view 
WHERE model = 'sale.order' 
AND inherit_id IS NULL
AND (
    arch_db::text LIKE '%transferred_id%' OR
    arch_db::text LIKE '%locked%' OR
    arch_db::text LIKE '%authorized_transaction_ids%' OR
    arch_db::text LIKE '%subscription_state%' OR
    arch_db::text LIKE '%payment_action_capture%' OR
    arch_db::text LIKE '%payment_action_void%' OR
    arch_db::text LIKE '%resume_subscription%'
);

-- Step 5: Clean up any remaining problematic views using regex patterns
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

-- Step 6: Clean up orphaned view-group relations
DELETE FROM ir_ui_view_group_rel 
WHERE view_id NOT IN (SELECT id FROM ir_ui_view);

-- Step 7: Clean up orphaned model data
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
