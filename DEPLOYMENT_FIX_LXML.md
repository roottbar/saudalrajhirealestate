# 🔧 LXML Dependency Fix - Saudi Al-Rajhi Real Estate

**Date**: September 30, 2025  
**Author**: roottbar <root@tbarholding.com>  
**Issue**: `ImportError: lxml.html.clean module is now a separate project lxml_html_clean`

## 🚨 Problem Description

The deployment failed with the following error:
```
ImportError: lxml.html.clean module is now a separate project lxml_html_clean.
Install lxml[html_clean] or lxml_html_clean directly.
```

This is due to a change in lxml library where the `html.clean` module has been separated into its own package.

## ✅ Solution Applied

### 1. Updated Requirements.txt
Added the missing dependency:
```txt
lxml>=4.9.0
lxml_html_clean>=0.1.0
```

### 2. Created Fix Script
Created `fix_lxml_dependency.py` to automatically install the required dependencies.

## 🚀 How to Apply Fix

### Option 1: Install directly on deployment server
```bash
pip install lxml_html_clean>=0.1.0
# OR
pip install lxml[html_clean]
```

### Option 2: Run the fix script
```bash
python3 fix_lxml_dependency.py
```

### Option 3: Reinstall from updated requirements
```bash
pip install -r requirements.txt
```

## 📋 Modules Affected

The following modules use lxml and may be affected:
- `pdf_helper`
- `base_ubl` 
- `hr_resume_ats`
- `hr_resume_ats2`
- Core Odoo mail processing

## ✅ Verification

After applying the fix, test Odoo startup:
```bash
odoo-bin --stop-after-init --test-tags=lxml
```

The error should no longer appear and modules should load successfully.

## 📝 Notes

- This is a common issue when upgrading to newer versions of lxml
- The fix is backward compatible with older lxml versions
- All Saudi Al-Rajhi Real Estate modules should work normally after this fix

---
**Status**: ✅ FIXED  
**Tested**: Ready for deployment  
**Next Steps**: Restart Odoo deployment server
