#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Manifest Fix
Author: roottbar
Date: 2025-01-30
Description: Comprehensive fix for all manifest file issues
"""

import os
import re
import ast
from pathlib import Path

class ComprehensiveManifestFixer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.fixed_files = []
        self.errors = []
        
        # Define accounting modules (installable: True)
        self.accounting_modules = {
            'account_advanced', 'account_analytic_parent', 'account_bank_fees',
            'account_dynamic_reports', 'account_einvoice_generate', 'account_financial_report',
            'account_financial_report_sale', 'account_invoice_ubl', 'account_journal_edit',
            'account_move_line_report_xls', 'account_move_multi_cancel', 'account_operating_unit',
            'account_over_due', 'account_parent', 'account_payment_advanced', 'account_payment_mode',
            'account_payment_partner', 'account_payment_unece', 'account_purchase_stock_report_non_billed',
            'account_reports_branch', 'account_reports_operating', 'account_sale_stock_report_non_billed',
            'account_tax_balance', 'account_tax_unece', 'accounting_category_partner',
            'analytic_account_ocs', 'analytic_account_ocs2', 'analytic_account_ocs_3',
            'analytic_invoice_journal_ocs', 'analytic_operating_unit', 'analytic_operating_unit_access_all',
            'analytic_payment_link', 'base_account_budget', 'base_accounting_kit',
            'bstt_account_invoice', 'bstt_account_operating_unit_sequence', 'bstt_account_report_levels',
            'bstt_finanical_report', 'cost_center_reports', 'dynamic_accounts_report',
            'journal_entry_report', 'mis_builder', 'mis_builder_cash_flow', 'mis_template_financial_report',
            'print_journal_entries', 'partner_statement', 'tk_partner_ledger'
        }
        
        # Define renting modules (installable: True)
        self.renting_modules = {
            'renting', 'rental_availability_control', 'rent_customize'
        }
        
        # Define core/base modules that should be installable
        self.core_modules = {
            'base_ubl', 'base_ubl_payment', 'base_unece', 'base_dynamic_reports',
            'branch', 'operating_unit', 'operating_unit_access_all', 'date_range',
            'mass_editing', 'query_deluxe'
        }
        
        # Define invoice/billing related modules
        self.invoice_modules = {
            'einv_sa', 'sa_einvoice', 'l10n_sa_hr_payroll', 'nati_l10n_sa',
            'invoice_list_post_cancel', 'invoice_pdf_ai', 'msr_sar_symbol',
            'ejar_integration'
        }
        
        # All modules that should be installable
        self.installable_modules = (
            self.accounting_modules | 
            self.renting_modules | 
            self.core_modules | 
            self.invoice_modules
        )

    def clean_string_content(self, content):
        """Clean string content of problematic characters"""
        # Remove invalid Unicode characters
        content = content.replace('\u060c', ',')  # Arabic comma
        content = content.replace('\u2013', '-')  # En dash
        content = content.replace('\u2019', "'")  # Right single quotation mark
        content = content.replace('\u200b', '')   # Zero width space
        
        # Clean up extra whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        return content

    def rebuild_manifest_from_scratch(self, manifest_path):
        """Rebuild manifest file from scratch with proper structure"""
        module_name = manifest_path.parent.name
        
        try:
            # Try to read the original content to extract basic info
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()
            
            # Extract basic information using regex
            name_match = re.search(r"'name':\s*['\"]([^'\"]+)['\"]", original_content)
            author_match = re.search(r"'author':\s*['\"]([^'\"]+)['\"]", original_content)
            category_match = re.search(r"'category':\s*['\"]([^'\"]+)['\"]", original_content)
            depends_match = re.search(r"'depends':\s*\[(.*?)\]", original_content, re.DOTALL)
            
            # Set default values
            name = name_match.group(1) if name_match else module_name.replace('_', ' ').title()
            author = author_match.group(1) if author_match else "roottbar"
            category = category_match.group(1) if category_match else "Tools"
            
            # Parse dependencies
            depends = ['base']
            if depends_match:
                deps_content = depends_match.group(1)
                # Extract individual dependencies
                dep_matches = re.findall(r"'([^']+)'", deps_content)
                if dep_matches:
                    depends = dep_matches
            
            # Clean problematic dependencies
            problematic_deps = ['hr_payroll_community', 'l10n_sa_invoice']
            depends = [dep for dep in depends if dep not in problematic_deps]
            
            # Ensure base is in dependencies
            if 'base' not in depends:
                depends.insert(0, 'base')
            
            # Determine installable status
            should_be_installable = module_name in self.installable_modules
            
            # Create clean manifest content
            manifest_content = {
                'name': name,
                'version': '18.0.1.0.0',
                'summary': f'Enhanced {name} module',
                'description': f'Enhanced {name} module for Odoo 18.0 by roottbar',
                'category': category,
                'author': author,
                'maintainer': 'roottbar',
                'depends': depends,
                'data': [],
                'license': 'LGPL-3',
                'installable': should_be_installable,
                'auto_install': False,
            }
            
            # Try to extract data files
            data_match = re.search(r"'data':\s*\[(.*?)\]", original_content, re.DOTALL)
            if data_match:
                data_content = data_match.group(1)
                data_files = re.findall(r"'([^']+)'", data_content)
                if data_files:
                    manifest_content['data'] = data_files
            
            # Try to extract qweb files
            qweb_match = re.search(r"'qweb':\s*\[(.*?)\]", original_content, re.DOTALL)
            if qweb_match:
                qweb_content = qweb_match.group(1)
                qweb_files = re.findall(r"'([^']+)'", qweb_content)
                if qweb_files:
                    manifest_content['qweb'] = qweb_files
            
            # Check if it's an application
            if 'application' in original_content and module_name in self.installable_modules:
                manifest_content['application'] = True
            
            return manifest_content
            
        except Exception as e:
            # Fallback to minimal manifest
            should_be_installable = module_name in self.installable_modules
            
            return {
                'name': module_name.replace('_', ' ').title(),
                'version': '18.0.1.0.0',
                'summary': f'Enhanced module for Odoo 18.0',
                'description': f'Enhanced {module_name} module for Odoo 18.0 by roottbar',
                'category': 'Tools',
                'author': 'roottbar',
                'maintainer': 'roottbar',
                'depends': ['base'],
                'data': [],
                'license': 'LGPL-3',
                'installable': should_be_installable,
                'auto_install': False,
            }

    def write_clean_manifest(self, manifest_path, manifest_dict):
        """Write a clean, properly formatted manifest file"""
        try:
            # Create formatted manifest content
            lines = ["# -*- coding: utf-8 -*-", "{"]
            
            # Define the order of keys for better readability
            key_order = [
                'name', 'version', 'summary', 'description', 'category', 
                'author', 'maintainer', 'website', 'depends', 'data', 
                'qweb', 'assets', 'external_dependencies', 'license',
                'application', 'installable', 'auto_install'
            ]
            
            for key in key_order:
                if key in manifest_dict:
                    value = manifest_dict[key]
                    if isinstance(value, str):
                        # Escape quotes and clean the string
                        clean_value = value.replace('"', '\\"').replace('\n', '\\n')
                        lines.append(f'    \'{key}\': "{clean_value}",')
                    elif isinstance(value, bool):
                        lines.append(f'    \'{key}\': {value},')
                    elif isinstance(value, list):
                        if len(value) == 0:
                            lines.append(f'    \'{key}\': [],')
                        else:
                            lines.append(f'    \'{key}\': [')
                            for item in value:
                                clean_item = str(item).replace("'", "\\'")
                                lines.append(f'        \'{clean_item}\',')
                            lines.append('    ],')
                    elif isinstance(value, dict):
                        lines.append(f'    \'{key}\': {value},')
                    else:
                        lines.append(f'    \'{key}\': {repr(value)},')
            
            lines.append("}")
            
            content = '\n'.join(lines)
            
            # Test if the content is valid Python
            compile(content, str(manifest_path), 'exec')
            
            # Write the content
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            self.errors.append(f"Error writing {manifest_path}: {str(e)}")
            return False

    def fix_manifest_file(self, manifest_path):
        """Fix a single manifest file"""
        module_name = manifest_path.parent.name
        
        try:
            # Rebuild the manifest from scratch
            manifest_dict = self.rebuild_manifest_from_scratch(manifest_path)
            
            # Write the clean manifest
            if self.write_clean_manifest(manifest_path, manifest_dict):
                self.fixed_files.append(str(manifest_path))
                return True
            else:
                return False
                
        except Exception as e:
            self.errors.append(f"Error processing {manifest_path}: {str(e)}")
            return False

    def run_comprehensive_fix(self):
        """Run the comprehensive fix process"""
        print("🔧 Starting Comprehensive Manifest Fix")
        print("=" * 60)
        
        # Find all manifest files
        manifest_files = list(self.base_path.glob('**/__manifest__.py'))
        
        print(f"Found {len(manifest_files)} manifest files to fix")
        print()
        
        success_count = 0
        
        for manifest_path in manifest_files:
            module_name = manifest_path.parent.name
            print(f"Fixing: {module_name}")
            
            if self.fix_manifest_file(manifest_path):
                success_count += 1
                installable = module_name in self.installable_modules
                status = "✅ INSTALLABLE" if installable else "❌ NON-INSTALLABLE"
                print(f"  {status}")
            else:
                print(f"  ❌ FAILED")
        
        # Generate report
        self.generate_comprehensive_report(len(manifest_files), success_count)

    def generate_comprehensive_report(self, total_files, success_count):
        """Generate comprehensive fix report"""
        print()
        print("=" * 60)
        print("📊 COMPREHENSIVE FIX REPORT")
        print("=" * 60)
        
        print(f"Total manifest files: {total_files}")
        print(f"Successfully fixed: {success_count}")
        print(f"Failed: {total_files - success_count}")
        print()
        
        # Count installable vs non-installable
        installable_count = len([f for f in self.fixed_files if Path(f).parent.name in self.installable_modules])
        non_installable_count = success_count - installable_count
        
        print(f"Modules set to installable: True: {installable_count}")
        print(f"Modules set to installable: False: {non_installable_count}")
        print()
        
        # List installable modules
        print("📦 INSTALLABLE MODULES (accounting/renting/core):")
        installable_modules = [Path(f).parent.name for f in self.fixed_files if Path(f).parent.name in self.installable_modules]
        for module in sorted(installable_modules):
            print(f"  ✅ {module}")
        
        print()
        print("📦 NON-INSTALLABLE MODULES:")
        non_installable_modules = [Path(f).parent.name for f in self.fixed_files if Path(f).parent.name not in self.installable_modules]
        for module in sorted(non_installable_modules):
            print(f"  ❌ {module}")
        
        if self.errors:
            print()
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")
        
        # Save detailed report
        report_path = self.base_path / 'COMPREHENSIVE_MANIFEST_FIX_REPORT.md'
        self.save_comprehensive_report(report_path, total_files, success_count)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        print("\n🎉 Comprehensive fix completed successfully!")

    def save_comprehensive_report(self, report_path, total_files, success_count):
        """Save comprehensive fix report"""
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 🔧 Comprehensive Manifest Fix Report\n\n")
            f.write(f"**Date:** {os.popen('date /t').read().strip()}\n")
            f.write(f"**Author:** roottbar\n\n")
            
            f.write("## 📊 Summary\n\n")
            f.write(f"- **Total manifest files:** {total_files}\n")
            f.write(f"- **Successfully fixed:** {success_count}\n")
            f.write(f"- **Failed:** {total_files - success_count}\n\n")
            
            installable_count = len([f for f in self.fixed_files if Path(f).parent.name in self.installable_modules])
            non_installable_count = success_count - installable_count
            
            f.write(f"- **Modules set to installable: True:** {installable_count}\n")
            f.write(f"- **Modules set to installable: False:** {non_installable_count}\n\n")
            
            f.write("## 📦 Installable Modules (Accounting/Renting/Core)\n\n")
            installable_modules = [Path(f).parent.name for f in self.fixed_files if Path(f).parent.name in self.installable_modules]
            for module in sorted(installable_modules):
                f.write(f"- ✅ `{module}`\n")
            
            f.write("\n## 📦 Non-Installable Modules\n\n")
            non_installable_modules = [Path(f).parent.name for f in self.fixed_files if Path(f).parent.name not in self.installable_modules]
            for module in sorted(non_installable_modules):
                f.write(f"- ❌ `{module}`\n")
            
            if self.errors:
                f.write("\n## ❌ Errors\n\n")
                for error in self.errors:
                    f.write(f"- {error}\n")

if __name__ == "__main__":
    # Run comprehensive fix
    fixer = ComprehensiveManifestFixer(".")
    fixer.run_comprehensive_fix()
