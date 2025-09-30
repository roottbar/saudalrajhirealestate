#!/usr/bin/env python3
"""
Fix lxml dependency issue for Odoo 15/18 deployment
Saudi Al-Rajhi Real Estate Project

The lxml.html.clean module has been separated into its own package.
This script ensures the correct dependencies are installed.

Author: roottbar <root@tbarholding.com>
Date: 2025-09-30
"""

import subprocess
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_package(package_name):
    """Install a Python package using pip"""
    try:
        logger.info(f"Installing {package_name}...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', package_name], 
                              check=True, capture_output=True, text=True)
        logger.info(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package_name}: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def main():
    """Main function to fix lxml dependency issues"""
    logger.info("=== Saudi Al-Rajhi Real Estate - Fixing lxml Dependencies ===")
    
    packages_to_install = [
        'lxml_html_clean>=0.1.0',
        'lxml[html_clean]',  # Alternative approach
    ]
    
    success_count = 0
    for package in packages_to_install:
        if install_package(package):
            success_count += 1
        
    if success_count > 0:
        logger.info("✅ lxml dependency fix applied successfully!")
        logger.info("📋 You can now restart your Odoo deployment.")
        return 0
    else:
        logger.error("❌ Failed to install required lxml dependencies")
        return 1

if __name__ == "__main__":
    sys.exit(main())
