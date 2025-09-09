-- حل مشكلة transferred_id في Odoo
-- Fix for transferred_id issue in Odoo
-- يجب تشغيل هذا الملف باستخدام: psql -d rajhirealestateodoo -f fix_transferred_id.sql
-- Run this file using: psql -d rajhirealestateodoo -f fix_transferred_id.sql

\echo 'بدء حل مشكلة transferred_id...'
\echo 'Starting transferred_id fix...'

-- إضافة الحقول المطلوبة إلى جدول sale_order
-- Add required fields to sale_order table

\echo 'إضافة حقل transferred_id...'
\echo 'Adding transferred_id field...'
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS transferred_id INTEGER;

\echo 'إضافة حقل locked...'
\echo 'Adding locked field...'
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS locked BOOLEAN DEFAULT FALSE;

\echo 'إضافة حقل subscription_state...'
\echo 'Adding subscription_state field...'
ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS subscription_state VARCHAR(20) DEFAULT '1_draft';

-- إنشاء جدول العلاقة many2many للمعاملات المصرح بها
-- Create many2many relation table for authorized transactions
\echo 'إنشاء جدول العلاقة للمعاملات المصرح بها...'
\echo 'Creating authorized transactions relation table...'
CREATE TABLE IF NOT EXISTS sale_order_payment_transaction_rel (
    sale_order_id INTEGER REFERENCES sale_order(id) ON DELETE CASCADE,
    payment_transaction_id INTEGER,
    PRIMARY KEY (sale_order_id, payment_transaction_id)
);

-- إضافة الحقول إلى ir_model_fields للتعرف عليها في Odoo
-- Add fields to ir_model_fields for Odoo recognition

\echo 'تسجيل الحقول في نظام Odoo...'
\echo 'Registering fields in Odoo system...'

-- تسجيل حقل transferred_id
-- Register transferred_id field
INSERT INTO ir_model_fields (name, model, field_description, ttype, state, model_id, create_date, write_date, create_uid, write_uid)
SELECT 'transferred_id', 'sale.order', 'Transferred Order', 'many2one', 'manual', 
       (SELECT id FROM ir_model WHERE model = 'sale.order'),
       NOW(), NOW(), 1, 1
WHERE NOT EXISTS (
    SELECT 1 FROM ir_model_fields 
    WHERE name = 'transferred_id' AND model = 'sale.order'
);

-- تسجيل حقل locked
-- Register locked field
INSERT INTO ir_model_fields (name, model, field_description, ttype, state, model_id, create_date, write_date, create_uid, write_uid)
SELECT 'locked', 'sale.order', 'Locked', 'boolean', 'manual',
       (SELECT id FROM ir_model WHERE model = 'sale.order'),
       NOW(), NOW(), 1, 1
WHERE NOT EXISTS (
    SELECT 1 FROM ir_model_fields 
    WHERE name = 'locked' AND model = 'sale.order'
);

-- تسجيل حقل subscription_state
-- Register subscription_state field
INSERT INTO ir_model_fields (name, model, field_description, ttype, state, model_id, create_date, write_date, create_uid, write_uid)
SELECT 'subscription_state', 'sale.order', 'Subscription State', 'selection', 'manual',
       (SELECT id FROM ir_model WHERE model = 'sale.order'),
       NOW(), NOW(), 1, 1
WHERE NOT EXISTS (
    SELECT 1 FROM ir_model_fields 
    WHERE name = 'subscription_state' AND model = 'sale.order'
);

-- تسجيل حقل authorized_transaction_ids
-- Register authorized_transaction_ids field
INSERT INTO ir_model_fields (name, model, field_description, ttype, state, model_id, relation, create_date, write_date, create_uid, write_uid)
SELECT 'authorized_transaction_ids', 'sale.order', 'Authorized Transactions', 'many2many', 'manual',
       (SELECT id FROM ir_model WHERE model = 'sale.order'),
       'payment.transaction',
       NOW(), NOW(), 1, 1
WHERE NOT EXISTS (
    SELECT 1 FROM ir_model_fields 
    WHERE name = 'authorized_transaction_ids' AND model = 'sale.order'
);

-- إضافة قيود الفهرسة للأداء
-- Add indexing constraints for performance
\echo 'إضافة الفهارس...'
\echo 'Adding indexes...'
CREATE INDEX IF NOT EXISTS idx_sale_order_transferred_id ON sale_order(transferred_id);
CREATE INDEX IF NOT EXISTS idx_sale_order_locked ON sale_order(locked);
CREATE INDEX IF NOT EXISTS idx_sale_order_subscription_state ON sale_order(subscription_state);

-- تحديث إحصائيات الجداول
-- Update table statistics
\echo 'تحديث إحصائيات الجداول...'
\echo 'Updating table statistics...'
ANALYZE sale_order;
ANALYZE sale_order_payment_transaction_rel;
ANALYZE ir_model_fields;

\echo 'تم الانتهاء من حل مشكلة transferred_id بنجاح!'
\echo 'transferred_id fix completed successfully!'
\echo 'يرجى إعادة تشغيل خادم Odoo لتطبيق التغييرات'
\echo 'Please restart Odoo server to apply changes'