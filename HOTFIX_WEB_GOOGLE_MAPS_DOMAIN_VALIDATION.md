# Hotfix: Web Google Maps Domain Validation Error

## Issue Description
The database initialization was failing with a `TypeError` in the `web_google_maps` module when validating view domains.

### Error Details
```
TypeError: View._validate_domain_identifiers() missing 3 required positional arguments: 'use', 'target_model', and 'node_info'
```

**Location:** `/home/odoo/src/user/web_google_maps/models/ir_ui_view.py`, line 41

**Affected View:** `res_config_settings_view_form` in `web_google_maps/views/res_config_settings.xml`

## Root Cause
The `_validate_domain_identifiers` method in Odoo 18 requires 6 parameters, but the code was only passing 3 parameters:
- **Old call:** `self._validate_domain_identifiers(node, domain, desc)`
- **Required signature:** `self._validate_domain_identifiers(node, domain, desc, use, target_model, node_info)`

## Solution
Updated the method call in `web_google_maps/models/ir_ui_view.py` at line 41-42 to include all required parameters:

```python
fnames, vnames = self._validate_domain_identifiers(
    node, domain, desc, desc, field.comodel_name, node_info
)
```

### Parameters Mapping
1. `node` - The XML node being validated
2. `domain` - The domain string to validate
3. `desc` - Description of the domain for error messages
4. `use` - Usage description (same as `desc`)
5. `target_model` - The comodel name from the field (`field.comodel_name`)
6. `node_info` - Node information dictionary (already available in method scope)

## Files Modified
- `web_google_maps/models/ir_ui_view.py` (1 line changed)

## Verification
✅ Python syntax validation passed for all web_google_maps Python files
✅ XML syntax validation passed for all web_google_maps XML files
✅ No similar issues found in other modules
✅ ks_dashboard_ninja module verified (no issues)

## Testing
All syntax validations completed successfully. The fix aligns with Odoo 18's method signature requirements.

## Related Modules Checked
- ✅ `ks_dashboard_ninja/models/ks_odoo_base.py` - No issues
- ✅ All other modules - No similar validation method overrides found

## Deployment Status
- **Fixed:** 2025-10-05
- **Commit:** 4668cb4
- **Status:** Ready for deployment
