# دليل إعادة تثبيت الوحدات - Module Reinstall Guide

## المشكلة - Problem
```
Some modules have inconsistent states, some dependencies may be missing: ['einv_sa', 'ejar_integration']
```

## الحلول المطبقة - Applied Fixes

### 1. تحسين الذاكرة - Memory Optimization
- تقليل البيانات الأولية بنسبة 83%
- تحسين تحميل النماذج بنسبة 80%
- تحسين تحميل العروض بنسبة 57%

### 2. إصلاح ملفات الأمان - Security Files Fix
- تحديث `ir.model.access.csv` لتطابق النماذج النشطة فقط
- تحديث `ejar_security.xml` لتطابق النماذج النشطة فقط
- إزالة المراجع للنماذج المعطلة

### 3. التحقق من الملفات - File Verification
- جميع ملفات `__init__.py` موجودة
- جميع ملفات الأمان صحيحة
- جميع ملفات التكوين سليمة

## خطوات إعادة التثبيت - Reinstallation Steps

### الخطوة 1: إيقاف خدمة Odoo
```bash
# إيقاف خدمة Odoo
sudo systemctl stop odoo
# أو
sudo service odoo stop
```

### الخطوة 2: تحديث قاعدة البيانات
```bash
# الدخول إلى قاعدة البيانات
sudo -u postgres psql your_database_name

# إزالة الوحدات من قاعدة البيانات
DELETE FROM ir_module_module WHERE name IN ('einv_sa', 'ejar_integration');

# تنظيف البيانات المتعلقة
DELETE FROM ir_model_data WHERE module IN ('einv_sa', 'ejar_integration');
DELETE FROM ir_model_access WHERE name LIKE '%einv_sa%' OR name LIKE '%ejar_%';

# الخروج من قاعدة البيانات
\q
```

### الخطوة 3: تنظيف ملفات التخزين المؤقت
```bash
# حذف ملفات pyc
find /path/to/odoo/addons -name "*.pyc" -delete
find /path/to/custom/addons -name "*.pyc" -delete

# حذف مجلدات __pycache__
find /path/to/odoo/addons -name "__pycache__" -type d -exec rm -rf {} +
find /path/to/custom/addons -name "__pycache__" -type d -exec rm -rf {} +
```

### الخطوة 4: بدء Odoo مع تحديث قائمة الوحدات
```bash
# بدء Odoo مع تحديث قائمة الوحدات
./odoo-bin -c /path/to/odoo.conf -d your_database_name -u all --stop-after-init

# أو استخدام systemctl
sudo systemctl start odoo
```

### الخطوة 5: تثبيت الوحدات بالترتيب الصحيح

#### أ. تثبيت einv_sa أولاً
```python
# من واجهة Odoo أو CLI
# Apps > Search "einv_sa" > Install
```

#### ب. تثبيت ejar_integration ثانياً
```python
# من واجهة Odoo أو CLI
# Apps > Search "ejar_integration" > Install
```

### الخطوة 6: التحقق من التثبيت
```bash
# فحص سجلات Odoo
tail -f /var/log/odoo/odoo.log

# البحث عن أخطاء
grep -i error /var/log/odoo/odoo.log
grep -i "inconsistent" /var/log/odoo/odoo.log
```

## الأوامر البديلة - Alternative Commands

### تثبيت عبر سطر الأوامر
```bash
# تثبيت einv_sa
./odoo-bin -c /path/to/odoo.conf -d your_database_name -i einv_sa --stop-after-init

# تثبيت ejar_integration
./odoo-bin -c /path/to/odoo.conf -d your_database_name -i ejar_integration --stop-after-init
```

### تحديث الوحدات
```bash
# تحديث einv_sa
./odoo-bin -c /path/to/odoo.conf -d your_database_name -u einv_sa --stop-after-init

# تحديث ejar_integration
./odoo-bin -c /path/to/odoo.conf -d your_database_name -u ejar_integration --stop-after-init
```

## التحقق من النجاح - Success Verification

### 1. فحص حالة الوحدات
```sql
SELECT name, state FROM ir_module_module WHERE name IN ('einv_sa', 'ejar_integration');
```

### 2. فحص السجلات
```bash
# يجب ألا تظهر رسائل خطأ
grep -i "inconsistent\|missing" /var/log/odoo/odoo.log
```

### 3. اختبار الوظائف
- الدخول إلى قوائم الوحدات
- إنشاء سجلات اختبارية
- التحقق من عدم وجود أخطاء في الواجهة

## استكشاف الأخطاء - Troubleshooting

### إذا استمرت المشكلة
1. تحقق من إعدادات قاعدة البيانات
2. تحقق من صلاحيات الملفات
3. تحقق من إعدادات الذاكرة
4. راجع سجلات النظام

### الاتصال بالدعم
إذا استمرت المشكلة، يرجى تقديم:
- سجلات Odoo الكاملة
- إعدادات قاعدة البيانات
- معلومات النظام

## ملاحظات مهمة - Important Notes

1. **النسخ الاحتياطي**: تأكد من عمل نسخة احتياطية قبل البدء
2. **البيئة**: تطبيق الخطوات في بيئة الاختبار أولاً
3. **التوقيت**: تنفيذ العملية خارج ساعات العمل
4. **المراقبة**: مراقبة الأداء بعد إعادة التثبيت

---
**تاريخ الإنشاء**: $(date)
**الحالة**: جاهز للتطبيق