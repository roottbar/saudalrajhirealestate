# Quick Module Fix Script for einv_sa and ejar_integration
# This script provides manual steps to fix the inconsistent module states

Write-Host "🚀 إصلاح مشكلة الحالات غير المتسقة للوحدات" -ForegroundColor Cyan
Write-Host "الوحدات المتأثرة: einv_sa, ejar_integration" -ForegroundColor Yellow

Write-Host "`n📋 الخطوات المطلوبة:" -ForegroundColor Blue

Write-Host "`n1. إيقاف خدمة Odoo" -ForegroundColor Green
Write-Host "   تشغيل الأمر: Stop-Service -Name 'odoo*' -Force" -ForegroundColor Gray

Write-Host "`n2. تنظيف ملفات Python المؤقتة" -ForegroundColor Green
Write-Host "   حذف ملفات .pyc و مجلدات __pycache__" -ForegroundColor Gray

Write-Host "`n3. تنظيف قاعدة البيانات" -ForegroundColor Green
Write-Host "   تنفيذ أوامر SQL لإزالة بيانات الوحدات القديمة" -ForegroundColor Gray

Write-Host "`n4. إعادة تشغيل Odoo وتثبيت الوحدات" -ForegroundColor Green
Write-Host "   تثبيت einv_sa أولاً، ثم ejar_integration" -ForegroundColor Gray

Write-Host "`n⚠️ تحذير مهم:" -ForegroundColor Red
Write-Host "عمل نسخة احتياطية من قاعدة البيانات قبل المتابعة!" -ForegroundColor Red

Write-Host "`n📁 الملفات المرجعية:" -ForegroundColor Blue
Write-Host "- CRITICAL_MODULE_FIX_GUIDE.md (دليل شامل)" -ForegroundColor Gray
Write-Host "- database_cleanup_commands.sql (أوامر SQL)" -ForegroundColor Gray

# إنشاء ملف أوامر SQL
$sqlCommands = @"
-- أوامر تنظيف قاعدة البيانات للوحدات einv_sa و ejar_integration
BEGIN;

-- إزالة تبعيات الوحدات
DELETE FROM ir_module_module_dependency WHERE name IN ('einv_sa', 'ejar_integration');

-- إزالة سجلات الوحدات
DELETE FROM ir_module_module WHERE name IN ('einv_sa', 'ejar_integration');

-- تنظيف النماذج والحقول
DELETE FROM ir_model_fields WHERE model LIKE 'ejar.%';
DELETE FROM ir_model WHERE model LIKE 'ejar.%';

-- تنظيف صلاحيات الوصول
DELETE FROM ir_model_access WHERE perm_model LIKE 'model_ejar_%';

-- تنظيف المجموعات الأمنية
DELETE FROM res_groups_users_rel WHERE gid IN (
    SELECT id FROM res_groups WHERE category_id IN (
        SELECT id FROM ir_module_category WHERE name LIKE '%ejar%'
    )
);
DELETE FROM res_groups WHERE category_id IN (
    SELECT id FROM ir_module_category WHERE name LIKE '%ejar%'
);
DELETE FROM ir_module_category WHERE name LIKE '%ejar%';

-- تنظيف عناصر القائمة
DELETE FROM ir_ui_menu WHERE name LIKE '%Ejar%' OR name LIKE '%ejar%';

-- تنظيف العروض والإجراءات
DELETE FROM ir_ui_view WHERE name LIKE '%ejar%';
DELETE FROM ir_actions_act_window WHERE name LIKE '%ejar%';

-- تنظيف التسلسلات والمهام المجدولة
DELETE FROM ir_sequence WHERE name LIKE '%ejar%';
DELETE FROM ir_cron WHERE name LIKE '%ejar%';

-- إعادة تعيين حالة الوحدات
UPDATE ir_module_module SET state = 'uninstalled' WHERE name IN ('einv_sa', 'ejar_integration');

-- تنظيف بيانات الوحدات
DELETE FROM ir_model_data WHERE module IN ('einv_sa', 'ejar_integration');

COMMIT;
"@

$sqlCommands | Out-File -FilePath "database_cleanup_commands.sql" -Encoding UTF8
Write-Host "`n✅ تم إنشاء ملف أوامر SQL: database_cleanup_commands.sql" -ForegroundColor Green

Write-Host "`n🔧 الخطوات التفصيلية:" -ForegroundColor Cyan

Write-Host "`nالخطوة 1: إيقاف Odoo" -ForegroundColor Yellow
$response = Read-Host "هل تريد إيقاف خدمة Odoo الآن؟ (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    try {
        $services = Get-Service -Name "odoo*" -ErrorAction SilentlyContinue
        if ($services) {
            foreach ($service in $services) {
                if ($service.Status -eq "Running") {
                    Stop-Service -Name $service.Name -Force
                    Write-Host "✅ تم إيقاف الخدمة: $($service.Name)" -ForegroundColor Green
                }
            }
        } else {
            Write-Host "ℹ️ لم يتم العثور على خدمة Odoo" -ForegroundColor Blue
        }
        
        # إيقاف العمليات المتبقية
        $processes = Get-Process -Name "*odoo*" -ErrorAction SilentlyContinue
        if ($processes) {
            $processes | Stop-Process -Force
            Write-Host "✅ تم إيقاف عمليات Odoo المتبقية" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "⚠️ خطأ في إيقاف Odoo: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nالخطوة 2: تنظيف ملفات Python" -ForegroundColor Yellow
$response = Read-Host "هل تريد تنظيف ملفات Python المؤقتة؟ (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    try {
        # حذف ملفات .pyc
        $pycFiles = Get-ChildItem -Recurse -Include "*.pyc" -ErrorAction SilentlyContinue
        if ($pycFiles) {
            $pycFiles | Remove-Item -Force
            Write-Host "✅ تم حذف $($pycFiles.Count) ملف .pyc" -ForegroundColor Green
        }
        
        # حذف مجلدات __pycache__
        $pycacheDirs = Get-ChildItem -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue
        if ($pycacheDirs) {
            $pycacheDirs | ForEach-Object { 
                Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue
            }
            Write-Host "✅ تم حذف $($pycacheDirs.Count) مجلد __pycache__" -ForegroundColor Green
        }
        
        Write-Host "✅ تم تنظيف ملفات Python بنجاح" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ خطأ في تنظيف الملفات: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "`nالخطوة 3: تنظيف قاعدة البيانات" -ForegroundColor Yellow
Write-Host "يرجى تنفيذ الأوامر الموجودة في ملف: database_cleanup_commands.sql" -ForegroundColor Red
Write-Host "في قاعدة بيانات PostgreSQL الخاصة بك" -ForegroundColor Red

Write-Host "`nالخطوة 4: إعادة تشغيل وتثبيت الوحدات" -ForegroundColor Yellow
Write-Host "بعد تنظيف قاعدة البيانات:" -ForegroundColor Gray
Write-Host "1. ابدأ تشغيل Odoo" -ForegroundColor Gray
Write-Host "2. ادخل إلى قائمة التطبيقات" -ForegroundColor Gray
Write-Host "3. ثبت einv_sa أولاً" -ForegroundColor Gray
Write-Host "4. ثبت ejar_integration ثانياً" -ForegroundColor Gray

Write-Host "`n✅ انتهى السكريبت بنجاح!" -ForegroundColor Green
Write-Host "تأكد من تنفيذ جميع الخطوات بالترتيب المحدد" -ForegroundColor Yellow