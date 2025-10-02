# Purchase Decimal Precision - موديول دقة الكسور العشرية في أوامر الشراء

## الوصف
هذا الموديول يسمح بإدخال الكسور العشرية حتى 4 خانات في سطور أوامر الشراء بدلاً من الخانتين الافتراضيتين في Odoo 15.

## المميزات
- زيادة دقة الكسور العشرية إلى 4 خانات للحقول التالية:
  - سعر الوحدة (Unit Price)
  - الكمية (Quantity) 
  - المجموع الفرعي (Subtotal)
  - المجموع الكلي (Total)
- متوافق مع سير العمل الحالي لأوامر الشراء
- يدعم اللغتين العربية والإنجليزية

## التثبيت
1. انسخ مجلد `purchase_decimal_precision` إلى مجلد addons في Odoo
2. قم بتحديث قائمة التطبيقات (Update Apps List)
3. ابحث عن "Purchase Decimal Precision" وقم بتثبيته
4. أعد تشغيل خدمة Odoo

## الاستخدام
بعد التثبيت، ستتمكن من:
- إدخال أسعار بدقة 4 خانات عشرية (مثل: 12.3456)
- إدخال كميات بدقة 4 خانات عشرية (مثل: 1.2345)
- عرض المجاميع بدقة 4 خانات عشرية

## هيكل الملفات
```
purchase_decimal_precision/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   └── purchase_order.py
├── data/
│   └── decimal_precision_data.xml
└── security/
    └── ir.model.access.csv
```

## المتطلبات
- Odoo 15.0
- موديول Purchase (مثبت افتراضياً)

## الدعم الفني
للحصول على الدعم الفني أو الإبلاغ عن مشاكل، يرجى التواصل مع فريق التطوير.

## الترخيص
LGPL-3

---

# Purchase Decimal Precision Module

## Description
This module allows entering decimal values with up to 4 decimal places in purchase order lines instead of the default 2 decimal places in Odoo 15.

## Features
- Increases decimal precision to 4 places for:
  - Unit Price
  - Quantity
  - Subtotal
  - Total
- Compatible with existing purchase workflows
- Supports Arabic and English languages

## Installation
1. Copy the `purchase_decimal_precision` folder to your Odoo addons directory
2. Update the Apps List
3. Search for "Purchase Decimal Precision" and install it
4. Restart Odoo service

## Usage
After installation, you can:
- Enter prices with 4 decimal precision (e.g., 12.3456)
- Enter quantities with 4 decimal precision (e.g., 1.2345)
- View totals with 4 decimal precision

## Requirements
- Odoo 15.0
- Purchase module (installed by default)

## License
LGPL-3