# PDF Processing Troubleshooting Guide
# دليل حل مشاكل معالجة ملفات PDF

## English Version

### Common Issues and Solutions

#### 1. "Error processing resume file" Message
This error can occur for several reasons:

**Possible Causes:**
- Corrupted PDF file
- Password-protected PDF
- Image-only PDF (scanned document)
- Invalid file format
- Large file size (>10MB)

**Solutions:**
1. **Check file format**: Ensure the file is actually a PDF
2. **Remove password protection**: Save the PDF without password
3. **Convert scanned PDFs**: Use OCR software to convert image-based PDFs to text
4. **Reduce file size**: Compress the PDF if it's larger than 10MB
5. **Try a different PDF**: Test with a simple text-based PDF

#### 2. Using the Debug Tool

We've included a debug script to help identify PDF issues:

```bash
cd hr_resume_ats
python test_pdf_debug.py
```

Enter the path to your PDF file when prompted. The script will:
- Check if PyPDF2 is installed
- Validate PDF format
- Test text extraction
- Provide detailed error information

#### 3. PDF Requirements

**Supported:**
- Text-based PDF files
- Unprotected PDFs
- Files smaller than 10MB
- Standard PDF format (PDF 1.4 and above)

**Not Supported:**
- Password-protected PDFs
- Image-only PDFs (without OCR)
- Corrupted or incomplete PDFs
- Files larger than 10MB

#### 4. Error Messages Explained

- **"Invalid PDF file format"**: File doesn't start with PDF header
- **"PDF file is password protected"**: Remove password and try again
- **"No text could be extracted"**: PDF contains only images
- **"File size too large"**: Compress the PDF file
- **"Failed to read PDF file"**: File is corrupted or invalid

---

## النسخة العربية

### المشاكل الشائعة والحلول

#### 1. رسالة "خطأ في معالجة ملف السيرة الذاتية"
يمكن أن يحدث هذا الخطأ لعدة أسباب:

**الأسباب المحتملة:**
- ملف PDF تالف
- ملف PDF محمي بكلمة مرور
- ملف PDF يحتوي على صور فقط (مستند ممسوح ضوئياً)
- تنسيق ملف غير صحيح
- حجم ملف كبير (أكثر من 10 ميجابايت)

**الحلول:**
1. **تحقق من تنسيق الملف**: تأكد أن الملف هو PDF فعلاً
2. **إزالة حماية كلمة المرور**: احفظ الـ PDF بدون كلمة مرور
3. **تحويل ملفات PDF الممسوحة**: استخدم برنامج OCR لتحويل ملفات PDF المبنية على الصور إلى نص
4. **تقليل حجم الملف**: اضغط الـ PDF إذا كان أكبر من 10 ميجابايت
5. **جرب ملف PDF مختلف**: اختبر بملف PDF بسيط يحتوي على نص

#### 2. استخدام أداة التشخيص

قمنا بتضمين أداة تشخيص لمساعدتك في تحديد مشاكل PDF:

```bash
cd hr_resume_ats
python test_pdf_debug.py
```

أدخل مسار ملف PDF عند الطلب. ستقوم الأداة بـ:
- فحص ما إذا كان PyPDF2 مثبت
- التحقق من صحة تنسيق PDF
- اختبار استخراج النص
- توفير معلومات مفصلة عن الأخطاء

#### 3. متطلبات ملفات PDF

**المدعومة:**
- ملفات PDF النصية
- ملفات PDF غير المحمية
- ملفات أصغر من 10 ميجابايت
- تنسيق PDF القياسي (PDF 1.4 وما فوق)

**غير المدعومة:**
- ملفات PDF المحمية بكلمة مرور
- ملفات PDF التي تحتوي على صور فقط (بدون OCR)
- ملفات PDF التالفة أو غير المكتملة
- ملفات أكبر من 10 ميجابايت

#### 4. شرح رسائل الخطأ

- **"تنسيق ملف PDF غير صحيح"**: الملف لا يبدأ برأس PDF
- **"ملف PDF محمي بكلمة مرور"**: أزل كلمة المرور وحاول مرة أخرى
- **"لا يمكن استخراج أي نص"**: الـ PDF يحتوي على صور فقط
- **"حجم الملف كبير جداً"**: اضغط ملف PDF
- **"فشل في قراءة ملف PDF"**: الملف تالف أو غير صحيح

### نصائح إضافية

1. **استخدم ملفات PDF عالية الجودة**: تجنب الملفات الممسوحة ضوئياً
2. **تحقق من الملف قبل الرفع**: افتح الملف في قارئ PDF للتأكد من صحته
3. **استخدم أدوات ضغط PDF**: لتقليل حجم الملفات الكبيرة
4. **احفظ من Word إلى PDF**: إذا كان لديك المستند الأصلي في Word

### الحصول على المساعدة

إذا استمرت المشكلة:
1. استخدم أداة التشخيص المرفقة
2. تحقق من سجلات النظام للحصول على تفاصيل أكثر
3. تواصل مع مدير النظام مع تفاصيل الخطأ