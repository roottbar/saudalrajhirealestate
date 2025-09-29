#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update all Odoo modules to version 18.0
Author: roottbar
Date: 2025-01-29
"""

import os
import re
import glob

def update_manifest_version(file_path):
    """Update version in __manifest__.py file to 18.0"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update version patterns
        patterns = [
            (r"'version'\s*:\s*['\"]15\.0\.\d+\.\d+\.\d+['\"]", "'version': '18.0.1.0.0'"),
            (r"'version'\s*:\s*['\"]16\.0\.\d+\.\d+\.\d+['\"]", "'version': '18.0.1.0.0'"),
            (r"'version'\s*:\s*['\"]17\.0\.\d+\.\d+\.\d+['\"]", "'version': '18.0.1.0.0'"),
            (r'"version"\s*:\s*[\'"]15\.0\.\d+\.\d+\.\d+[\'"]', '"version": "18.0.1.0.0"'),
            (r'"version"\s*:\s*[\'"]16\.0\.\d+\.\d+\.\d+[\'"]', '"version": "18.0.1.0.0"'),
            (r'"version"\s*:\s*[\'"]17\.0\.\d+\.\d+\.\d+[\'"]', '"version": "18.0.1.0.0"'),
        ]
        
        updated = False
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                updated = True
        
        # Add maintainer if not exists
        if "'maintainer'" not in content and '"maintainer"' not in content:
            # Find author line and add maintainer after it
            author_pattern = r"(\s*'author'\s*:\s*[^,]+,)"
            if re.search(author_pattern, content):
                content = re.sub(author_pattern, r"\1\n    'maintainer': 'roottbar',", content)
                updated = True
        
        # Update description to mention Odoo 18.0 - 2025 Edition
        if "2025 Edition" not in content:
            desc_pattern = r"('description'\s*:\s*['\"])(.*?)(['\"])"
            match = re.search(desc_pattern, content, re.DOTALL)
            if match:
                desc_content = match.group(2)
                if "Updated for Odoo 18.0 - 2025 Edition" not in desc_content:
                    new_desc = desc_content.rstrip() + "\n        \n        Updated for Odoo 18.0 - 2025 Edition"
                    content = re.sub(desc_pattern, r"\1" + new_desc + r"\3", content, flags=re.DOTALL)
                    updated = True
        
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all manifest files"""
    base_path = "C:/Users/Hamads/saudalrajhirealestate"
    manifest_files = glob.glob(os.path.join(base_path, "**/__manifest__.py"), recursive=True)
    
    updated_count = 0
    total_count = len(manifest_files)
    
    print(f"Found {total_count} manifest files to update...")
    
    for manifest_file in manifest_files:
        module_name = os.path.basename(os.path.dirname(manifest_file))
        print(f"Updating {module_name}...")
        
        if update_manifest_version(manifest_file):
            updated_count += 1
            print(f"  [OK] Updated {module_name}")
        else:
            print(f"  [SKIP] Skipped {module_name} (no changes needed)")
    
    print(f"\nUpdate complete!")
    print(f"Updated {updated_count} out of {total_count} modules")
    print(f"All modules are now ready for Odoo 18.0 - 2025 Edition")

if __name__ == "__main__":
    main()
