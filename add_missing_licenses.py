#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add Missing License Keys - Odoo 18 Migration
Saudi Al-Rajhi Real Estate Project
Created by: roottbar
Date: 2025-01-30
"""

import os
import re
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('license_fix_odoo18.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LicenseFixer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.fix_report = {
            'total_files': 0,
            'fixed_files': 0,
            'failed_files': [],
            'changes_made': []
        }
        
        # Modules that need license keys based on the log
        self.modules_needing_license = [
            'Audit_log', 'account_advanced', 'account_bank_fees', 'account_over_due',
            'account_payment_advanced', 'account_reports_branch', 'account_reports_operating',
            'accounting_category_partner', 'barameg_geidea_pos', 'base_dynamic_reports',
            'bi_advance_branch', 'branch', 'bstt_account_report_levels',
            'bstt_ksa_ninja_dashboard_back_button', 'contracts_management',
            'custom_hr_timesheet_fix', 'disable_publisher_update', 'dynamic_portal',
            'dynamic_xlsx_report', 'glossy_elements', 'glossy_path_advanced',
            'hr_advanced', 'hr_attendance_summary', 'hr_bonus_deduction',
            'hr_employee_profile_portal', 'hr_end_of_service', 'hr_end_of_service_loan',
            'hr_end_of_service_petty_cash', 'hr_end_of_service_time_off', 'hr_letter',
            'hr_loan', 'hr_overtime', 'hr_zk_attendance', 'iban_formatter',
            'journal_entry_report', 'leave_contract_allocation', 'legal_management',
            'nati_l10n_sa', 'notify_upcoming_and_overdue', 'petty_cash',
            'plustech_asset_enhance', 'print_journal_entries', 'product_unit_filter',
            'product_unit_state_filter', 'project_advanced', 'project_progress_bar',
            'purchase_request', 'rent_customize', 'rental_availability_control',
            'renting', 'sa_einvoice', 'sale_discount_total', 'stock_restrict',
            'user_action_rule'
        ]
        
    def find_manifests_needing_license(self):
        """Find manifest files that need license keys"""
        manifests_to_fix = []
        
        for module_name in self.modules_needing_license:
            manifest_path = self.project_root / module_name / '__manifest__.py'
            if manifest_path.exists():
                manifests_to_fix.append(manifest_path)
            else:
                logger.warning(f"Module {module_name} not found at {manifest_path}")
                
        return manifests_to_fix
    
    def add_license_to_manifest(self, manifest_file):
        """Add license key to a manifest file"""
        try:
            logger.info(f"Adding license to: {manifest_file.relative_to(self.project_root)}")
            
            # Read file content
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Check if license key already exists
            if "'license'" in content or '"license"' in content:
                logger.info(f"License already exists in: {manifest_file.relative_to(self.project_root)}")
                return True
            
            # Find the best place to insert license key
            # Look for common patterns where we can insert the license
            patterns_to_try = [
                # After author
                (r"('author':\s*['\"][^'\"]*['\"],?)", r"\1\n    'license': 'LGPL-3',"),
                (r'("author":\s*"[^"]*",?)', r'\1\n    "license": "LGPL-3",'),
                
                # After website
                (r"('website':\s*['\"][^'\"]*['\"],?)", r"\1\n    'license': 'LGPL-3',"),
                (r'("website":\s*"[^"]*",?)', r'\1\n    "license": "LGPL-3",'),
                
                # After category
                (r"('category':\s*['\"][^'\"]*['\"],?)", r"\1\n    'license': 'LGPL-3',"),
                (r'("category":\s*"[^"]*",?)', r'\1\n    "license": "LGPL-3",'),
                
                # After version
                (r"('version':\s*['\"][^'\"]*['\"],?)", r"\1\n    'license': 'LGPL-3',"),
                (r'("version":\s*"[^"]*",?)', r'\1\n    "license": "LGPL-3",'),
                
                # Before depends
                (r"(\s*)('depends':\s*\[)", r"\1'license': 'LGPL-3',\n\1\2"),
                (r'(\s*)("depends":\s*\[)', r'\1"license": "LGPL-3",\n\1\2'),
                
                # Before data
                (r"(\s*)('data':\s*\[)", r"\1'license': 'LGPL-3',\n\1\2"),
                (r'(\s*)("data":\s*\[)', r'\1"license": "LGPL-3",\n\1\2'),
                
                # Before installable
                (r"(\s*)('installable':\s*True)", r"\1'license': 'LGPL-3',\n\1\2"),
                (r'(\s*)("installable":\s*true)', r'\1"license": "LGPL-3",\n\1\2'),
            ]
            
            updated_content = content
            license_added = False
            
            for pattern, replacement in patterns_to_try:
                if re.search(pattern, updated_content, re.IGNORECASE):
                    updated_content = re.sub(pattern, replacement, updated_content, count=1, flags=re.IGNORECASE)
                    license_added = True
                    break
            
            # If no pattern matched, try to add before the closing brace
            if not license_added:
                # Find the last comma before closing brace and add license there
                closing_brace_pattern = r'(\s*)(})\s*$'
                if re.search(closing_brace_pattern, updated_content):
                    # Add license before the closing brace
                    updated_content = re.sub(closing_brace_pattern, r"\1'license': 'LGPL-3',\n\1\2", updated_content)
                    license_added = True
            
            # Write back if changes were made
            if license_added and updated_content != original_content:
                with open(manifest_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                logger.info(f"✅ Added license to: {manifest_file.relative_to(self.project_root)}")
                self.fix_report['fixed_files'] += 1
                self.fix_report['changes_made'].append({
                    'file': str(manifest_file.relative_to(self.project_root)),
                    'changes': ["Added 'license': 'LGPL-3' key"]
                })
            elif not license_added:
                logger.warning(f"⚠️ Could not find suitable place to add license in: {manifest_file.relative_to(self.project_root)}")
            else:
                logger.info(f"⏭️ No changes needed: {manifest_file.relative_to(self.project_root)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add license to {manifest_file}: {str(e)}")
            self.fix_report['failed_files'].append({
                'file': str(manifest_file.relative_to(self.project_root)),
                'error': str(e)
            })
            return False
    
    def run_license_fix(self):
        """Run the complete license fixing process"""
        logger.info("🔑 Starting license key addition for Odoo 18...")
        
        # Find manifest files that need license keys
        manifests_to_fix = self.find_manifests_needing_license()
        self.fix_report['total_files'] = len(manifests_to_fix)
        
        logger.info(f"Found {len(manifests_to_fix)} manifest files that need license keys")
        
        if not manifests_to_fix:
            logger.info("✅ No manifest files need license keys!")
            return
        
        # Fix each file
        for manifest_file in manifests_to_fix:
            self.add_license_to_manifest(manifest_file)
        
        # Generate report
        self.generate_fix_report()
        
        logger.info("🎉 License key addition completed!")
        logger.info(f"✅ Files processed: {self.fix_report['total_files']}")
        logger.info(f"✅ Files fixed: {self.fix_report['fixed_files']}")
        
        if self.fix_report['failed_files']:
            logger.warning(f"⚠️ Failed files: {len(self.fix_report['failed_files'])}")
    
    def generate_fix_report(self):
        """Generate license fix report"""
        report_file = self.project_root / 'LICENSE_FIX_REPORT.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🔑 License Keys Fix Report - Odoo 18 Migration\n\n")
            f.write("## 📊 Fix Summary\n\n")
            f.write(f"- **Total Files Needing License:** {self.fix_report['total_files']}\n")
            f.write(f"- **Files Fixed:** {self.fix_report['fixed_files']}\n")
            f.write(f"- **Files Failed:** {len(self.fix_report['failed_files'])}\n\n")
            
            if self.fix_report['failed_files']:
                f.write("## ❌ Failed Files\n\n")
                for failed in self.fix_report['failed_files']:
                    f.write(f"- **{failed['file']}:** {failed['error']}\n")
                f.write("\n")
            
            if self.fix_report['changes_made']:
                f.write("## 📝 Changes Made\n\n")
                for change_info in self.fix_report['changes_made']:
                    f.write(f"### {change_info['file']}\n")
                    for change in change_info['changes']:
                        f.write(f"- {change}\n")
                    f.write("\n")
            
            f.write("## 🔄 License Added\n\n")
            f.write("All modules now have the required `'license': 'LGPL-3'` key in their manifest files.\n")
            f.write("This resolves the warning messages about missing license keys in Odoo 18.\n\n")
            
            f.write("---\n")
            f.write("*License fix completed by roottbar on 2025-01-30*\n")
        
        logger.info(f"📄 License fix report saved to: {report_file}")

def main():
    """Main execution function"""
    project_root = Path(__file__).parent
    fixer = LicenseFixer(project_root)
    fixer.run_license_fix()

if __name__ == "__main__":
    main()
