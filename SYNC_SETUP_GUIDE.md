# دليل إعداد التزامن التلقائي مع GitHub و Odoo.sh

## نظرة عامة
هذا النظام يوفر تزامناً تلقائياً بين مشروعك المحلي و GitHub و Odoo.sh، حيث يتم دفع أي تغييرات تحدث في الملفات تلقائياً.

## المكونات

### 1. GitHub Actions (`.github/workflows/odoo-sync.yml`)
- يعمل عند كل push إلى GitHub
- يقوم بمزامنة التغييرات مع Odoo.sh تلقائياً
- يتطلب إعداد secrets في GitHub

### 2. سكريبت المراقبة التلقائية (`auto-push.py`)
- يراقب التغييرات في الملفات المحلية
- يقوم بـ commit و push تلقائي عند حدوث تغييرات
- يدعم التزامن مع GitHub و Odoo.sh

## خطوات الإعداد

### الخطوة 1: إعداد GitHub Secrets
1. اذهب إلى repository في GitHub
2. Settings → Secrets and variables → Actions
3. أضف هذه الـ secrets:
   - `ODOO_SSH_PRIVATE_KEY`: المفتاح الخاص للـ SSH الخاص بـ Odoo.sh
   - `ODOO_REPO_URL`: رابط repository في Odoo.sh (مثل: `git@git.odoo.sh:your-project.git`)

### الخطوة 2: إعداد SSH Key لـ Odoo.sh
```bash
# إنشاء SSH key جديد
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# إضافة المفتاح العام إلى Odoo.sh
# انسخ محتوى ~/.ssh/id_rsa.pub وأضفه في إعدادات Odoo.sh
```

### الخطوة 3: إضافة Odoo.sh كـ Remote
```bash
# إضافة Odoo.sh remote
git remote add odoo git@git.odoo.sh:your-project.git

# التحقق من الـ remotes
git remote -v
```

### الخطوة 4: تثبيت المتطلبات المحلية
```bash
# تشغيل ملف الإعداد
setup-sync.bat

# أو يدوياً:
pip install -r requirements-autopush.txt
```

### الخطوة 5: بدء المراقبة التلقائية
```bash
# بدء المراقبة
start-autopush.bat

# أو يدوياً:
python auto-push.py
```

## كيفية العمل

### التزامن التلقائي المحلي
1. السكريبت يراقب جميع الملفات في المشروع
2. عند حدوث تغيير، ينتظر 30 ثانية لتجميع التغييرات
3. يقوم بـ `git add .` و `git commit` تلقائياً
4. يدفع التغييرات إلى GitHub و Odoo.sh

### التزامن عبر GitHub Actions
1. عند push إلى GitHub، يتم تشغيل workflow
2. يتم checkout الكود
3. يتم إعداد SSH للاتصال بـ Odoo.sh
4. يتم دفع التغييرات إلى Odoo.sh

## الملفات المتجاهلة
السكريبت يتجاهل:
- ملفات `.pyc`, `.log`, `.tmp`, `.swp`
- مجلدات `.git`, `__pycache__`, `.vscode`, `node_modules`

## استكشاف الأخطاء

### مشكلة في SSH
```bash
# اختبار الاتصال بـ Odoo.sh
ssh -T git@git.odoo.sh
```

### مشكلة في Git Push
```bash
# التحقق من الـ remotes
git remote -v

# اختبار push يدوي
git push origin main
git push odoo main
```

### مشكلة في Python Script
```bash
# تشغيل السكريبت مع تفاصيل أكثر
python auto-push.py

# مراجعة ملف الـ log
type auto-push.log
```

## الأمان
- لا تشارك المفاتيح الخاصة
- استخدم GitHub Secrets لحفظ المعلومات الحساسة
- تأكد من صحة صلاحيات SSH keys

## التخصيص
يمكنك تعديل:
- `commit_delay` في `auto-push.py` لتغيير وقت الانتظار
- `ignored_extensions` و `ignored_dirs` لتخصيص الملفات المتجاهلة
- رسائل الـ commit في السكريبت

## الدعم
في حالة وجود مشاكل:
1. تحقق من ملف `auto-push.log`
2. تأكد من صحة إعدادات SSH
3. تحقق من GitHub Secrets
4. تأكد من صلاحيات الوصول لـ repositories