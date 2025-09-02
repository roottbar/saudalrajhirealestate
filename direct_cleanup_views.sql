-- Direct SQL cleanup for problematic views in sale.order model
-- Run this script directly in your PostgreSQL database
-- WARNING: Make sure to backup your database before running this script

-- Show problematic views before deletion
SELECT 
    id, 
    name, 
    'Will be deleted' as status
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
);

-- Delete problematic views
DELETE FROM ir_ui_view 
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
);

-- Clean up orphaned view group relations
DELETE FROM ir_ui_view_group_rel 
WHERE view_id NOT IN (SELECT id FROM ir_ui_view);

-- Clean up orphaned model data
DELETE FROM ir_model_data 
WHERE model = 'ir.ui.view' 
AND res_id NOT IN (SELECT id FROM ir_ui_view);

-- Show remaining views for sale.order model
SELECT 
    id, 
    name, 
    'Remaining' as status
FROM ir_ui_view 
WHERE model = 'sale.order'
ORDER BY name;

-- Instructions for next steps
SELECT 'CLEANUP COMPLETED - Please restart Odoo service and upgrade rent_customize module' as next_steps;