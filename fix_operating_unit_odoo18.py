#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Operating Unit module for Odoo 18 compatibility
Created by: roottbar
Date: 2025-01-30
"""

import os
import re

def fix_operating_unit_security():
    """Fix security file for Odoo 18 compatibility"""
    security_file = "operating_unit/security/operating_unit_security.xml"
    
    try:
        with open(security_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix company_ids reference for Odoo 18
        content = re.sub(
            r"'company_ids'",
            "'allowed_company_ids'",
            content
        )
        
        with open(security_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed security file: {security_file}")
        return True
    except Exception as e:
        print(f"Error fixing security file: {e}")
        return False

def fix_operating_unit_model():
    """Fix operating unit model for Odoo 18 compatibility"""
    model_file = "operating_unit/models/operating_unit.py"
    
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix name_search method for Odoo 18
        # Replace the deprecated name_search with _name_search
        content = re.sub(
            r'@api\.model\s+def name_search\(self, name="", args=None, operator="ilike", limit=100\):',
            '@api.model\ndef _name_search(self, name="", args=None, operator="ilike", limit=100):',
            content
        )
        
        # Update the super call
        content = re.sub(
            r'names1 = super\(models\.Model, self\)\.name_search\(',
            'names1 = super()._name_search(',
            content
        )
        
        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed model file: {model_file}")
        return True
    except Exception as e:
        print(f"Error fixing model file: {e}")
        return False

def fix_res_users_model():
    """Fix res.users model for Odoo 18 compatibility"""
    model_file = "operating_unit/models/res_users.py"
    
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix _uid reference for Odoo 18
        content = re.sub(
            r'self\._uid',
            'self.env.uid',
            content
        )
        
        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed res.users model file: {model_file}")
        return True
    except Exception as e:
        print(f"Error fixing res.users model file: {e}")
        return False

def fix_test_file():
    """Fix test file for Odoo 18 compatibility"""
    test_file = "operating_unit/tests/test_operating_unit.py"
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix super() call for Odoo 18
        content = re.sub(
            r'super\(TestOperatingUnit, self\)\.setUp\(\)',
            'super().setUp()',
            content
        )
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed test file: {test_file}")
        return True
    except Exception as e:
        print(f"Error fixing test file: {e}")
        return False

def main():
    """Fix all operating unit files for Odoo 18 compatibility"""
    print("Fixing Operating Unit module for Odoo 18 compatibility...")
    
    fixes = [
        fix_operating_unit_security,
        fix_operating_unit_model,
        fix_res_users_model,
        fix_test_file
    ]
    
    fixed_count = 0
    for fix_func in fixes:
        if fix_func():
            fixed_count += 1
    
    print(f"Fixed {fixed_count}/{len(fixes)} files")

if __name__ == "__main__":
    main()
