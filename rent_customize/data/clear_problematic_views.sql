-- SQL script to clear problematic views from database
-- This removes cached views that reference non-existent fields

-- Delete problematic views that reference transferred_id, locked, authorized_transaction_ids
DELETE FROM ir_ui_view 
WHERE model = 'sale.order' 
AND (
    arch_db LIKE '%transferred_id%' 
    OR arch_db LIKE '%locked%' 
    OR arch_db LIKE '%authorized_transaction_ids%'
    OR arch_db LIKE '%payment_action_capture%'
    OR arch_db LIKE '%payment_action_void%'
    OR arch_db LIKE '%resume_subscription%'
    OR arch_db LIKE '%subscription_state%'
)
AND name NOT LIKE '%rent_customize%';

-- Clear view cache
DELETE FROM ir_ui_view_group_rel WHERE view_id NOT IN (SELECT id FROM ir_ui_view);

-- Update module state to force reload
UPDATE ir_module_module SET state = 'to upgrade' WHERE name = 'rent_customize';