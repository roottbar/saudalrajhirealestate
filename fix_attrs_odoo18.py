#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix attrs and states attributes for Odoo 18 compatibility
Created by: roottbar
Date: 2025-01-30
"""

import os
import re
import glob

def fix_attrs_in_file(file_path):
    """Fix attrs and states attributes in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix attrs="{'required': [...]}" to required="..."
        content = re.sub(
            r'attrs="\{\'required\':\s*\[([^\]]+)\]\}"',
            r'required="\1"',
            content
        )
        
        # Fix attrs="{'invisible': [...]}" to invisible="..."
        content = re.sub(
            r'attrs="\{\'invisible\':\s*\[([^\]]+)\]\}"',
            r'invisible="\1"',
            content
        )
        
        # Fix attrs="{'readonly': [...]}" to readonly="..."
        content = re.sub(
            r'attrs="\{\'readonly\':\s*\[([^\]]+)\]\}"',
            r'readonly="\1"',
            content
        )
        
        # Fix attrs="{'string': [...]}" to string="..."
        content = re.sub(
            r'attrs="\{\'string\':\s*\[([^\]]+)\]\}"',
            r'string="\1"',
            content
        )
        
        # Fix complex attrs with multiple conditions
        # Pattern: attrs="{'required': [...], 'invisible': [...]}"
        def fix_complex_attrs(match):
            attrs_str = match.group(1)
            # Extract individual conditions
            required_match = re.search(r"'required':\s*\[([^\]]+)\]", attrs_str)
            invisible_match = re.search(r"'invisible':\s*\[([^\]]+)\]", attrs_str)
            readonly_match = re.search(r"'readonly':\s*\[([^\]]+)\]", attrs_str)
            
            result = []
            if required_match:
                result.append(f'required="{required_match.group(1)}"')
            if invisible_match:
                result.append(f'invisible="{invisible_match.group(1)}"')
            if readonly_match:
                result.append(f'readonly="{readonly_match.group(1)}"')
            
            return ' '.join(result)
        
        content = re.sub(
            r'attrs="\{([^}]+)\}"',
            fix_complex_attrs,
            content
        )
        
        # Fix states attribute (deprecated)
        content = re.sub(r'states="[^"]*"', '', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed attrs/states in: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all XML files with attrs and states attributes"""
    print("Fixing attrs and states attributes for Odoo 18 compatibility...")
    
    # Find all XML files
    xml_files = glob.glob("**/*.xml", recursive=True)
    
    fixed_count = 0
    total_files = 0
    
    for xml_file in xml_files:
        if fix_attrs_in_file(xml_file):
            fixed_count += 1
        total_files += 1
    
    print(f"Fixed {fixed_count}/{total_files} XML files")

if __name__ == "__main__":
    main()
