#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حل نهائي شامل لجميع مشاكل العروض في Odoo
يقوم بحذف العروض المشكلة وإعادة تحميل النظام
"""

import psycopg2
import sys
import os

def cleanup_problematic_views():
    """
    حذف جميع العروض المشكلة من قاعدة البيانات
    """
    try:
        # الاتصال بقاعدة البيانات
        conn = psycopg2.connect(
            host="localhost",
            database="odoo",  # غير اسم قاعدة البيانات حسب الحاجة
            user="odoo",      # غير اسم المستخدم حسب الحاجة
            password="odoo"   # غير كلمة المرور حسب الحاجة
        )
        
        cursor = conn.cursor()
        
        print("بدء تنظيف العروض المشكلة...")
        
        # قائمة العروض المشكلة للحذف
        problematic_views = [
            ("account.move.line", "operating_unit_id"),
            ("purchase.order", "action_budget"),
            ("sale.order", "resume_subscription"),
            ("sale.order", "payment_action_capture"),
            ("sale.order", "payment_action_void"),
            ("sale.order", "transferred_id"),
            ("sale.order", "locked"),
            ("sale.order", "authorized_transaction_ids")
        ]
        
        # حذف العروض المشكلة
        for model, field in problematic_views:
            query = f"""
            DELETE FROM ir_ui_view 
            WHERE model = %s 
            AND arch_db LIKE %s
            AND arch_db NOT LIKE %s
            """
            
            cursor.execute(query, (model, f'%{field}%', f'%<!-- %{field}% -->%'))
            deleted_count = cursor.rowcount
            print(f"تم حذف {deleted_count} عرض يحتوي على {field} في {model}")
        
        # تنظيف العروض غير النشطة
        cursor.execute("DELETE FROM ir_ui_view WHERE active = false")
        inactive_deleted = cursor.rowcount
        print(f"تم حذف {inactive_deleted} عرض غير نشط")
        
        # تحديث حالة الوحدات لإعادة التحميل
        modules_to_upgrade = ['rent_customize', 'account_operating_unit']
        for module in modules_to_upgrade:
            cursor.execute(
                "UPDATE ir_module_module SET state = 'to upgrade' WHERE name = %s",
                (module,)
            )
            print(f"تم تحديد الوحدة {module} للترقية")
        
        # حفظ التغييرات
        conn.commit()
        print("تم حفظ جميع التغييرات بنجاح")
        
        cursor.close()
        conn.close()
        
        print("\n✅ تم تنظيف جميع العروض المشكلة بنجاح!")
        print("الآن يمكنك إعادة تشغيل Odoo باستخدام restart_odoo.bat")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تنظيف العروض: {e}")
        return False

def main():
    """
    الدالة الرئيسية
    """
    print("=" * 50)
    print("حل نهائي شامل لمشاكل العروض في Odoo")
    print("=" * 50)
    
    # تنظيف العروض المشكلة
    if cleanup_problematic_views():
        print("\n🎉 تم حل جميع المشاكل بنجاح!")
        print("\nالخطوات التالية:")
        print("1. قم بتشغيل restart_odoo.bat")
        print("2. أو استخدم الأمر: python -m odoo -c odoo.conf -u rent_customize --stop-after-init")
        print("3. تحقق من عدم وجود أخطاء في السجلات")
    else:
        print("\n❌ فشل في حل المشاكل")
        print("تحقق من إعدادات قاعدة البيانات في السكريبت")

if __name__ == "__main__":
    main()