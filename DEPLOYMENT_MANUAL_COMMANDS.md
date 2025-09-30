# 🚀 DEPLOYMENT SERVER MANUAL FIX COMMANDS

**Run these commands on your deployment server (Linux) to fix all issues:**

## Option 1: Automated Script (Recommended)

```bash
# Copy the deployment script to your server and run it
chmod +x DEPLOYMENT_SERVER_FIX.sh
./DEPLOYMENT_SERVER_FIX.sh
```

## Option 2: Manual Commands (Step by Step)

### Step 1: Navigate to Modules Directory
```bash
cd /home/odoo/src/user
pwd  # Should show: /home/odoo/src/user
```

### Step 2: Pull Latest Fixes from GitHub
```bash
git status
git pull origin Update_Odoo_2025
```

### Step 3: If Git Pull Fails - Apply Manual Fix
```bash
# Backup the original file
cp report_xlsx/controllers/main.py report_xlsx/controllers/main.py.backup

# Apply the critical fix
sed -i 's/from odoo.addons.web.controllers.report import ReportController as BaseReportController/from odoo.addons.web.controllers.main import ReportController as BaseReportController/g' report_xlsx/controllers/main.py

# Verify the fix worked
grep "from odoo.addons.web.controllers.main import ReportController" report_xlsx/controllers/main.py
```

### Step 4: Install Missing Python Dependency
```bash
# Install the missing lxml dependency
pip install lxml_html_clean>=0.1.0

# If pip doesn't work, try pip3
pip3 install lxml_html_clean>=0.1.0
```

### Step 5: Restart Odoo Service
**Choose ONE of these commands based on your setup:**

```bash
# Option A: systemd (most common)
sudo systemctl restart odoo
sudo systemctl status odoo

# Option B: service command
sudo service odoo restart
sudo service odoo status

# Option C: supervisor
sudo supervisorctl restart odoo
sudo supervisorctl status odoo

# Option D: Direct process kill/restart (if others don't work)
pkill -f odoo-bin
# Then start your Odoo service normally
```

### Step 6: Test Your Deployment
```bash
# Run your original odoo command
odoo-bin --stop-after-init --log-db rajhirealestateodoo-saudalrajhirealestate-update-od-24172634 --http-interface=127.0.0.1 -u bstt_hr_attendance,material_purchase_requisitions,hr_advanced,hr_attendance_multi_company,hr_zk_attendance,account_tax_balance,mis_builder,account_financial_report_sale,print_journal_entries,account_financial_report,cr_activity_report,bstt_remove_analytic_account,partner_statement,hr_end_of_service,bstt_account_report_levels,date_range,report_xlsx_helper,bstt_ksa_ninja_dashboard_back_button,customer_tickets,web_google_maps,analytic_invoice_journal_ocs,ks_dn_advance,query_deluxe,report_xlsx,user_action_rule,purchase_request,purchase_discount,ks_dashboard_ninja,bstt_hr,hr_loan,bstt_hr_payroll_analytic_account_new,bstt_account_invoice,bstt_hr_payroll_analytic_account,bstt_finger_print,bstt_partner,renting,bstt_finanical_report,plustech_asset_enhance,rent_customize,bstt_account_operating_unit_sequence --without-demo=all
```

## ✅ Expected Results After Fix:

- ❌ **No more**: `ModuleNotFoundError: No module named 'odoo.addons.web.controllers.report'`
- ❌ **No more**: `ImportError: lxml.html.clean module is now a separate project`
- ❌ **No more**: `At least one test failed when loading the modules (date_range)`
- ✅ **See**: `Module date_range loaded in X.XXs`
- ✅ **See**: `Module report_xlsx loaded successfully`
- ✅ **See**: `loading 299 modules...` (all modules loading)

## 🔍 Troubleshooting:

### If the fix doesn't work:
1. **Check file paths**: Make sure you're in `/home/odoo/src/user`
2. **Check permissions**: You may need `sudo` for some commands
3. **Check Odoo path**: Your Odoo might be in a different directory
4. **Check Python version**: Try `python3` instead of `python`

### Common Odoo installation paths:
- `/home/odoo/src/user/` (your setup)
- `/opt/odoo/addons/`
- `/usr/lib/python3/site-packages/odoo/addons/`
- `/var/lib/odoo/`

---

**🎯 Result**: Your Saudi Al-Rajhi Real Estate Odoo 15 system will deploy successfully with all critical errors resolved!
