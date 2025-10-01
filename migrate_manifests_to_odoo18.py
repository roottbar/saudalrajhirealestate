#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 15 to 18 Migration Script for __manifest__.py files
Author: roottbar
Date: 2025-01-30
Description: Updates all manifest files to Odoo 18 format with selective installable flags
"""

import os
import re
import ast
import json
from pathlib import Path

class ManifestMigrator:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.changes_made = []
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

    def read_manifest(self, manifest_path):
        """Read and parse a manifest file"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the manifest as Python code
            manifest = ast.literal_eval(content.strip())
            return manifest, content
        except Exception as e:
            self.errors.append(f"Error reading {manifest_path}: {str(e)}")
            return None, None

    def write_manifest(self, manifest_path, manifest_dict):
        """Write manifest dictionary back to file with proper formatting"""
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
                        lines.append(f"    '{key}': \"{value}\",")
                    elif isinstance(value, bool):
                        lines.append(f"    '{key}': {value},")
                    elif isinstance(value, list):
                        if len(value) == 0:
                            lines.append(f"    '{key}': [],")
                        else:
                            lines.append(f"    '{key}': [")
                            for item in value:
                                lines.append(f"        '{item}',")
                            lines.append("    ],")
                    elif isinstance(value, dict):
                        lines.append(f"    '{key}': {value},")
                    else:
                        lines.append(f"    '{key}': {repr(value)},")
            
            # Add any remaining keys not in the order
            for key, value in manifest_dict.items():
                if key not in key_order:
                    if isinstance(value, str):
                        lines.append(f"    '{key}': \"{value}\",")
                    elif isinstance(value, bool):
                        lines.append(f"    '{key}': {value},")
                    else:
                        lines.append(f"    '{key}': {repr(value)},")
            
            lines.append("}")
            
            content = '\n'.join(lines)
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            self.errors.append(f"Error writing {manifest_path}: {str(e)}")
            return False

    def update_version(self, manifest, module_name):
        """Update version from 15.0.x.x.x to 18.0.x.x.x"""
        changes = []
        
        if 'version' in manifest:
            old_version = manifest['version']
            
            # Convert 15.0.x.x.x to 18.0.x.x.x
            if old_version.startswith('15.0'):
                new_version = old_version.replace('15.0', '18.0', 1)
                manifest['version'] = new_version
                changes.append(f"Updated version: {old_version} -> {new_version}")
            elif old_version.startswith('14.0'):
                new_version = old_version.replace('14.0', '18.0', 1)
                manifest['version'] = new_version
                changes.append(f"Updated version: {old_version} -> {new_version}")
            elif not old_version.startswith('18.0'):
                # Handle other version formats
                version_parts = old_version.split('.')
                if len(version_parts) >= 2:
                    new_version = f"18.0.{'.'.join(version_parts[2:])}" if len(version_parts) > 2 else "18.0.1.0.0"
                else:
                    new_version = "18.0.1.0.0"
                manifest['version'] = new_version
                changes.append(f"Updated version: {old_version} -> {new_version}")
        else:
            manifest['version'] = '18.0.1.0.0'
            changes.append("Added missing version: 18.0.1.0.0")
        
        return changes

    def set_installable_flag(self, manifest, module_name):
        """Set installable flag based on module type"""
        changes = []
        
        # Determine if module should be installable
        should_be_installable = module_name in self.installable_modules
        
        # Set installable flag
        manifest['installable'] = should_be_installable
        
        if should_be_installable:
            changes.append(f"Set installable: True (accounting/renting/core module)")
        else:
            changes.append(f"Set installable: False (non-essential module)")
        
        return changes

    def add_license_if_missing(self, manifest):
        """Add license key if missing"""
        changes = []
        
        if 'license' not in manifest:
            manifest['license'] = 'LGPL-3'
            changes.append("Added missing license: LGPL-3")
        
        return changes

    def update_dependencies(self, manifest):
        """Update dependencies for Odoo 18 compatibility"""
        changes = []
        
        if 'depends' in manifest:
            depends = manifest['depends']
            
            # Remove problematic dependencies
            problematic_deps = ['hr_payroll_community', 'l10n_sa_invoice']
            
            for dep in problematic_deps:
                if dep in depends:
                    depends.remove(dep)
                    changes.append(f"Removed problematic dependency: {dep}")
            
            # Update specific dependency mappings if needed
            dep_mappings = {
                # Add any specific dependency updates here
            }
            
            for old_dep, new_dep in dep_mappings.items():
                if old_dep in depends:
                    depends[depends.index(old_dep)] = new_dep
                    changes.append(f"Updated dependency: {old_dep} -> {new_dep}")
        
        return changes

    def process_manifest(self, manifest_path):
        """Process a single manifest file"""
        module_name = manifest_path.parent.name
        
        print(f"Processing: {module_name}")
        
        manifest, original_content = self.read_manifest(manifest_path)
        if manifest is None:
            return False
        
        changes = []
        
        # Update version
        changes.extend(self.update_version(manifest, module_name))
        
        # Set installable flag
        changes.extend(self.set_installable_flag(manifest, module_name))
        
        # Add license if missing
        changes.extend(self.add_license_if_missing(manifest))
        
        # Update dependencies
        changes.extend(self.update_dependencies(manifest))
        
        # Write updated manifest
        if changes:
            if self.write_manifest(manifest_path, manifest):
                self.changes_made.append({
                    'module': module_name,
                    'path': str(manifest_path),
                    'changes': changes
                })
                print(f"  ✅ Updated: {', '.join(changes)}")
                return True
            else:
                print(f"  ❌ Failed to write manifest")
                return False
        else:
            print(f"  ℹ️ No changes needed")
            return True

    def run_migration(self):
        """Run the complete migration process"""
        print("🚀 Starting Odoo 15 to 18 Manifest Migration")
        print("=" * 60)
        
        # Find all manifest files
        manifest_files = list(self.base_path.glob('**/__manifest__.py'))
        
        print(f"Found {len(manifest_files)} manifest files to process")
        print()
        
        success_count = 0
        
        for manifest_path in manifest_files:
            if self.process_manifest(manifest_path):
                success_count += 1
            print()
        
        # Generate report
        self.generate_report(len(manifest_files), success_count)

    def generate_report(self, total_files, success_count):
        """Generate migration report"""
        print("=" * 60)
        print("📊 MIGRATION REPORT")
        print("=" * 60)
        
        print(f"Total manifest files: {total_files}")
        print(f"Successfully processed: {success_count}")
        print(f"Failed: {total_files - success_count}")
        print()
        
        # Count installable vs non-installable
        installable_count = len([c for c in self.changes_made if any('installable: True' in change for change in c['changes'])])
        non_installable_count = len([c for c in self.changes_made if any('installable: False' in change for change in c['changes'])])
        
        print(f"Modules set to installable: True: {installable_count}")
        print(f"Modules set to installable: False: {non_installable_count}")
        print()
        
        # List installable modules
        print("📦 INSTALLABLE MODULES (accounting/renting/core):")
        installable_modules = [c['module'] for c in self.changes_made if any('installable: True' in change for change in c['changes'])]
        for module in sorted(installable_modules):
            print(f"  ✅ {module}")
        
        print()
        print("📦 NON-INSTALLABLE MODULES:")
        non_installable_modules = [c['module'] for c in self.changes_made if any('installable: False' in change for change in c['changes'])]
        for module in sorted(non_installable_modules):
            print(f"  ❌ {module}")
        
        if self.errors:
            print()
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")
        
        # Save detailed report
        report_path = self.base_path / 'ODOO18_MANIFEST_MIGRATION_REPORT.md'
        self.save_detailed_report(report_path, total_files, success_count)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        print("\n🎉 Migration completed successfully!")

    def save_detailed_report(self, report_path, total_files, success_count):
        """Save detailed migration report"""
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 🚀 Odoo 15 to 18 Manifest Migration Report\n\n")
            f.write(f"**Date:** {os.popen('date /t').read().strip()}\n")
            f.write(f"**Author:** roottbar\n\n")
            
            f.write("## 📊 Summary\n\n")
            f.write(f"- **Total manifest files:** {total_files}\n")
            f.write(f"- **Successfully processed:** {success_count}\n")
            f.write(f"- **Failed:** {total_files - success_count}\n\n")
            
            installable_count = len([c for c in self.changes_made if any('installable: True' in change for change in c['changes'])])
            non_installable_count = len([c for c in self.changes_made if any('installable: False' in change for change in c['changes'])])
            
            f.write(f"- **Modules set to installable: True:** {installable_count}\n")
            f.write(f"- **Modules set to installable: False:** {non_installable_count}\n\n")
            
            f.write("## 📦 Installable Modules (Accounting/Renting/Core)\n\n")
            installable_modules = [c['module'] for c in self.changes_made if any('installable: True' in change for change in c['changes'])]
            for module in sorted(installable_modules):
                f.write(f"- ✅ `{module}`\n")
            
            f.write("\n## 📦 Non-Installable Modules\n\n")
            non_installable_modules = [c['module'] for c in self.changes_made if any('installable: False' in change for change in c['changes'])]
            for module in sorted(non_installable_modules):
                f.write(f"- ❌ `{module}`\n")
            
            f.write("\n## 🔧 Detailed Changes\n\n")
            for change in self.changes_made:
                f.write(f"### {change['module']}\n\n")
                f.write(f"**Path:** `{change['path']}`\n\n")
                f.write("**Changes:**\n")
                for c in change['changes']:
                    f.write(f"- {c}\n")
                f.write("\n")
            
            if self.errors:
                f.write("## ❌ Errors\n\n")
                for error in self.errors:
                    f.write(f"- {error}\n")

if __name__ == "__main__":
    # Run migration
    migrator = ManifestMigrator(".")
    migrator.run_migration()
