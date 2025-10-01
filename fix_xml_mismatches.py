#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix XML tag mismatches in Odoo 18 migration
Created by: roottbar
Date: 2025-01-30
"""

import os
import re
import glob

def fix_xml_mismatches_in_file(file_path):
    """Fix XML tag mismatches in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix mismatched tree/list tags
        # Pattern 1: <tree> ... </list>
        content = re.sub(r'<tree>([^<]*(?:<[^/][^>]*>[^<]*)*)</list>', r'<list>\1</list>', content, flags=re.DOTALL)
        
        # Pattern 2: </tree> ... <list>
        content = re.sub(r'</tree>([^<]*(?:<[^/][^>]*>[^<]*)*)<list>', r'</list>\1<list>', content, flags=re.DOTALL)
        
        # Pattern 3: Mixed tree/list in same line
        content = re.sub(r'<tree>([^<]*)</list>', r'<list>\1</list>', content)
        content = re.sub(r'</tree>([^<]*)<list>', r'</list>\1<list>', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed mismatches in: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all XML files with tag mismatches"""
    print("Fixing XML tag mismatches for Odoo 18 compatibility...")
    
    # Find all XML files
    xml_files = glob.glob("**/*.xml", recursive=True)
    
    fixed_count = 0
    total_files = 0
    
    for xml_file in xml_files:
        if fix_xml_mismatches_in_file(xml_file):
            fixed_count += 1
        total_files += 1
    
    print(f"Fixed {fixed_count}/{total_files} XML files")

if __name__ == "__main__":
    main()
