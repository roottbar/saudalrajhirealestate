# 🚀 AUTOMATED DEPLOYMENT FIX - READY TO EXECUTE

## ⚡ QUICK START - Copy & Paste These Commands on Your Deployment Server

### **STEP 1: Connect to Your Deployment Server**
```bash
# SSH into your deployment server (Linux)
ssh your_username@your_server_ip
```

### **STEP 2: Run Automated Fix (ONE COMMAND)**
```bash
cd /home/odoo/src/user && git pull origin Update_Odoo_2025 && chmod +x DEPLOYMENT_SERVER_FIX.sh && ./DEPLOYMENT_SERVER_FIX.sh
```

---

## 📋 Alternative: Step-by-Step Commands

If you prefer to run each step separately:

### **1. Navigate to Odoo Directory**
```bash
cd /home/odoo/src/user
```

### **2. Pull Latest Fixes from GitHub**
```bash
git pull origin Update_Odoo_2025
```

### **3. Make Script Executable**
```bash
chmod +x DEPLOYMENT_SERVER_FIX.sh
```

### **4. Run the Automated Fix**
```bash
./DEPLOYMENT_SERVER_FIX.sh
```

### **5. Choose Restart Method**
When prompted, select your Odoo restart method:
- **A** = systemctl restart odoo
- **B** = service odoo restart
- **C** = supervisorctl restart odoo
- **D** = Manual restart

---

## ✅ What This Script Does Automatically

The script will:
1. ✅ Pull all latest fixes from GitHub
2. ✅ Apply report_xlsx controller fix
3. ✅ Install lxml_html_clean dependency
4. ✅ Verify all fixes are correct
5. ✅ Restart your Odoo service
6. ✅ Provide deployment status summary

---

## 🎯 Expected Output

```
🚀 Starting saudalrajhirealestate deployment fix...
📁 Navigating to modules directory...
✅ Current directory: /home/odoo/src/user
📋 Checking current git status...
⬇️  Pulling latest fixes from GitHub...
✅ Git pull successful!
📦 Installing missing lxml_html_clean dependency...
✅ lxml_html_clean installed successfully!
🔍 Verifying critical fixes...
✅ report_xlsx controller fix: CORRECT
✅ date_range test fix: CORRECT
✅ lxml dependency fix: CORRECT
🔄 Restarting Odoo service...
✅ Odoo restarted successfully!
🚀 Saudi Al-Rajhi Real Estate deployment fix completed!
```

---

## 🆘 If Script Fails

If you get any errors, run manual fix commands:

```bash
cd /home/odoo/src/user

# Manual report_xlsx fix
sed -i 's/from odoo.addons.web.controllers.report import/from odoo.addons.web.controllers.main import/g' report_xlsx/controllers/main.py

# Install dependency
pip install lxml_html_clean>=0.1.0

# Restart Odoo
sudo systemctl restart odoo
```

---

## 📞 Support Information

- **Repository**: https://github.com/roottbar/saudalrajhirealestate
- **Branch**: Update_Odoo_2025
- **Author**: roottbar <root@tbarholding.com>
- **Date**: September 30, 2025

---

## ⚡ COPY THIS SINGLE COMMAND NOW:

```bash
cd /home/odoo/src/user && git pull origin Update_Odoo_2025 && chmod +x DEPLOYMENT_SERVER_FIX.sh && ./DEPLOYMENT_SERVER_FIX.sh
```

**This one command does everything automatically!** 🎉
