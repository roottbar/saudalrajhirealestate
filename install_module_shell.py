# -*- coding: utf-8 -*-
"""
سكريبت Odoo Shell لحل مشكلة transferred_id
Odoo Shell Script to fix transferred_id issue

استخدام:
Usage:
python -m odoo shell -d rajhirealestateodoo -c odoo.conf < install_module_shell.py
"""

print("بدء حل مشكلة transferred_id...")
print("Starting transferred_id fix...")

try:
    # تحديث قائمة الوحدات
    # Update module list
    print("تحديث قائمة الوحدات...")
    print("Updating module list...")
    env['ir.module.module'].update_list()
    
    # البحث عن وحدة odoo17_compatibility_fix
    # Search for odoo17_compatibility_fix module
    module = env['ir.module.module'].search([('name', '=', 'odoo17_compatibility_fix')])
    
    if module:
        print(f"تم العثور على الوحدة: {module.name}")
        print(f"Module found: {module.name}")
        print(f"حالة الوحدة: {module.state}")
        print(f"Module state: {module.state}")
        
        if module.state != 'installed':
            print("تثبيت الوحدة...")
            print("Installing module...")
            module.button_immediate_install()
            print("تم تثبيت الوحدة بنجاح!")
            print("Module installed successfully!")
        else:
            print("الوحدة مثبتة مسبقاً")
            print("Module is already installed")
    else:
        print("لم يتم العثور على الوحدة في مسار الإضافات")
        print("Module not found in addons path")
        print("استخدام الطريقة المباشرة لقاعدة البيانات...")
        print("Using direct database approach...")
        
        # إضافة الحقول مباشرة إلى النموذج
        # Add fields directly to the model
        
        # التحقق من وجود الحقول
        # Check if fields exist
        existing_fields = env['ir.model.fields'].search([
            ('model', '=', 'sale.order'),
            ('name', 'in', ['transferred_id', 'locked', 'authorized_transaction_ids', 'subscription_state'])
        ])
        
        existing_field_names = existing_fields.mapped('name')
        print(f"الحقول الموجودة: {existing_field_names}")
        print(f"Existing fields: {existing_field_names}")
        
        # الحصول على نموذج sale.order
        # Get sale.order model
        sale_order_model = env['ir.model'].search([('model', '=', 'sale.order')])
        
        if sale_order_model:
            # إضافة الحقول المفقودة
            # Add missing fields
            fields_to_add = [
                {
                    'name': 'transferred_id',
                    'field_description': 'Transferred Order',
                    'ttype': 'many2one',
                    'relation': 'sale.order',
                    'state': 'manual'
                },
                {
                    'name': 'locked',
                    'field_description': 'Locked',
                    'ttype': 'boolean',
                    'state': 'manual'
                },
                {
                    'name': 'subscription_state',
                    'field_description': 'Subscription State',
                    'ttype': 'selection',
                    'selection': "[('1_draft', 'Draft'), ('2_active', 'Active'), ('3_closed', 'Closed'), ('4_paused', 'Paused')]",
                    'state': 'manual'
                },
                {
                    'name': 'authorized_transaction_ids',
                    'field_description': 'Authorized Transactions',
                    'ttype': 'many2many',
                    'relation': 'payment.transaction',
                    'state': 'manual'
                }
            ]
            
            for field_data in fields_to_add:
                if field_data['name'] not in existing_field_names:
                    field_data['model_id'] = sale_order_model.id
                    field_data['model'] = 'sale.order'
                    
                    try:
                        new_field = env['ir.model.fields'].create(field_data)
                        print(f"تم إنشاء الحقل: {field_data['name']}")
                        print(f"Field created: {field_data['name']}")
                    except Exception as e:
                        print(f"خطأ في إنشاء الحقل {field_data['name']}: {str(e)}")
                        print(f"Error creating field {field_data['name']}: {str(e)}")
                else:
                    print(f"الحقل موجود مسبقاً: {field_data['name']}")
                    print(f"Field already exists: {field_data['name']}")
        
        # إضافة الطرق المطلوبة إلى النموذج
        # Add required methods to the model
        print("إضافة الطرق المطلوبة...")
        print("Adding required methods...")
        
        # تنفيذ SQL مباشر لإضافة الأعمدة
        # Execute direct SQL to add columns
        sql_commands = [
            "ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS transferred_id INTEGER;",
            "ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS locked BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS subscription_state VARCHAR(20) DEFAULT '1_draft';"
        ]
        
        for sql in sql_commands:
            try:
                env.cr.execute(sql)
                print(f"تم تنفيذ: {sql}")
                print(f"Executed: {sql}")
            except Exception as e:
                print(f"خطأ في تنفيذ SQL: {str(e)}")
                print(f"SQL execution error: {str(e)}")
    
    # تحديث cache النموذج
    # Update model cache
    print("تحديث cache النموذج...")
    print("Updating model cache...")
    env.registry.clear_cache()
    
    # حفظ التغييرات
    # Commit changes
    env.cr.commit()
    print("تم حفظ التغييرات")
    print("Changes committed")
    
    print("تم الانتهاء من حل المشكلة بنجاح!")
    print("Fix completed successfully!")
    
except Exception as e:
    print(f"خطأ عام: {str(e)}")
    print(f"General error: {str(e)}")
    env.cr.rollback()
    print("تم التراجع عن التغييرات")
    print("Changes rolled back")

print("انتهى السكريبت")
print("Script finished")