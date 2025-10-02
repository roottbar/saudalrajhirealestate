# ===================================================================
# Odoo Module Inconsistency Fix Script
# ===================================================================
# This script fixes the inconsistent states of einv_sa and ejar_integration modules
# by performing a complete cleanup and reinstallation process.

Write-Host "=== Odoo Module Inconsistency Fix Script ===" -ForegroundColor Green
Write-Host "Fixing modules: einv_sa, ejar_integration" -ForegroundColor Yellow

# Configuration
$ODOO_SERVICE = "odoo"
$DB_NAME = "rajhirealestateodoo"
$ODOO_USER = "odoo"
$ODOO_PASSWORD = "admin"
$ODOO_HOST = "localhost"
$ODOO_PORT = "8069"

# Step 1: Stop Odoo Service
Write-Host "`n[1/7] Stopping Odoo service..." -ForegroundColor Cyan
try {
    Stop-Service -Name $ODOO_SERVICE -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Odoo service stopped successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ Warning: Could not stop Odoo service automatically" -ForegroundColor Yellow
    Write-Host "Please stop Odoo manually before continuing..." -ForegroundColor Red
    Read-Host "Press Enter when Odoo is stopped"
}

# Step 2: Clean Python cache files
Write-Host "`n[2/7] Cleaning Python cache files..." -ForegroundColor Cyan
$currentDir = Get-Location
Get-ChildItem -Path $currentDir -Recurse -Include "*.pyc" | Remove-Item -Force
Get-ChildItem -Path $currentDir -Recurse -Directory -Name "__pycache__" | ForEach-Object {
    Remove-Item -Path (Join-Path $currentDir $_) -Recurse -Force
}
Write-Host "✓ Python cache files cleaned" -ForegroundColor Green

# Step 3: Database cleanup commands
Write-Host "`n[3/7] Preparing database cleanup commands..." -ForegroundColor Cyan
$dbCleanupCommands = @"
-- Remove module records and dependencies
DELETE FROM ir_module_module_dependency WHERE name IN ('einv_sa', 'ejar_integration');
DELETE FROM ir_module_module WHERE name IN ('einv_sa', 'ejar_integration');

-- Clean model and field records
DELETE FROM ir_model_fields WHERE model LIKE 'ejar.%';
DELETE FROM ir_model WHERE model LIKE 'ejar.%';

-- Clean access control records
DELETE FROM ir_model_access WHERE perm_model LIKE 'model_ejar_%';
DELETE FROM res_groups_users_rel WHERE gid IN (
    SELECT id FROM res_groups WHERE category_id IN (
        SELECT id FROM ir_module_category WHERE name LIKE '%ejar%'
    )
);
DELETE FROM res_groups WHERE category_id IN (
    SELECT id FROM ir_module_category WHERE name LIKE '%ejar%'
);
DELETE FROM ir_module_category WHERE name LIKE '%ejar%';

-- Clean menu items
DELETE FROM ir_ui_menu WHERE name LIKE '%Ejar%' OR name LIKE '%ejar%';

-- Clean views and actions
DELETE FROM ir_ui_view WHERE name LIKE '%ejar%';
DELETE FROM ir_actions_act_window WHERE name LIKE '%ejar%';

-- Clean sequence and cron records
DELETE FROM ir_sequence WHERE name LIKE '%ejar%';
DELETE FROM ir_cron WHERE name LIKE '%ejar%';

-- Reset module states
UPDATE ir_module_module SET state = 'uninstalled' WHERE name IN ('einv_sa', 'ejar_integration');

-- Commit changes
COMMIT;
"@

Write-Host "✓ Database cleanup commands prepared" -ForegroundColor Green

# Step 4: Create database cleanup script
$dbScriptPath = Join-Path $currentDir "db_cleanup.sql"
$dbCleanupCommands | Out-File -FilePath $dbScriptPath -Encoding UTF8
Write-Host "✓ Database cleanup script created: $dbScriptPath" -ForegroundColor Green

# Step 5: Display manual database cleanup instructions
Write-Host "`n[4/7] Database Cleanup Required" -ForegroundColor Cyan
Write-Host "Please execute the following database cleanup manually:" -ForegroundColor Yellow
Write-Host "1. Connect to PostgreSQL database: $DB_NAME" -ForegroundColor White
Write-Host "2. Execute the SQL script: $dbScriptPath" -ForegroundColor White
Write-Host "3. Or run these commands in psql:" -ForegroundColor White
Write-Host "   psql -U postgres -d $DB_NAME -f `"$dbScriptPath`"" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter after completing database cleanup"

# Step 6: Start Odoo and install modules
Write-Host "`n[5/7] Starting Odoo service..." -ForegroundColor Cyan
try {
    Start-Service -Name $ODOO_SERVICE
    Write-Host "✓ Odoo service started" -ForegroundColor Green
} catch {
    Write-Host "⚠ Warning: Could not start Odoo service automatically" -ForegroundColor Yellow
    Write-Host "Please start Odoo manually..." -ForegroundColor Red
}

# Wait for Odoo to start
Write-Host "`n[6/7] Waiting for Odoo to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Step 7: Module installation commands
Write-Host "`n[7/7] Module Installation Commands" -ForegroundColor Cyan
Write-Host "Execute these commands to reinstall modules:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Install einv_sa first:" -ForegroundColor White
Write-Host "   odoo-bin -d $DB_NAME -i einv_sa --stop-after-init" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Install ejar_integration second:" -ForegroundColor White
Write-Host "   odoo-bin -d $DB_NAME -i ejar_integration --stop-after-init" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Update both modules:" -ForegroundColor White
Write-Host "   odoo-bin -d $DB_NAME -u einv_sa,ejar_integration --stop-after-init" -ForegroundColor Gray
Write-Host ""

# Final verification steps
Write-Host "`nFinal Verification Steps:" -ForegroundColor Green
Write-Host "1. Check Odoo logs for any errors" -ForegroundColor White
Write-Host "2. Verify modules are installed in Apps menu" -ForegroundColor White
Write-Host "3. Test basic functionality of both modules" -ForegroundColor White
Write-Host "4. Monitor system performance and memory usage" -ForegroundColor White

Write-Host "`n=== Script Completed ===" -ForegroundColor Green
Write-Host "The inconsistent module states should now be resolved." -ForegroundColor Yellow
Write-Host "If issues persist, check the MODULE_REINSTALL_GUIDE.md for detailed steps." -ForegroundColor Cyan

# Keep window open
Read-Host "`nPress Enter to exit"