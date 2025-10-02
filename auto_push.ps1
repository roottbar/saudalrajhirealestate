# Auto Push Script for Saudal Rajhi Real Estate Odoo Production
# This script automatically commits and pushes changes to GitHub

param(
    [string]$CommitMessage = "Auto update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)

Write-Host "Starting auto push process..." -ForegroundColor Green

# Check if there are any changes
$status = git status --porcelain
if ([string]::IsNullOrEmpty($status)) {
    Write-Host "No changes detected. Nothing to commit." -ForegroundColor Yellow
    exit 0
}

Write-Host "Changes detected. Proceeding with commit and push..." -ForegroundColor Cyan

# Add all changes
Write-Host "Adding all changes..." -ForegroundColor Blue
git add .

# Commit changes
Write-Host "Committing changes with message: $CommitMessage" -ForegroundColor Blue
git commit -m "$CommitMessage"

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Blue
$pushResult = git push origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
} else {
    Write-Host "Push failed. Trying to push to master branch..." -ForegroundColor Yellow
    $pushResult = git push origin master 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully pushed to GitHub (master branch)!" -ForegroundColor Green
    } else {
        Write-Host "Push failed. Error: $pushResult" -ForegroundColor Red
        Write-Host "You may need to create the repository on GitHub first or check your credentials." -ForegroundColor Yellow
    }
}

Write-Host "Auto push process completed." -ForegroundColor Green