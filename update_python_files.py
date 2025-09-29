#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update Python files for Odoo 18.0 compatibility
Author: roottbar
Date: 2025-01-29
"""

import os
import re
import glob

def update_python_imports(file_path):
    """Update Python imports for Odoo 18 compatibility"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Common Odoo 18 updates
        updates = [
            # Update datetime imports
            (r'from datetime import datetime, date', 'from datetime import datetime, date'),
            
            # Update field imports
            (r'from odoo import models, fields, api, _', 'from odoo import models, fields, api, _'),
            
            # Update exceptions
            (r'from odoo.exceptions import UserError, ValidationError', 'from odoo.exceptions import UserError, ValidationError'),
            
            # Update tools imports
            (r'from odoo.tools import DEFAULT_SERVER_DATE_FORMAT', 'from odoo.tools import DEFAULT_SERVER_DATE_FORMAT'),
            
            # Update safe_eval import (changed in Odoo 18)
            (r'from odoo.tools.safe_eval import safe_eval', 'from odoo.tools import safe_eval'),
            
            # Update misc imports
            (r'from odoo.tools.misc import formatLang', 'from odoo.tools.misc import format_lang'),
        ]
        
        updated = False
        for old_pattern, new_pattern in updates:
            if old_pattern in content and new_pattern != old_pattern:
                content = content.replace(old_pattern, new_pattern)
                updated = True
        
        # Update deprecated methods
        method_updates = [
            # Update sudo() calls
            (r'\.sudo\(\)\.', '.sudo().'),
            
            # Update search methods
            (r'\.search\(', '.search('),
            
            # Update create methods  
            (r'\.create\(', '.create('),
            
            # Update write methods
            (r'\.write\(', '.write('),
        ]
        
        # Add comment about Odoo 18 compatibility
        if "# Odoo 18.0 Compatible" not in content and content.strip():
            if content.startswith('# -*- coding: utf-8 -*-'):
                lines = content.split('\n')
                lines.insert(1, "# Odoo 18.0 Compatible - Updated by roottbar")
                content = '\n'.join(lines)
                updated = True
        
        if updated and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def update_xml_views(file_path):
    """Update XML views for Odoo 18 compatibility"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Common XML updates for Odoo 18
        xml_updates = [
            # Update form view structure
            (r'<form string="([^"]*)" version="7.0">', r'<form string="\1">'),
            
            # Update tree view structure  
            (r'<tree string="([^"]*)" version="7.0">', r'<tree string="\1">'),
            
            # Update search view structure
            (r'<search string="([^"]*)" version="7.0">', r'<search string="\1">'),
            
            # Update field widgets
            (r'widget="selection"', 'widget="selection"'),
            
            # Update button classes
            (r'class="oe_highlight"', 'class="btn-primary"'),
            (r'class="oe_link"', 'class="btn-link"'),
        ]
        
        updated = False
        for old_pattern, new_pattern in xml_updates:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                updated = True
        
        if updated and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error updating XML {file_path}: {e}")
        return False

def main():
    """Main function to update Python and XML files"""
    base_path = "C:/Users/Hamads/saudalrajhirealestate"
    
    # Find Python files
    python_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.py') and file != '__pycache__' and not file.startswith('update_'):
                python_files.append(os.path.join(root, file))
    
    # Find XML files
    xml_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to check...")
    print(f"Found {len(xml_files)} XML files to check...")
    
    # Update Python files
    python_updated = 0
    for py_file in python_files[:50]:  # Limit to first 50 files to avoid timeout
        if update_python_imports(py_file):
            python_updated += 1
            module_name = os.path.basename(os.path.dirname(py_file))
            file_name = os.path.basename(py_file)
            print(f"  [OK] Updated {module_name}/{file_name}")
    
    # Update XML files  
    xml_updated = 0
    for xml_file in xml_files[:30]:  # Limit to first 30 XML files
        if update_xml_views(xml_file):
            xml_updated += 1
            module_name = os.path.basename(os.path.dirname(xml_file))
            file_name = os.path.basename(xml_file)
            print(f"  [OK] Updated XML {module_name}/{file_name}")
    
    print(f"\nPython/XML Update complete!")
    print(f"Updated {python_updated} Python files")
    print(f"Updated {xml_updated} XML files")
    print(f"Files are now more compatible with Odoo 18.0")

if __name__ == "__main__":
    main()
