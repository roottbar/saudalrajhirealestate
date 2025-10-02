#!/usr/bin/env python3
"""
Module Validation Script for Odoo 18 Migration
Validates module structure, imports, and dependencies for inconsistent modules.
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path

# List of modules with inconsistent states from the error log
INCONSISTENT_MODULES = [
    'account_dynamic_reports', 'account_financial_report', 'account_financial_report_sale',
    'account_move_line_report_xls', 'account_move_multi_cancel', 'account_operating_unit',
    'account_parent', 'account_tax_balance', 'analytic_invoice_journal_ocs',
    'analytic_operating_unit', 'analytic_payment_link', 'bstt_account_invoice',
    'bstt_account_operating_unit_sequence', 'bstt_account_report_levels',
    'bstt_finanical_report', 'bstt_finger_print', 'bstt_hr', 'bstt_hr_attendance',
    'bstt_hr_payroll_analytic_account', 'bstt_hr_payroll_analytic_account_new',
    'bstt_ksa_ninja_dashboard_back_button', 'bstt_partner', 'bstt_remove_analytic_account',
    'cr_activity_report', 'customer_tickets', 'date_range', 'dp_biostar_2_biomatric_attendance',
    'hide_menu_user', 'hr_advanced', 'hr_attendance_multi_company', 'hr_contract_types_ksa',
    'hr_end_of_service', 'hr_end_of_service_sa_ocs', 'hr_loan', 'hr_resume_ats2',
    'hr_zk_attendance', 'iban_formatter', 'ks_dashboard_ninja', 'ks_dn_advance',
    'material_purchase_requisitions', 'mis_builder', 'mis_builder_cash_flow',
    'odoo_readonly_user', 'operating_unit', 'partner_statement', 'plustech_asset_enhance',
    'print_journal_entries', 'purchase_decimal_precision', 'purchase_discount',
    'purchase_request', 'query_deluxe', 'rent_customize', 'rental_availability_control',
    'renting', 'report_xlsx', 'report_xlsx_helper', 'sale_operating_unit',
    'sales_team_operating_unit', 'sha_po_dynamic_approval', 'stock_operating_unit',
    'tk_partner_ledger', 'user_action_rule', 'web_google_maps'
]

class ModuleValidator:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.results = {}
        
    def validate_module(self, module_name):
        """Validate a single module"""
        module_path = self.base_path / module_name
        result = {
            'exists': False,
            'manifest_valid': False,
            'manifest_errors': [],
            'python_files_valid': True,
            'python_errors': [],
            'import_errors': [],
            'dependencies': [],
            'missing_dependencies': []
        }
        
        if not module_path.exists():
            result['exists'] = False
            return result
            
        result['exists'] = True
        
        # Check manifest file
        manifest_path = module_path / '__manifest__.py'
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_content = f.read()
                    
                # Parse manifest
                manifest_ast = ast.parse(manifest_content)
                manifest_dict = ast.literal_eval(manifest_ast.body[0].value)
                result['manifest_valid'] = True
                result['dependencies'] = manifest_dict.get('depends', [])
                
                # Check if dependencies exist
                for dep in result['dependencies']:
                    if dep not in ['base', 'web', 'mail', 'account', 'stock', 'sale', 'purchase', 'hr']:
                        dep_path = self.base_path / dep
                        if not dep_path.exists():
                            result['missing_dependencies'].append(dep)
                            
            except Exception as e:
                result['manifest_valid'] = False
                result['manifest_errors'].append(str(e))
        else:
            result['manifest_errors'].append('__manifest__.py not found')
            
        # Check Python files
        for py_file in module_path.rglob('*.py'):
            if py_file.name == '__manifest__.py':
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for syntax errors
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    result['python_files_valid'] = False
                    result['python_errors'].append(f"{py_file.relative_to(module_path)}: {e}")
                    
                # Check for problematic imports
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            if node.module and 'odoo.addons.web.controllers.report' in node.module:
                                result['import_errors'].append(f"{py_file.relative_to(module_path)}: Uses deprecated import path")
                                
                except Exception as e:
                    result['import_errors'].append(f"{py_file.relative_to(module_path)}: {e}")
                    
            except Exception as e:
                result['python_files_valid'] = False
                result['python_errors'].append(f"{py_file.relative_to(module_path)}: {e}")
                
        return result
        
    def validate_all_modules(self):
        """Validate all inconsistent modules"""
        print("🔍 Validating modules with inconsistent states...")
        print("=" * 60)
        
        for module_name in INCONSISTENT_MODULES:
            print(f"\n📦 Validating module: {module_name}")
            result = self.validate_module(module_name)
            self.results[module_name] = result
            
            if not result['exists']:
                print(f"   ❌ Module directory not found")
                continue
                
            if not result['manifest_valid']:
                print(f"   ❌ Manifest errors: {', '.join(result['manifest_errors'])}")
            else:
                print(f"   ✅ Manifest valid")
                
            if not result['python_files_valid']:
                print(f"   ❌ Python syntax errors: {len(result['python_errors'])}")
                for error in result['python_errors'][:3]:  # Show first 3 errors
                    print(f"      - {error}")
            else:
                print(f"   ✅ Python files valid")
                
            if result['import_errors']:
                print(f"   ⚠️  Import issues: {len(result['import_errors'])}")
                for error in result['import_errors'][:3]:  # Show first 3 errors
                    print(f"      - {error}")
                    
            if result['missing_dependencies']:
                print(f"   ❌ Missing dependencies: {', '.join(result['missing_dependencies'])}")
            else:
                print(f"   ✅ All dependencies found")
                
        self.generate_summary()
        
    def generate_summary(self):
        """Generate validation summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        total_modules = len(INCONSISTENT_MODULES)
        existing_modules = sum(1 for r in self.results.values() if r['exists'])
        valid_manifests = sum(1 for r in self.results.values() if r['manifest_valid'])
        valid_python = sum(1 for r in self.results.values() if r['python_files_valid'])
        modules_with_import_errors = sum(1 for r in self.results.values() if r['import_errors'])
        modules_with_missing_deps = sum(1 for r in self.results.values() if r['missing_dependencies'])
        
        print(f"Total modules checked: {total_modules}")
        print(f"Existing modules: {existing_modules}")
        print(f"Valid manifests: {valid_manifests}")
        print(f"Valid Python files: {valid_python}")
        print(f"Modules with import errors: {modules_with_import_errors}")
        print(f"Modules with missing dependencies: {modules_with_missing_deps}")
        
        # List problematic modules
        print("\n🚨 PROBLEMATIC MODULES:")
        for module_name, result in self.results.items():
            issues = []
            if not result['exists']:
                issues.append("missing")
            if not result['manifest_valid']:
                issues.append("manifest")
            if not result['python_files_valid']:
                issues.append("syntax")
            if result['import_errors']:
                issues.append("imports")
            if result['missing_dependencies']:
                issues.append("dependencies")
                
            if issues:
                print(f"   - {module_name}: {', '.join(issues)}")
                
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("1. Fix missing modules or remove them from the addons path")
        print("2. Update import statements for Odoo 18 compatibility")
        print("3. Install missing dependencies or update manifest files")
        print("4. Fix Python syntax errors")
        print("5. Consider using Odoo 18 instead of Odoo 17 for this migration")

if __name__ == "__main__":
    base_path = Path(__file__).parent
    validator = ModuleValidator(base_path)
    validator.validate_all_modules()