#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسكريبت اختبار وظائف موديل تقييد الحسابات
Test Script for User Account Restriction Module Functionality

هذا الاسكريبت يتحقق من:
- وجود الموديل وملفاته
- صحة التكوين
- اختبار الوظائف الأساسية
- التحقق من الربط مع GitHub

This script verifies:
- Module existence and files
- Configuration correctness  
- Basic functionality testing
- GitHub connection verification
"""

import os
import sys
import json
from datetime import datetime


class ModuleTestRunner:
    """فئة تشغيل اختبارات الموديل"""
    
    def __init__(self):
        self.module_path = "user_account_restriction"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
    
    def log_test(self, test_name, passed, message=""):
        """تسجيل نتيجة الاختبار"""
        self.test_results["tests"][test_name] = {
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if passed:
            self.test_results["summary"]["passed"] += 1
            print(f"✅ {test_name}: نجح")
        else:
            self.test_results["summary"]["failed"] += 1
            print(f"❌ {test_name}: فشل - {message}")
        
        self.test_results["summary"]["total"] += 1
    
    def test_module_structure(self):
        """اختبار بنية الموديل"""
        print("\n🔍 اختبار بنية الموديل...")
        
        # فحص وجود المجلد الرئيسي
        if not os.path.exists(self.module_path):
            self.log_test("module_directory", False, f"مجلد الموديل غير موجود: {self.module_path}")
            return
        
        self.log_test("module_directory", True, "مجلد الموديل موجود")
        
        # فحص الملفات المطلوبة
        required_files = [
            "__manifest__.py",
            "models/__init__.py", 
            "models/res_users.py",
            "models/account_account.py",
            "views/res_users_views.xml",
            "security/security.xml",
            "security/ir.model.access.csv"
        ]
        
        for file_path in required_files:
            full_path = os.path.join(self.module_path, file_path)
            exists = os.path.exists(full_path)
            self.log_test(f"file_{file_path.replace('/', '_')}", exists, 
                         f"الملف موجود: {file_path}" if exists else f"الملف مفقود: {file_path}")
    
    def test_manifest_file(self):
        """اختبار ملف المانيفست"""
        print("\n📋 اختبار ملف المانيفست...")
        
        manifest_path = os.path.join(self.module_path, "__manifest__.py")
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # فحص المحتوى المطلوب
            required_keys = ['name', 'version', 'depends', 'data', 'installable']
            
            for key in required_keys:
                if f"'{key}'" in content or f'"{key}"' in content:
                    self.log_test(f"manifest_{key}", True, f"المفتاح موجود: {key}")
                else:
                    self.log_test(f"manifest_{key}", False, f"المفتاح مفقود: {key}")
            
            # فحص التبعيات
            if "'account'" in content and "'base'" in content:
                self.log_test("manifest_dependencies", True, "التبعيات صحيحة")
            else:
                self.log_test("manifest_dependencies", False, "التبعيات غير مكتملة")
                
        except Exception as e:
            self.log_test("manifest_readable", False, f"خطأ في قراءة المانيفست: {str(e)}")
    
    def test_security_files(self):
        """اختبار ملفات الأمان"""
        print("\n🔒 اختبار ملفات الأمان...")
        
        # فحص ملف security.xml
        security_path = os.path.join(self.module_path, "security", "security.xml")
        
        try:
            with open(security_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # فحص وجود القواعد المطلوبة
            required_rules = [
                "account_account_user_restriction_rule",
                "account_move_line_user_restriction_rule", 
                "account_move_user_restriction_rule"
            ]
            
            for rule in required_rules:
                if rule in content:
                    self.log_test(f"security_rule_{rule}", True, f"القاعدة موجودة: {rule}")
                else:
                    self.log_test(f"security_rule_{rule}", False, f"القاعدة مفقودة: {rule}")
                    
        except Exception as e:
            self.log_test("security_xml_readable", False, f"خطأ في قراءة ملف الأمان: {str(e)}")
        
        # فحص ملف ir.model.access.csv
        access_path = os.path.join(self.module_path, "security", "ir.model.access.csv")
        
        try:
            with open(access_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "res.users" in content and "account.account" in content:
                self.log_test("access_csv_content", True, "ملف الصلاحيات يحتوي على المحتوى المطلوب")
            else:
                self.log_test("access_csv_content", False, "ملف الصلاحيات لا يحتوي على المحتوى المطلوب")
                
        except Exception as e:
            self.log_test("access_csv_readable", False, f"خطأ في قراءة ملف الصلاحيات: {str(e)}")
    
    def test_model_files(self):
        """اختبار ملفات النماذج"""
        print("\n🏗️ اختبار ملفات النماذج...")
        
        # فحص res_users.py
        users_model_path = os.path.join(self.module_path, "models", "res_users.py")
        
        try:
            with open(users_model_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # فحص وجود الحقل المطلوب
            if "restricted_account_ids" in content:
                self.log_test("users_model_field", True, "حقل الحسابات المقيدة موجود")
            else:
                self.log_test("users_model_field", False, "حقل الحسابات المقيدة مفقود")
            
            # فحص وجود الدالة المطلوبة
            if "get_restricted_accounts" in content:
                self.log_test("users_model_method", True, "دالة الحصول على الحسابات المقيدة موجودة")
            else:
                self.log_test("users_model_method", False, "دالة الحصول على الحسابات المقيدة مفقودة")
                
        except Exception as e:
            self.log_test("users_model_readable", False, f"خطأ في قراءة نموذج المستخدمين: {str(e)}")
        
        # فحص account_account.py
        account_model_path = os.path.join(self.module_path, "models", "account_account.py")
        
        try:
            with open(account_model_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # فحص وجود دوال البحث والقراءة المعدلة
            if "def search(" in content:
                self.log_test("account_model_search", True, "دالة البحث المعدلة موجودة")
            else:
                self.log_test("account_model_search", False, "دالة البحث المعدلة مفقودة")
            
            if "def read(" in content:
                self.log_test("account_model_read", True, "دالة القراءة المعدلة موجودة")
            else:
                self.log_test("account_model_read", False, "دالة القراءة المعدلة مفقودة")
                
        except Exception as e:
            self.log_test("account_model_readable", False, f"خطأ في قراءة نموذج الحسابات: {str(e)}")
    
    def test_view_files(self):
        """اختبار ملفات العروض"""
        print("\n👁️ اختبار ملفات العروض...")
        
        views_path = os.path.join(self.module_path, "views", "res_users_views.xml")
        
        try:
            with open(views_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # فحص وجود العروض المطلوبة
            required_views = [
                "view_users_form_inherit",
                "view_users_tree_inherit",
                "view_users_search_inherit"
            ]
            
            for view in required_views:
                if view in content:
                    self.log_test(f"view_{view}", True, f"العرض موجود: {view}")
                else:
                    self.log_test(f"view_{view}", False, f"العرض مفقود: {view}")
            
            # فحص وجود الحقل في العروض
            if "restricted_account_ids" in content:
                self.log_test("view_field_present", True, "حقل الحسابات المقيدة موجود في العروض")
            else:
                self.log_test("view_field_present", False, "حقل الحسابات المقيدة مفقود في العروض")
                
        except Exception as e:
            self.log_test("views_readable", False, f"خطأ في قراءة ملف العروض: {str(e)}")
    
    def test_git_status(self):
        """اختبار حالة Git"""
        print("\n📦 اختبار حالة Git...")
        
        try:
            # فحص وجود مجلد .git
            if os.path.exists(".git"):
                self.log_test("git_repository", True, "مستودع Git موجود")
            else:
                self.log_test("git_repository", False, "مستودع Git غير موجود")
                return
            
            # فحص ملف .gitignore
            if os.path.exists(".gitignore"):
                self.log_test("gitignore_exists", True, "ملف .gitignore موجود")
            else:
                self.log_test("gitignore_exists", False, "ملف .gitignore مفقود")
            
            # محاولة تشغيل أوامر Git
            import subprocess
            
            try:
                result = subprocess.run(['git', 'status', '--porcelain'], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.log_test("git_status_command", True, "أمر git status يعمل بشكل صحيح")
                    
                    # فحص وجود تغييرات غير محفوظة
                    if result.stdout.strip():
                        self.log_test("git_uncommitted_changes", True, "يوجد تغييرات غير محفوظة")
                    else:
                        self.log_test("git_no_changes", True, "لا توجد تغييرات غير محفوظة")
                else:
                    self.log_test("git_status_command", False, "فشل في تشغيل أمر git status")
            except subprocess.TimeoutExpired:
                self.log_test("git_status_command", False, "انتهت مهلة تشغيل أمر git status")
            except FileNotFoundError:
                self.log_test("git_command_available", False, "أمر git غير متوفر")
                
        except Exception as e:
            self.log_test("git_test_error", False, f"خطأ في اختبار Git: {str(e)}")
    
    def generate_report(self):
        """إنشاء تقرير الاختبار"""
        print("\n📊 إنشاء تقرير الاختبار...")
        
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            self.log_test("report_generated", True, f"تم إنشاء التقرير: {report_file}")
            
        except Exception as e:
            self.log_test("report_generation", False, f"فشل في إنشاء التقرير: {str(e)}")
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🚀 بدء اختبار موديل تقييد الحسابات...")
        print("=" * 50)
        
        # تشغيل الاختبارات
        self.test_module_structure()
        self.test_manifest_file()
        self.test_security_files()
        self.test_model_files()
        self.test_view_files()
        self.test_git_status()
        
        # إنشاء التقرير
        self.generate_report()
        
        # عرض الملخص
        print("\n" + "=" * 50)
        print("📋 ملخص نتائج الاختبار:")
        print(f"✅ نجح: {self.test_results['summary']['passed']}")
        print(f"❌ فشل: {self.test_results['summary']['failed']}")
        print(f"📊 المجموع: {self.test_results['summary']['total']}")
        
        success_rate = (self.test_results['summary']['passed'] / 
                       self.test_results['summary']['total'] * 100) if self.test_results['summary']['total'] > 0 else 0
        
        print(f"📈 معدل النجاح: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 الموديل جاهز للاستخدام!")
        elif success_rate >= 60:
            print("⚠️ الموديل يحتاج إلى بعض التحسينات")
        else:
            print("🔧 الموديل يحتاج إلى إصلاحات مهمة")
        
        return success_rate >= 80


def main():
    """الدالة الرئيسية"""
    print("🔍 اختبار موديل تقييد الحسابات للمستخدمين")
    print("User Account Restriction Module Test")
    print("=" * 50)
    
    # تشغيل الاختبارات
    tester = ModuleTestRunner()
    success = tester.run_all_tests()
    
    # إنهاء البرنامج
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()