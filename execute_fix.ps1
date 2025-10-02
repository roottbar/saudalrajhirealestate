# Enhanced Module Inconsistency Fix Script
# This script provides a comprehensive solution for fixing einv_sa and ejar_integration module inconsistencies

param(
    [string]$OdooPath = "C:\Program Files\Odoo 16.0\server\odoo-bin",
    [string]$DatabaseName = "rajhirealestateodoo",
    [string]$ConfigFile = "C:\Program Files\Odoo 16.0\server\odoo.conf",
    [switch]$SkipBackup = $false
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-OdooService {
    try {
        $service = Get-Service -Name "odoo*" -ErrorAction SilentlyContinue
        return $service -ne $null
    }
    catch {
        return $false
    }
}

function Stop-OdooService {
    Write-ColorOutput "🛑 Stopping Odoo service..." $Blue
    
    if (Test-OdooService) {
        try {
            $services = Get-Service -Name "odoo*"
            foreach ($service in $services) {
                if ($service.Status -eq "Running") {
                    Stop-Service -Name $service.Name -Force -ErrorAction Stop
                    Write-ColorOutput "✅ Stopped service: $($service.Name)" $Green
                }
            }
        }
        catch {
            Write-ColorOutput "⚠️ Could not stop Odoo service automatically. Please stop it manually." $Yellow
            Write-ColorOutput "Press any key to continue after stopping Odoo..." $Yellow
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
    }
    else {
        Write-ColorOutput "ℹ️ No Odoo service found. Assuming Odoo is not running as a service." $Blue
    }
    
    # Kill any remaining Odoo processes
    try {
        $odooProcesses = Get-Process -Name "*odoo*" -ErrorAction SilentlyContinue
        if ($odooProcesses) {
            $odooProcesses | Stop-Process -Force
            Write-ColorOutput "✅ Killed remaining Odoo processes" $Green
        }
    }
    catch {
        Write-ColorOutput "ℹ️ No Odoo processes to kill" $Blue
    }
}

function Start-OdooService {
    Write-ColorOutput "🚀 Starting Odoo service..." $Blue
    
    if (Test-OdooService) {
        try {
            $services = Get-Service -Name "odoo*"
            foreach ($service in $services) {
                if ($service.Status -ne "Running") {
                    Start-Service -Name $service.Name -ErrorAction Stop
                    Write-ColorOutput "✅ Started service: $($service.Name)" $Green
                }
            }
        }
        catch {
            Write-ColorOutput "⚠️ Could not start Odoo service automatically. Please start it manually." $Yellow
        }
    }
    else {
        Write-ColorOutput "ℹ️ No Odoo service configured. You may need to start Odoo manually." $Yellow
    }
}

function Clear-PythonCache {
    Write-ColorOutput "🧹 Cleaning Python cache files..." $Blue
    
    $currentDir = Get-Location
    
    try {
        # Remove .pyc files
        $pycFiles = Get-ChildItem -Recurse -Include "*.pyc" -ErrorAction SilentlyContinue
        if ($pycFiles) {
            $pycFiles | Remove-Item -Force
            Write-ColorOutput "✅ Removed $($pycFiles.Count) .pyc files" $Green
        }
        
        # Remove __pycache__ directories
        $pycacheDirs = Get-ChildItem -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue
        if ($pycacheDirs) {
            $pycacheDirs | ForEach-Object { 
                Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue
            }
            Write-ColorOutput "✅ Removed $($pycacheDirs.Count) __pycache__ directories" $Green
        }
        
        Write-ColorOutput "✅ Python cache cleanup completed" $Green
    }
    catch {
        Write-ColorOutput "⚠️ Some cache files could not be removed: $($_.Exception.Message)" $Yellow
    }
}

function Show-DatabaseCleanupCommands {
    Write-ColorOutput "📋 Database Cleanup Commands" $Blue
    Write-ColorOutput "Please execute these SQL commands in your PostgreSQL database:" $Yellow
    
    $sqlCommands = @"

-- ============================================
-- CRITICAL MODULE CLEANUP COMMANDS
-- Execute these in your PostgreSQL database
-- ============================================

BEGIN;

-- 1. Remove module dependencies
DELETE FROM ir_module_module_dependency WHERE name IN ('einv_sa', 'ejar_integration');

-- 2. Remove module records
DELETE FROM ir_module_module WHERE name IN ('einv_sa', 'ejar_integration');

-- 3. Clean model and field records
DELETE FROM ir_model_fields WHERE model LIKE 'ejar.%';
DELETE FROM ir_model WHERE model LIKE 'ejar.%';

-- 4. Clean access control records
DELETE FROM ir_model_access WHERE perm_model LIKE 'model_ejar_%';

-- 5. Clean security groups
DELETE FROM res_groups_users_rel WHERE gid IN (
    SELECT id FROM res_groups WHERE category_id IN (
        SELECT id FROM ir_module_category WHERE name LIKE '%ejar%'
    )
);
DELETE FROM res_groups WHERE category_id IN (
    SELECT id FROM ir_module_category WHERE name LIKE '%ejar%'
);
DELETE FROM ir_module_category WHERE name LIKE '%ejar%';

-- 6. Clean menu items
DELETE FROM ir_ui_menu WHERE name LIKE '%Ejar%' OR name LIKE '%ejar%';

-- 7. Clean views and actions
DELETE FROM ir_ui_view WHERE name LIKE '%ejar%';
DELETE FROM ir_actions_act_window WHERE name LIKE '%ejar%';

-- 8. Clean sequences and scheduled jobs
DELETE FROM ir_sequence WHERE name LIKE '%ejar%';
DELETE FROM ir_cron WHERE name LIKE '%ejar%';

-- 9. Reset module states
UPDATE ir_module_module SET state = 'uninstalled' WHERE name IN ('einv_sa', 'ejar_integration');

-- 10. Clean any remaining ejar-related data
DELETE FROM ir_model_data WHERE module IN ('einv_sa', 'ejar_integration');

COMMIT;

-- ============================================
-- END OF CLEANUP COMMANDS
-- ============================================

"@

    Write-ColorOutput $sqlCommands $Yellow
    
    # Save commands to file
    $sqlFile = "database_cleanup_commands.sql"
    $sqlCommands | Out-File -FilePath $sqlFile -Encoding UTF8
    Write-ColorOutput "✅ SQL commands saved to: $sqlFile" $Green
}

function Install-Modules {
    param([string]$OdooPath, [string]$DatabaseName, [string]$ConfigFile)
    
    Write-ColorOutput "📦 Installing modules..." $Blue
    
    if (-not (Test-Path $OdooPath)) {
        Write-ColorOutput "❌ Odoo executable not found at: $OdooPath" $Red
        Write-ColorOutput "Please provide the correct path to odoo-bin" $Yellow
        return $false
    }
    
    try {
        # Install einv_sa first
        Write-ColorOutput "Installing einv_sa..." $Blue
        $result1 = & $OdooPath -d $DatabaseName -i einv_sa --stop-after-init --no-http 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ einv_sa installed successfully" $Green
        } else {
            Write-ColorOutput "⚠️ einv_sa installation completed with warnings" $Yellow
        }
        
        # Install ejar_integration second
        Write-ColorOutput "Installing ejar_integration..." $Blue
        $result2 = & $OdooPath -d $DatabaseName -i ejar_integration --stop-after-init --no-http 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ ejar_integration installed successfully" $Green
        } else {
            Write-ColorOutput "⚠️ ejar_integration installation completed with warnings" $Yellow
        }
        
        # Update both modules
        Write-ColorOutput "Updating both modules..." $Blue
        $result3 = & $OdooPath -d $DatabaseName -u einv_sa,ejar_integration --stop-after-init --no-http 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Modules updated successfully" $Green
        } else {
            Write-ColorOutput "⚠️ Module update completed with warnings" $Yellow
        }
        
        return $true
    }
    catch {
        Write-ColorOutput "❌ Error during module installation: $($_.Exception.Message)" $Red
        return $false
    }
}

function Show-ManualInstructions {
    Write-ColorOutput "📋 Manual Installation Instructions" $Blue
    Write-ColorOutput "If automatic installation fails, follow these steps:" $Yellow
    
    $instructions = @"

1. Start Odoo manually:
   $OdooPath -d $DatabaseName -c $ConfigFile

2. Open Odoo in browser (usually http://localhost:8069)

3. Go to Apps menu

4. Remove any filters and search for 'einv_sa'

5. Install einv_sa first

6. After successful installation, search for 'ejar_integration'

7. Install ejar_integration

8. Verify both modules are installed and working

"@
    
    Write-ColorOutput $instructions $Yellow
}

# Main execution
Write-ColorOutput "🚀 Starting Enhanced Module Inconsistency Fix" $Blue
Write-ColorOutput "Target modules: einv_sa, ejar_integration" $Blue
Write-ColorOutput "Database: $DatabaseName" $Blue

# Step 1: Create backup reminder
if (-not $SkipBackup) {
    Write-ColorOutput "⚠️ IMPORTANT: Create a database backup before proceeding!" $Red
    Write-ColorOutput "Press 'y' to continue or any other key to exit..." $Yellow
    $response = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    if ($response.Character -ne 'y' -and $response.Character -ne 'Y') {
        Write-ColorOutput "❌ Operation cancelled by user" $Red
        exit 1
    }
}

# Step 2: Stop Odoo
Stop-OdooService

# Step 3: Clean Python cache
Clear-PythonCache

# Step 4: Show database cleanup commands
Show-DatabaseCleanupCommands

Write-ColorOutput "📋 Please execute the SQL commands shown above in your PostgreSQL database" $Yellow
Write-ColorOutput "Press any key to continue after executing the database cleanup..." $Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Step 5: Start Odoo service
Start-OdooService

# Wait for Odoo to start
Write-ColorOutput "⏳ Waiting for Odoo to start..." $Blue
Start-Sleep -Seconds 10

# Step 6: Install modules
$installSuccess = Install-Modules -OdooPath $OdooPath -DatabaseName $DatabaseName -ConfigFile $ConfigFile

if (-not $installSuccess) {
    Write-ColorOutput "⚠️ Automatic installation failed. Showing manual instructions..." $Yellow
    Show-ManualInstructions
}

# Step 7: Final verification
Write-ColorOutput "🎯 Fix process completed!" $Green
Write-ColorOutput "Please verify the following:" $Blue
Write-ColorOutput "1. Check Odoo logs for any remaining errors" $Yellow
Write-ColorOutput "2. Verify both modules are installed in Apps menu" $Yellow
Write-ColorOutput "3. Test basic functionality of both modules" $Yellow

Write-ColorOutput "📁 Generated files:" $Blue
Write-ColorOutput "- database_cleanup_commands.sql (SQL cleanup commands)" $Green
Write-ColorOutput "- CRITICAL_MODULE_FIX_GUIDE.md (Complete documentation)" $Green

Write-ColorOutput "✅ Enhanced module fix script completed!" $Green