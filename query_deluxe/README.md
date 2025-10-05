# PostgreSQL Query Deluxe - Development Tool

## ⚠️ CRITICAL SECURITY WARNING ⚠️

**This module is designed for DEVELOPMENT and DEBUGGING purposes ONLY.**

**DO NOT install this module in production environments or on Odoo.sh!**

## What This Module Does

PostgreSQL Query Deluxe allows users to execute raw PostgreSQL queries directly from the Odoo web interface. While this can be useful for debugging and development, it presents significant security risks.

## Security Risks

### 1. **Bypasses Odoo Security**
- Direct database access ignores Odoo's record rules and access rights
- Users with access can view/modify any data in the database
- Circumvents multi-company and data isolation controls

### 2. **Data Exposure**
- Can expose sensitive information (passwords, financial data, personal info)
- Example queries include accessing `pg_user` and system catalogs
- No audit trail for data accessed via raw queries

### 3. **Destructive Operations**
- Allows DELETE, DROP, ALTER, and other destructive SQL commands
- Can accidentally or maliciously delete critical data
- Can modify database structure (ALTER TABLE, DROP TABLE)
- Example queries include operations like `DROP TABLE mytable`

### 4. **Odoo.sh Compatibility Issues**
- Odoo.sh has security policies that may block or flag this module
- Direct database access violates managed hosting best practices
- May cause deployment failures or security alerts

## When to Use This Module

### ✅ Acceptable Use Cases (Development Only)
- Local development environment for debugging
- Testing SQL queries before implementing in code
- Database analysis and troubleshooting
- Learning PostgreSQL and Odoo database structure

### ❌ Never Use For
- Production environments
- Odoo.sh or any managed hosting
- Multi-user/client environments
- Any system with sensitive data

## Installation

### Current Status
By default, this module is **disabled** (`installable = False` in `__manifest__.py`).

### To Enable (Development Only)

1. **Ensure you are in a local development environment**
2. Edit `query_deluxe/__manifest__.py`
3. Change `'installable': False` to `'installable': True`
4. Restart Odoo
5. Install the module from Apps menu

### For Odoo.sh Deployments

**Keep the module disabled!** The manifest is configured with `installable: False` to prevent installation.

## Usage

Once enabled in a development environment:

1. Navigate to **Query Deluxe** menu
2. Type your SQL query in the text field
3. Click **Execute** to run the query
4. View results in table format

### Available Features
- Execute SELECT queries and view results
- Run UPDATE, INSERT, DELETE statements
- Access PostgreSQL system catalogs
- Export results to PDF
- Save frequently used queries as examples

## Best Practices

### If You Must Use This Module

1. **Only in Development**: Never enable in production
2. **Backup First**: Always have recent backups before running queries
3. **Test Queries**: Test on non-production data first
4. **Read-Only Preferred**: Use SELECT queries when possible
5. **Limit Access**: Restrict to system administrators only
6. **Review Examples**: Remove dangerous example queries from `datas/data.xml`

### Recommended Alternatives

Instead of this module, consider:

- **Odoo ORM**: Use Python code with proper ORM methods
- **Database Views**: Create safe, read-only views
- **Studio**: Use Odoo Studio for data exploration
- **Reports**: Build proper reports with access controls
- **pgAdmin/DBeaver**: Use external tools for database management

## For Administrators

### Removing Dangerous Examples

The module includes example queries that can be dangerous. To remove them:

```bash
# Remove or comment out dangerous examples in:
query_deluxe/datas/data.xml
```

Consider removing examples that include:
- `UPDATE res_users SET password` (line 33-36)
- `DELETE FROM` operations (line 43-46)
- `ALTER DATABASE` operations (line 63-66)
- `DROP TABLE` operations (line 68-71)

### Access Control

The module is restricted to the "Access query_deluxe" group, which is auto-assigned to System administrators. Consider:

1. Creating a separate development-only database
2. Using environment variables to completely disable in production
3. Adding code checks to prevent execution on specific environments

## Technical Details

- **Model**: `querydeluxe`
- **Dependencies**: `base`, `mail`
- **Access Group**: `group_query_deluxe` (implied by `base.group_system`)
- **Version**: 18.0.1.0.0
- **License**: LGPL-3

## Support and Contact

- Original Author: Yvan Dotet (yvandotet@yahoo.fr)
- Original Repository: https://github.com/YvanDotet/query_deluxe
- Maintainer: roottbar

## Disclaimer

This module is provided "as is" without any warranty. The maintainers are not responsible for any data loss, security breaches, or other issues resulting from the use of this module.

**By enabling this module, you acknowledge the security risks and accept full responsibility for its use.**

## Odoo.sh Deployment Checklist

Before deploying to Odoo.sh:

- [x] Verify `installable: False` in `__manifest__.py`
- [x] Confirm module is not listed in auto-install modules
- [x] Test deployment without the module enabled
- [ ] Document that this module should remain disabled
- [ ] Train team on security implications

---

**Remember: This is a powerful tool that requires responsible use. When in doubt, keep it disabled!**
