#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Remaining Version Issues - Odoo 18 Migration
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
        logging.FileHandler('version_fix_odoo18.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VersionFixer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.fix_report = {
            'total_files': 0,
            'fixed_files': 0,
            'failed_files': [],
            'changes_made': []
        }
        
    def find_problematic_manifests(self):
        """Find all manifest files with version issues"""
        problematic_files = []
        
        # Find all __manifest__.py files
        for manifest_file in self.project_root.rglob('__manifest__.py'):
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for problematic version patterns
                version_patterns = [
                    r'"version":\s*"14\.0\.',  # 14.0.x.x.x
                    r'"version":\s*"15\.0\.',  # 15.0.x.x.x  
                    r'"version":\s*"16\.0\.',  # 16.0.x.x.x
                    r'"version":\s*"17\.0\.',  # 17.0.x.x.x
                    r"'version':\s*'14\.0\.",  # Single quotes version
                    r"'version':\s*'15\.0\.",
                    r"'version':\s*'16\.0\.",
                    r"'version':\s*'17\.0\.",
                ]
                
                for pattern in version_patterns:
                    if re.search(pattern, content):
                        problematic_files.append(manifest_file)
                        break
                        
            except Exception as e:
                logger.error(f"Error reading {manifest_file}: {str(e)}")
                
        return problematic_files
    
    def fix_manifest_version(self, manifest_file):
        """Fix version in a single manifest file"""
        try:
            logger.info(f"Fixing version in: {manifest_file.relative_to(self.project_root)}")
            
            # Read file content
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Version replacement patterns
            version_replacements = [
                # Double quotes patterns
                (r'"version":\s*"14\.0\.([^"]+)"', r'"version": "18.0.\1"'),
                (r'"version":\s*"15\.0\.([^"]+)"', r'"version": "18.0.\1"'),
                (r'"version":\s*"16\.0\.([^"]+)"', r'"version": "18.0.\1"'),
                (r'"version":\s*"17\.0\.([^"]+)"', r'"version": "18.0.\1"'),
                
                # Single quotes patterns
                (r"'version':\s*'14\.0\.([^']+)'", r"'version': '18.0.\1'"),
                (r"'version':\s*'15\.0\.([^']+)'", r"'version': '18.0.\1'"),
                (r"'version':\s*'16\.0\.([^']+)'", r"'version': '18.0.\1'"),
                (r"'version':\s*'17\.0\.([^']+)'", r"'version': '18.0.\1'"),
            ]
            
            changes_made = []
            
            # Apply version fixes
            for old_pattern, new_pattern in version_replacements:
                matches = re.findall(old_pattern, content)
                if matches:
                    content = re.sub(old_pattern, new_pattern, content)
                    for match in matches:
                        old_version = old_pattern.split(r'\.')[0].split('"')[1] if '"' in old_pattern else old_pattern.split(r'\.')[0].split("'")[1]
                        changes_made.append(f"Updated version: {old_version}.0.{match} -> 18.0.{match}")
            
            # Additional fixes for installable flag
            if 'installable' not in content and '"application"' in content:
                # Add installable flag before the closing brace
                content = re.sub(r'(\s*)(})\s*$', r'\1"installable": True,\n\1\2', content)
                changes_made.append("Added missing 'installable': True")
            
            # Write back if changes were made
            if content != original_content:
                with open(manifest_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"✅ Fixed: {manifest_file.relative_to(self.project_root)}")
                self.fix_report['fixed_files'] += 1
                self.fix_report['changes_made'].append({
                    'file': str(manifest_file.relative_to(self.project_root)),
                    'changes': changes_made
                })
            else:
                logger.info(f"⏭️ No changes needed: {manifest_file.relative_to(self.project_root)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fix {manifest_file}: {str(e)}")
            self.fix_report['failed_files'].append({
                'file': str(manifest_file.relative_to(self.project_root)),
                'error': str(e)
            })
            return False
    
    def run_version_fix(self):
        """Run the complete version fixing process"""
        logger.info("🔧 Starting version fix for remaining Odoo 18 issues...")
        
        # Find problematic manifest files
        problematic_files = self.find_problematic_manifests()
        self.fix_report['total_files'] = len(problematic_files)
        
        logger.info(f"Found {len(problematic_files)} manifest files with version issues")
        
        if not problematic_files:
            logger.info("✅ No version issues found! All manifests are properly updated.")
            return
        
        # Fix each file
        for manifest_file in problematic_files:
            self.fix_manifest_version(manifest_file)
        
        # Generate report
        self.generate_fix_report()
        
        logger.info("🎉 Version fixing completed!")
        logger.info(f"✅ Files processed: {self.fix_report['total_files']}")
        logger.info(f"✅ Files fixed: {self.fix_report['fixed_files']}")
        
        if self.fix_report['failed_files']:
            logger.warning(f"⚠️ Failed files: {len(self.fix_report['failed_files'])}")
    
    def generate_fix_report(self):
        """Generate version fix report"""
        report_file = self.project_root / 'VERSION_FIX_REPORT.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 🔧 Version Fix Report - Odoo 18 Migration\n\n")
            f.write("## 📊 Fix Summary\n\n")
            f.write(f"- **Total Files with Issues:** {self.fix_report['total_files']}\n")
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
            
            f.write("## 🔄 Version Patterns Fixed\n\n")
            f.write("- **14.0.x.x.x** → **18.0.x.x.x**\n")
            f.write("- **15.0.x.x.x** → **18.0.x.x.x**\n")
            f.write("- **16.0.x.x.x** → **18.0.x.x.x**\n")
            f.write("- **17.0.x.x.x** → **18.0.x.x.x**\n")
            f.write("- Added missing **installable: True** flags\n\n")
            
            f.write("---\n")
            f.write("*Version fix completed by roottbar on 2025-01-30*\n")
        
        logger.info(f"📄 Version fix report saved to: {report_file}")

def main():
    """Main execution function"""
    project_root = Path(__file__).parent
    fixer = VersionFixer(project_root)
    fixer.run_version_fix()

if __name__ == "__main__":
    main()
