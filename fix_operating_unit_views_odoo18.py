#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Operating Unit views for Odoo 18 compatibility
Created by: roottbar
Date: 2025-01-30
"""

import os
import re

def fix_operating_unit_view():
    """Fix operating_unit_view.xml for Odoo 18 compatibility"""
    view_file = "operating_unit/view/operating_unit_view.xml"
    
    try:
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace <tree> with <list> for Odoo 18 compatibility
        content = re.sub(r'<tree\s+', '<list ', content)
        content = re.sub(r'</tree>', '</list>', content)
        
        # Update view_mode from tree,form to list,form
        content = re.sub(r'view_mode">tree,form', 'view_mode">list,form', content)
        
        with open(view_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed view file: {view_file}")
        return True
    except Exception as e:
        print(f"Error fixing view file: {e}")
        return False

def fix_res_users_view():
    """Fix res_users_view.xml for Odoo 18 compatibility"""
    view_file = "operating_unit/view/res_users_view.xml"
    
    try:
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if there are any <tree> tags to replace
        if '<tree' in content:
            content = re.sub(r'<tree\s+', '<list ', content)
            content = re.sub(r'</tree>', '</list>', content)
        
        with open(view_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed res_users view file: {view_file}")
        return True
    except Exception as e:
        print(f"Error fixing res_users view file: {e}")
        return False

def main():
    """Fix all operating unit view files for Odoo 18 compatibility"""
    print("Fixing Operating Unit views for Odoo 18 compatibility...")
    
    fixes = [
        fix_operating_unit_view,
        fix_res_users_view
    ]
    
    fixed_count = 0
    for fix_func in fixes:
        if fix_func():
            fixed_count += 1
    
    print(f"Fixed {fixed_count}/{len(fixes)} view files")

if __name__ == "__main__":
    main()
