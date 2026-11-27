# SAFER-MedAI — راهنمای بارگذاری در GitHub

**نام دقیق مخزن:** `SAFER-MedAI-Synthetic-Pilot`

**توضیح مخزن (Description):** `Reproducible synthetic evidence-acquisition pilot for SAFER-MedAI (Stage 02C-1), including prespecified negative findings and archived traces.`

## مراحل

1. وارد https://github.com/new شوید؛ Repository name را دقیقا `SAFER-MedAI-Synthetic-Pilot` قرار دهید.
2. در مرحله نخست **Private** را انتخاب کنید؛ گزینه‌های Initialize with README / Add .gitignore / Add license را فعال نکنید (README و .gitignore از قبل داخل بسته هستند).
3. دو فایل `SAFER_MedAI_GitHub_READY_AUTHORS_20261127.zip` و `SAFER_UPLOAD_TO_GITHUB_WINDOWS_AUTHORS.ps1` را در Downloads ذخیره کنید.
4. PowerShell را اجرا کنید:

```powershell
& "$env:USERPROFILE\Downloads\SAFER_UPLOAD_TO_GITHUB_WINDOWS_AUTHORS.ps1"
```

5. در صورت درخواست، نام کاربری حساب GitHub را تایپ کنید و با توجه به اینکه مخزن تازه‌ساخته‌شده **Private** است عبارت `PRIVATE` را وارد کنید. اسکریپت محتوای ZIP را در Documents استخراج می‌کند، Git init/commit/push را انجام می‌دهد و هیچ توکن یا گذرواژه‌ای ذخیره نمی‌کند. باید Git for Windows روی سیستم نصب و احراز هویت GitHub برای push فراهم باشد.
6. پس از مشاهده فایل‌های README، src، pilot_02C1، tests و configs در GitHub، با صاحب/صاحبان حقوق کد درباره مجوز MIT و حقوق داده‌های مصنوعی تصمیم بگیرید. **تا آن زمان انتشار عمومی، GitHub Release و DOI را انجام ندهید.**
7. بعد از انتخاب مجوز معتبر و عمومی‌کردن مخزن، در Zenodo حساب GitHub را وصل کنید، مخزن را فعال و سپس GitHub Release با tag `v1.0.0` بسازید. پس از تأیید بایگانی Zenodo، Version DOI واقعی را به مقاله اضافه کنید.

## محدوده علمی و محتوای بسته

فقط پیاده‌سازی و سوابق **مصنوعی** Stage 02C-1 منتشر می‌شود؛ مخزن شامل مجموعه‌داده پزشکی NIH، ECG، تصاویر بیماران، مدل آموزش‌دیده تاریخی یا کد ثالث Active RCPS نیست. نتیجه اصلی آزمایش P4 در مقایسه با P5 **منفی ۵۰ واحد درصد** بوده و تأیید ۱۰۰۰ seed اجرا نشده است. هیچ ادعای ایمنی بالینی یا برتری عمومی مجاز نیست.

برای ممیزی محلی (در پوشه کد):

```powershell
python verify_archived_evidence.py
python recompute_recorded_primary.py
python -m unittest discover -s tests -p 'test_safer_cpu.py' -v
```

**هش فایل‌های Pilot در `pilot_02C1/SHA256_MANIFEST.csv` ثبت شده است.**
