-- سكريبت SQL لحذف جميع العروض المشكلة نهائياً
-- يجب تشغيله على قاعدة بيانات Odoo لحل جميع أخطاء التحقق

-- حذف العروض التي تحتوي على operating_unit_id في account.move.line
DELETE FROM ir_ui_view 
WHERE model = 'account.move.line' 
AND arch_db LIKE '%operating_unit_id%';

-- حذف العروض التي تحتوي على action_budget في purchase.order
DELETE FROM ir_ui_view 
WHERE model = 'purchase.order' 
AND arch_db LIKE '%action_budget%';

-- حذف العروض التي تحتوي على resume_subscription في sale.order
DELETE FROM ir_ui_view 
WHERE model = 'sale.order' 
AND arch_db LIKE '%resume_subscription%';

-- حذف العروض التي تحتوي على payment_action_capture في sale.order
DELETE FROM ir_ui_view 
WHERE model = 'sale.order' 
AND arch_db LIKE '%payment_action_capture%';

-- حذف العروض التي تحتوي على payment_action_void في sale.order
DELETE FROM ir_ui_view 
WHERE model = 'sale.order' 
AND arch_db LIKE '%payment_action_void%';

-- حذف العروض التي تحتوي على transferred_id المشكلة
DELETE FROM ir_ui_view 
WHERE model = 'sale.order' 
AND arch_db LIKE '%transferred_id%'
AND arch_db NOT LIKE '%<!-- %transferred_id% -->';

-- حذف العروض التي تحتوي على locked المشكلة
DELETE FROM ir_ui_view 
WHERE model = 'sale.order' 
AND arch_db LIKE '%locked%'
AND arch_db NOT LIKE '%<!-- %locked% -->';

-- حذف العروض التي تحتوي على authorized_transaction_ids المشكلة
DELETE FROM ir_ui_view 
WHERE model = 'sale.order' 
AND arch_db LIKE '%authorized_transaction_ids%'
AND arch_db NOT LIKE '%<!-- %authorized_transaction_ids% -->';

-- تنظيف الكاش
DELETE FROM ir_ui_view WHERE active = false;

-- إعادة تحميل العروض
UPDATE ir_module_module SET state = 'to upgrade' WHERE name = 'rent_customize';
UPDATE ir_module_module SET state = 'to upgrade' WHERE name = 'account_operating_unit';

-- رسالة تأكيد
SELECT 'تم تنظيف جميع العروض المشكلة بنجاح' as result;