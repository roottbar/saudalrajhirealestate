#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resolve Git merge conflicts by accepting our Odoo 18.0 changes
Created by: roottbar
Date: 2025-01-30
"""

import os
import re
import glob

def resolve_manifest_conflict(file_path):
    """Resolve merge conflict in manifest file by keeping our Odoo 18.0 version"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove conflict markers and keep our version (the one with 18.0)
        lines = content.split('\n')
        resolved_lines = []
        in_conflict = False
        our_version_found = False
        
        for line in lines:
                our_version_found = True
                continue
                in_conflict = False
                our_version_found = False
                continue
            elif in_conflict and our_version_found:
                resolved_lines.append(line)
            elif not in_conflict:
                # Keep all non-conflict lines
                resolved_lines.append(line)
        
        # Write resolved content
        resolved_content = '\n'.join(resolved_lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(resolved_content)
        
        print(f"Resolved conflict in: {file_path}")
        return True
    except Exception as e:
        print(f"Error resolving {file_path}: {e}")
        return False

def main():
    """Resolve all merge conflicts"""
    print("Resolving merge conflicts...")
    
    # Find all files with conflict markers
    conflict_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()