نظام الترشح لانتخابات اتحاد طلاب الموهبة والتميز
=============================================

ملخص
-----
مشروع ويب مبني على FastAPI يقدم واجهة عربية كاملة لفتح باب الترشح كفرد أو كقائمة.

هيكل المشروع
-------------
- `app/` يحتوي الكود
  - `main.py` التطبيق الرئيسي
  - `models.py` نماذج قاعدة البيانات (SQLAlchemy)
  - `database.py` إعداد الاتصال بقاعدة البيانات
  - `crud.py` دوال إنشاء السجلات
  - `utils.py` مساعدات: رفع الملفات، إرسال البريد
  - `templates/` واجهات HTML (عربية RTL)
- `requirements.txt` تبعيات

التثبيت والتشغيل (بيئة افتراضية)
---------------------------------
1. إنشاء وتفعيل venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. إعداد المتغيرات البيئية (اختياري):

```
export ADMIN_EMAIL=admin@domain.com
export SMTP_HOST=smtp.domain.com
export SMTP_PORT=587
export SMTP_USER=you
export SMTP_PASS=pass
export ADMIN_PASSWORD=your-secure-password
```

3. تشغيل الخادم:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

تغيير البريد الإداري
-------------------
يمكن تغيير البريد في الملف `app/config.py` أو عن طريق تعيين المتغير البيئي `ADMIN_EMAIL` قبل تشغيل التطبيق.

النسخ الاحتياطي للبيانات
------------------------
قاعدة البيانات الافتراضية هي SQLite `db.sqlite3`. لنسخها احتياطياً، انسخ الملف:

```bash
cp db.sqlite3 db.sqlite3.bak
tar -czvf uploads-backup.tgz uploads/
```

ملاحظات أمنية
-------------
- تحققنا من امتدادات MIME وحجم الملفات قبل الحفظ.
- إعادة تسمية الملفات بأسماء عشوائية لمنع التسميات المكررة.
- استخدام SQLAlchemy لمنع حقن SQL.
- جافاسكربت وفلترة جانب الخادم لتقليل XSS; يجب تعقيم أي مدخلات تعرض لاحقًا.
- الحماية من CSRF: عند النشر في إنتاج أضف حماية جلسات و CSRF tokens.

التوصيات للإنتاج
-----------------
- استخدام PostgreSQL بدل SQLite.
- استخدام خادم بريد موثوق وتهيئة TLS.
- تخزين الأسرار في Vault أو متغيرات بيئة آمنة.
- إضافة تسجيل دخول مبني على JWT أو جلسات مع CSRF.
