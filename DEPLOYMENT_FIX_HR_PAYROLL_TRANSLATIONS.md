# 🔧 HR Payroll & Translation Fixes - Saudi Al-Rajhi Real Estate

**Date**: September 30, 2025  
**Author**: roottbar <root@tbarholding.com>  
**Issues**: 
1. `TypeError: Model 'hr.payslip' does not exist in registry`
2. `OSError: Syntax error in po file (line 92)`

## 🚨 Problem Description

### Issue #5: Missing HR Payroll Module
```
TypeError: Model 'hr.payslip' does not exist in registry.
```

Multiple modules depend on `hr_payroll`, but the core Odoo payroll module isn't installed.

**Affected Modules:**
- l10n_sa_hr_payroll (Saudi Payroll Localization)
- bstt_hr_payroll_analytic_account
- bstt_hr_payroll_analytic_account_new
- plustech_hr_attendance_transaction
- hr_overtime
- hr_loan
- hr_bonus_deduction
- hr_advanced
- bstt_hr
- contracts_management

### Issue #6: Corrupted Arabic Translation File
```
OSError: Syntax error in po file (line 92)
couldn't read translation file [lang: ar_001][format: po]
```

One of the Arabic translation files has a syntax error.

## ✅ Solutions

### Solution #5: Install HR Payroll or Disable Payroll Modules

**Option A: Install hr_payroll (Recommended for Production)**
Add to `requirements.txt` or install via Apps:
```python
# In __manifest__.py files, ensure hr_payroll is available
# Or install: odoo.com/apps/modules/hr_payroll
```

**Option B: Temporarily Disable Payroll Modules**
Set `'installable': False` in these module manifests:
- l10n_sa_hr_payroll
- bstt_hr_payroll_analytic_account
- bstt_hr_payroll_analytic_account_new

### Solution #6: Fix or Skip Broken Translation Files

**Temporary Fix (Skip Arabic translations during deployment):**
Use `--load-language=en_US` flag when starting Odoo

**Permanent Fix:**
Identify and fix the corrupted .po file at line 92

## 🚀 Deployment Workaround

### Quick Fix: Disable Payroll-Dependent Modules Temporarily

Since hr_payroll is an enterprise/paid module, temporarily mark payroll-related modules as not installable:

1. In `l10n_sa_hr_payroll/__manifest__.py`: Set `'installable': False`
2. In `bstt_hr_payroll_analytic_account/__manifest__.py`: Set `'installable': False`
3. In `bstt_hr_payroll_analytic_account_new/__manifest__.py`: Set `'installable': False`

This allows the system to deploy without payroll functionality. Re-enable after installing hr_payroll.

## 📋 Module Dependency Analysis

**Modules needing hr_payroll:**
```
l10n_sa_hr_payroll → depends: ['hr_payroll']
bstt_hr_payroll_analytic_account → depends: ['hr_payroll_account']
plustech_hr_attendance_transaction → depends: hr_payroll
```

**Resolution Options:**
1. Install Odoo Enterprise hr_payroll module
2. Install community hr_payroll alternative  
3. Temporarily disable payroll modules

---
**Status**: 🔍 ANALYSIS COMPLETE  
**Recommended Action**: Install hr_payroll or disable dependent modules  
**Priority**: Medium (doesn't block non-payroll functionality)
