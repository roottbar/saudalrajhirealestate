#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix all <tree> tags to <list> for Odoo 18 compatibility
Created by: roottbar
Date: 2025-01-30
"""

import os
import re
import glob

def fix_tree_tags_in_file(file_path):
    """Fix <tree> tags to <list> in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace <tree> with <list> for Odoo 18 compatibility
        content = re.sub(r'<tree\s+', '<list ', content)
        content = re.sub(r'</tree>', '</list>', content)
        
        # Update view_mode from tree,form to list,form
        content = re.sub(r'view_mode">tree,form', 'view_mode">list,form', content)
        content = re.sub(r'view_mode">tree,form,', 'view_mode">list,form,', content)
        content = re.sub(r'view_mode">tree,', 'view_mode">list,', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all XML files with <tree> tags for Odoo 18 compatibility"""
    print("Fixing all <tree> tags to <list> for Odoo 18 compatibility...")
    
    # Find all XML files
    xml_files = glob.glob("**/*.xml", recursive=True)
    
    fixed_count = 0
    total_files = 0
    
    for xml_file in xml_files:
        if fix_tree_tags_in_file(xml_file):
            fixed_count += 1
        total_files += 1
    
    print(f"Fixed {fixed_count}/{total_files} XML files")

if __name__ == "__main__":
    main()
