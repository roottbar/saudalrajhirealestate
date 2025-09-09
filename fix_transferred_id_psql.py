#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حل مشكلة transferred_id باستخدام psql و Odoo shell
Script to fix transferred_id error using psql and Odoo shell
"""

import os
import sys
import subprocess

def run_psql_command(command, db_name="rajhirealestateodoo"):
    """
    تشغيل أمر psql
    Run a psql command
    """
    try:
        cmd = f'psql -d {db_name} -c "{command}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr
    except Exception as e:
        return None, str(e)

def fix_transferred_id_via_psql():
    """
    حل مشكلة transferred_id عبر إضافة الحقول المطلوبة مباشرة في قاعدة البيانات
    Fix transferred_id issue by adding required fields directly to database
    """
    print("بدء حل مشكلة transferred_id باستخدام psql...")
    print("Starting transferred_id fix using psql...")
    
    # إضافة الحقول المطلوبة إلى جدول sale_order
    sql_commands = [
        # إضافة حقل transferred_id
        "ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS transferred_id INTEGER;",
        
        # إضافة حقل locked
        "ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS locked BOOLEAN DEFAULT FALSE;",
        
        # إضافة حقل subscription_state
        "ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS subscription_state VARCHAR(20) DEFAULT '1_draft';",
        
        # إنشاء جدول للعلاقة many2many مع payment_transaction
        """CREATE TABLE IF NOT EXISTS sale_order_payment_transaction_rel (
            sale_order_id INTEGER REFERENCES sale_order(id) ON DELETE CASCADE,
            payment_transaction_id INTEGER,
            PRIMARY KEY (sale_order_id, payment_transaction_id)
        );""",
        
        # إضافة الحقول إلى ir_model_fields إذا لم تكن موجودة
        """INSERT INTO ir_model_fields (name, model, field_description, ttype, state, model_id)
        SELECT 'transferred_id', 'sale.order', 'Transferred Order', 'many2one', 'manual', 
               (SELECT id FROM ir_model WHERE model = 'sale.order')
        WHERE NOT EXISTS (
            SELECT 1 FROM ir_model_fields 
            WHERE name = 'transferred_id' AND model = 'sale.order'
        );""",
        
        """INSERT INTO ir_model_fields (name, model, field_description, ttype, state, model_id)
        SELECT 'locked', 'sale.order', 'Locked', 'boolean', 'manual',
               (SELECT id FROM ir_model WHERE model = 'sale.order')
        WHERE NOT EXISTS (
            SELECT 1 FROM ir_model_fields 
            WHERE name = 'locked' AND model = 'sale.order'
        );""",
        
        """INSERT INTO ir_model_fields (name, model, field_description, ttype, state, model_id)
        SELECT 'subscription_state', 'sale.order', 'Subscription State', 'selection', 'manual',
               (SELECT id FROM ir_model WHERE model = 'sale.order')
        WHERE NOT EXISTS (
            SELECT 1 FROM ir_model_fields 
            WHERE name = 'subscription_state' AND model = 'sale.order'
        );""",
        
        """INSERT INTO ir_model_fields (name, model, field_description, ttype, state, model_id)
        SELECT 'authorized_transaction_ids', 'sale.order', 'Authorized Transactions', 'many2many', 'manual',
               (SELECT id FROM ir_model WHERE model = 'sale.order')
        WHERE NOT EXISTS (
            SELECT 1 FROM ir_model_fields 
            WHERE name = 'authorized_transaction_ids' AND model = 'sale.order'
        );"""
    ]
    
    success_count = 0
    for i, command in enumerate(sql_commands, 1):
        print(f"تنفيذ الأمر {i}/{len(sql_commands)}...")
        print(f"Executing command {i}/{len(sql_commands)}...")
        
        stdout, stderr = run_psql_command(command)
        
        if stderr and "ERROR" in stderr:
            print(f"خطأ في الأمر {i}: {stderr}")
            print(f"Error in command {i}: {stderr}")
        else:
            print(f"تم تنفيذ الأمر {i} بنجاح")
            print(f"Command {i} executed successfully")
            success_count += 1
    
    return success_count == len(sql_commands)

def create_odoo_shell_script():
    """
    إنشاء سكريبت Odoo shell لتثبيت الوحدة
    Create Odoo shell script to install the module
    """
    script_content = """
# Odoo Shell Script to install odoo17_compatibility_fix
env['ir.module.module'].update_list()
module = env['ir.module.module'].search([('name', '=', 'odoo17_compatibility_fix')])
if module:
    if module.state != 'installed':
        module.button_immediate_install()
        print("Module odoo17_compatibility_fix installed successfully!")
    else:
        print("Module odoo17_compatibility_fix is already installed")
else:
    print("Module odoo17_compatibility_fix not found in addons path")
    print("Using direct database approach...")

# تحديث cache النموذج
env.registry.clear_cache()
env.cr.commit()
print("Cache cleared and changes committed")
"""
    
    with open('install_module_shell.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    return 'install_module_shell.py'

def main():
    print("="*50)
    print("حل مشكلة transferred_id في Odoo")
    print("Fixing transferred_id issue in Odoo")
    print("="*50)
    
    # الطريقة الأولى: إضافة الحقول مباشرة عبر psql
    print("\n1. محاولة حل المشكلة عبر psql...")
    print("1. Attempting to fix via psql...")
    
    if fix_transferred_id_via_psql():
        print("✓ تم حل المشكلة بنجاح عبر psql")
        print("✓ Successfully fixed via psql")
    else:
        print("✗ فشل في حل المشكلة عبر psql")
        print("✗ Failed to fix via psql")
    
    # الطريقة الثانية: إنشاء سكريبت Odoo shell
    print("\n2. إنشاء سكريبت Odoo shell...")
    print("2. Creating Odoo shell script...")
    
    script_file = create_odoo_shell_script()
    print(f"تم إنشاء السكريبت: {script_file}")
    print(f"Script created: {script_file}")
    
    print("\n" + "="*50)
    print("التعليمات النهائية:")
    print("Final Instructions:")
    print("="*50)
    print("1. قم بتشغيل الأمر التالي لتطبيق التغييرات:")
    print("1. Run the following command to apply changes:")
    print("   python -m odoo shell -d rajhirealestateodoo -c odoo.conf < install_module_shell.py")
    print("\n2. أو استخدم psql مباشرة إذا كان متاحاً:")
    print("2. Or use psql directly if available:")
    print("   psql -d rajhirealestateodoo -f sql_fix.sql")
    print("\n3. أعد تشغيل خادم Odoo بعد التطبيق")
    print("3. Restart Odoo server after applying changes")

if __name__ == '__main__':
    main()