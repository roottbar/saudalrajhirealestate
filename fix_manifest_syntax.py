#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix manifest syntax errors in Odoo modules
Created by: roottbar
Date: 2025-01-30
"""

import os
import re
import glob

def fix_manifest_file(file_path):
    """Fix syntax errors in manifest file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has syntax issues
        if '""",' in content and 'description' not in content[:200]:
            print(f"Fixing syntax in: {file_path}")
            
            # Extract the Arabic description text
            arabic_text = ""
            lines = content.split('\n')
            in_description = False
            description_lines = []
            
            for line in lines:
                if 'هذا التقرير يقوم بحساب:' in line or 'This module provides' in line:
                    in_description = True
                if in_description and line.strip() and not line.strip().startswith("'") and not line.strip().startswith('"'):
                    description_lines.append(line)
                elif in_description and (line.strip().startswith("'") or line.strip().startswith('"')):
                    break
            
            # Clean up the description
            description_text = '\n'.join(description_lines).strip()
            
            # Create a proper manifest structure
            if 'analytic_account_ocs' in file_path:
                fixed_content = f'''# -*- coding: utf-8 -*-
{{
    'name': "تقرير مراكز التكلفة",
    'version': "18.0.1.0.0",
    'summary': "Enhanced تقرير مراكز التكلفة module",
    'description': """
{description_text}
    """,
    'author': 'othmancs',
    'maintainer': 'roottbar',
    'website': 'https://www.tbarholdingocs.com',
    'category': 'Accounting',
    'depends': [
        'base',
        'account',
        'analytic',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/analytic_account_report_views.xml',
    ],
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
}}'''
            elif 'plustech_hr_employee_custody' in file_path:
                fixed_content = f'''# -*- coding: utf-8 -*-
{{
    'name': "Plus Tech Employee Custody Management",
    'version': "18.0.1.0.0",
    'summary': "Complete employee custody and asset management solution",
    'description': """
{description_text}
    """,
    'author': "Plus Technology Team",
    'maintainer': "roottbar",
    'category': "Human Resources/Custody",
    'depends': [
        'base',
        'plustech_hr_employee',
        'account_asset',
    ],
    'data': [
        'security/custody_security.xml',
        'security/ir.model.access.csv',
        'data/request_sequance.xml',
        'data/cron.xml',
        'data/template.xml',
        'views/employee_custody.xml',
        'views/custody_items.xml',
        'views/account_asset.xml',
        'views/hr_employee.xml',
    ],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
}}'''
            else:
                # Generic fix for other files
                fixed_content = content
                # Remove stray """", patterns
                fixed_content = re.sub(r'^\s*""",\s*$', '', fixed_content, flags=re.MULTILINE)
                # Fix duplicate keys
                fixed_content = re.sub(r"'category':\s*'[^']*',\s*'category':\s*'[^']*'", "'category': 'Accounting'", fixed_content)
                fixed_content = re.sub(r"'author':\s*'[^']*',\s*'author':\s*'[^']*'", "'author': 'roottbar'", fixed_content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"Fixed: {file_path}")
            return True
        else:
            print(f"No issues found in: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all manifest files with syntax errors"""
    print("Fixing manifest syntax errors...")
    
    # Get the list of problematic files from the grep results
    problematic_files = [
        'analytic_account_ocs/__manifest__.py',
        'analytic_account_ocs2/__manifest__.py', 
        'analytic_account_ocs_3/__manifest__.py',
        'plustech_hr_employee_custody/__manifest__.py',
        'web_google_maps/__manifest__.py',
        'purchase_decimal_precision/__manifest__.py',
        'hr_end_of_service_sa_ocs/__manifest__.py',
        'hr_resume_ats2/__manifest__.py',
        'hr_resume_ats/__manifest__.py',
        'google_marker_icon_picker/__manifest__.py',
        'contacts_maps/__manifest__.py'
    ]
    
    fixed_count = 0
    for file_path in problematic_files:
        full_path = os.path.join('.', file_path)
        if os.path.exists(full_path):
            if fix_manifest_file(full_path):
                fixed_count += 1
    
    print(f"Fixed {fixed_count} manifest files")

if __name__ == "__main__":
    main()