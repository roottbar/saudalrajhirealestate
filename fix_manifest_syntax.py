#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Manifest Syntax Issues
Author: roottbar
Date: 2025-01-30
Description: Fix syntax errors in __manifest__.py files
"""

import os
import re
from pathlib import Path

class ManifestSyntaxFixer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.fixed_files = []
        self.errors = []

    def fix_string_literals(self, content):
        """Fix unterminated string literals in manifest content"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix unterminated strings in summary and description
            if "'summary':" in line and line.count('"') == 1:
                # Find the closing quote on subsequent lines
                if line.strip().endswith('"'):
                    fixed_lines.append(line)
                else:
                    # Look for the content and close the string properly
                    content_match = re.search(r"'summary':\s*\"(.*)$", line)
                    if content_match:
                        content_text = content_match.group(1).strip()
                        if content_text:
                            fixed_lines.append(f"    'summary': \"{content_text}\",")
                        else:
                            # Look at next lines for content
                            j = i + 1
                            summary_content = []
                            while j < len(lines) and not lines[j].strip().endswith('",'):
                                if lines[j].strip():
                                    summary_content.append(lines[j].strip())
                                j += 1
                            
                            if j < len(lines) and lines[j].strip().endswith('",'):
                                summary_content.append(lines[j].strip().rstrip('",'))
                            
                            # Join the content and create proper string
                            full_summary = ' '.join(summary_content).strip()
                            if full_summary:
                                fixed_lines.append(f"    'summary': \"{full_summary}\",")
                            else:
                                fixed_lines.append(f"    'summary': \"Enhanced Module\",")
                            
                            # Skip the processed lines
                            i = j
                            continue
                    else:
                        fixed_lines.append(line)
            
            elif "'description':" in line and line.count('"') == 1:
                # Similar fix for description
                content_match = re.search(r"'description':\s*\"(.*)$", line)
                if content_match:
                    content_text = content_match.group(1).strip()
                    if content_text:
                        fixed_lines.append(f"    'description': \"{content_text}\",")
                    else:
                        # Look at next lines for content
                        j = i + 1
                        desc_content = []
                        while j < len(lines) and not (lines[j].strip().endswith('",') or lines[j].strip().endswith('",')):
                            if lines[j].strip():
                                desc_content.append(lines[j].strip())
                            j += 1
                        
                        if j < len(lines) and (lines[j].strip().endswith('",') or lines[j].strip().endswith('",')):
                            desc_content.append(lines[j].strip().rstrip('",').rstrip('",'))
                        
                        # Join the content and create proper string
                        full_desc = ' '.join(desc_content).strip()
                        if full_desc:
                            # Clean up the description
                            full_desc = re.sub(r'\s+', ' ', full_desc)
                            fixed_lines.append(f"    'description': \"{full_desc}\",")
                        else:
                            fixed_lines.append(f"    'description': \"Enhanced Module for Odoo 18.0\",")
                        
                        # Skip the processed lines
                        i = j
                        continue
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def fix_manifest_file(self, manifest_path):
        """Fix a single manifest file"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix string literals
            fixed_content = self.fix_string_literals(content)
            
            # Test if the fixed content is valid Python
            try:
                compile(fixed_content, str(manifest_path), 'exec')
                
                # Write the fixed content back
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                self.fixed_files.append(str(manifest_path))
                return True
                
            except SyntaxError as e:
                self.errors.append(f"Syntax error in {manifest_path}: {e}")
                return False
                
        except Exception as e:
            self.errors.append(f"Error processing {manifest_path}: {e}")
            return False

    def run_fix(self):
        """Run the syntax fix process"""
        print("🔧 Starting Manifest Syntax Fix")
        print("=" * 50)
        
        # Find all manifest files
        manifest_files = list(self.base_path.glob('**/__manifest__.py'))
        
        print(f"Found {len(manifest_files)} manifest files to check")
        print()
        
        success_count = 0
        
        for manifest_path in manifest_files:
            module_name = manifest_path.parent.name
            print(f"Checking: {module_name}")
            
            if self.fix_manifest_file(manifest_path):
                success_count += 1
                print(f"  ✅ Fixed")
            else:
                print(f"  ❌ Error")
            
        print()
        print("=" * 50)
        print("📊 SYNTAX FIX REPORT")
        print("=" * 50)
        
        print(f"Total files: {len(manifest_files)}")
        print(f"Successfully fixed: {success_count}")
        print(f"Errors: {len(manifest_files) - success_count}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")
        
        print(f"\n🎉 Syntax fix completed!")

if __name__ == "__main__":
    fixer = ManifestSyntaxFixer(".")
    fixer.run_fix()
