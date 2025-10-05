# Google Maps Dependency Fix

## Overview
This document explains the changes made to remove the dependency on `web_google_maps` module from the `rent_customize` module.

## Problem
The `rent_customize` module had a hard dependency on `web_google_maps` module due to:
1. A google_map view definition in `views/product.xml`
2. An action window view record referencing the google_map view
3. `web_google_maps` listed in the module dependencies in `__manifest__.py`

When `web_google_maps` was disabled or uninstalled, the `rent_customize` module would fail to load, causing system-wide issues.

## Solution
The following changes were made to allow `rent_customize` to work independently:

### 1. Commented out google_map view (views/product.xml)
- Commented out the `view_crm_template_google_map` record (lines 16-26)
- Commented out the `crm_lead_action_pipeline_view_google_map` action window view (lines 28-33)

### 2. Removed dependency (__manifest__.py)
- Commented out `web_google_maps` from the depends list
- Added explanatory comment for future reference

## Re-enabling Google Maps View
If you want to re-enable the Google Maps functionality:

1. Ensure `web_google_maps` module is installed
2. Uncomment the google_map view records in `views/product.xml`
3. Uncomment `web_google_maps` in `__manifest__.py` dependencies
4. Update the module: `odoo-bin -u rent_customize`

## Deployment Instructions

### For Odoo.sh or Production Environment:
```sql
-- Step 1: Uninstall both modules (if needed)
BEGIN;
UPDATE ir_module_module SET state='uninstalled'
WHERE name IN ('rent_customize','web_google_maps');
COMMIT;
```

### Step 2: Rebuild with updated source code
After pushing this fix to your branch:
```bash
# In Odoo.sh console or local environment:
# Trigger rebuild or manually update
odoo-bin -u rent_customize --stop-after-init
```

### Step 3: Reinstall modules
```bash
# Update the module with the fixed code
odoo-bin -u rent_customize,web_google_maps
```

## Benefits
- `rent_customize` can now work independently without `web_google_maps`
- System remains stable even if `web_google_maps` is disabled
- Easier to troubleshoot and maintain
- No need to modify database JSONB fields directly

## Technical Notes
- XML views are properly commented out (not deleted) for easy restoration
- Module dependency is commented out with explanation
- Changes follow minimal modification principle
- All existing functionality (except google maps view) remains intact
