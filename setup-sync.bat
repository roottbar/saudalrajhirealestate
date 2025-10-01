@echo off
echo ========================================
echo إعداد نظام التزامن التلقائي مع GitHub و Odoo.sh
echo ========================================

echo.
echo 1. تثبيت المكتبات المطلوبة...
pip install -r requirements-autopush.txt

echo.
echo 2. إعداد Git configuration...
git config --global user.name "Auto Sync Bot"
git config --global user.email "autosync@yourdomain.com"

echo.
echo 3. التحقق من Git remotes...
git remote -v

echo.
echo ========================================
echo تم الإعداد بنجاح!
echo ========================================
echo.
echo لبدء المراقبة التلقائية، قم بتشغيل:
echo python auto-push.py
echo.
echo أو استخدم:
echo start-autopush.bat
echo ========================================

pause