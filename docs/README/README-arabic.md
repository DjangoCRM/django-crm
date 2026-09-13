<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/README.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-hindi.md">हिन्दी</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-spanish.md">Español</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-arabic.md">
العربية</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-portuguese.md">Português</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-french.md">Français</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-german.md">Deutsch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-dutch.md">Dutch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-italian.md">Italiano</a>
</p>

# نظام إدارة علاقات العملاء Django-CRM

*(برنامج إدارة علاقات العملاء التعاوني والتحليلي)*

**Django-CRM** هو حل مفتوح المصدر لإدارة علاقات العملاء مصمم بهدفين رئيسيين:

- **للمستخدمين**: تقديم برنامج إدارة علاقات العملاء مفتوح المصدر بمستوى الشركات مع مجموعة شاملة من الحلول التجارية.
- **للمطورين**: تبسيط عمليات التطوير والتخصيص ودعم خادم الإنتاج.

**لا حاجة لتعلم إطار عمل خاص**: كل شيء مبني باستخدام إطار عمل Django الشهير.
يستفيد نظام إدارة علاقات العملاء أيضًا بشكل كامل من موقع إدارة Django، مع توثيق كل شيء في صفحة ويب واحدة!

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="لقطة شاشة لنظام إدارة علاقات العملاء Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

## ميزات إدارة علاقات العملاء

|                              |                                          |                                  |
|------------------------------|------------------------------------------|----------------------------------|
| ☑️ **مهام الفريق والمشاريع** | ☑️ **إدارة العملاء المحتملين**            | ☑️ **التسويق عبر البريد الإلكتروني** |
| ☑️ **إدارة جهات الاتصال**    | ☑️ **تتبع الصفقات وتوقعات المبيعات**      | ☑️ **التحكم في الوصول بناءً على الأدوار** |
| ☑️ **تحليلات المبيعات**      | ☑️ **تكامل الدردشة الداخلية**            | ☑️ **تصميم متوافق مع الأجهزة المحمولة** |
| ☑️ **تقارير قابلة للتخصيص**  | ☑️ **مزامنة البريد الإلكتروني التلقائية** | ☑️ **دعم العملات المتعددة**    |

تعرف على المزيد حول [قدرات البرنامج](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md).

نظام إدارة علاقات العملاء Django هو برنامج مفتوح المصدر لإدارة علاقات العملاء. هذا النظام مكتوب بلغة <a href="https://www.python.org" target="_blank"><img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" style="vertical-align: middle" alt="شعار بايثون" width="25" height="25"> بايثون</a>.
الواجهة الأمامية والخلفية تعتمد بالكامل على موقع إدارة Django.
يستخدم تطبيق إدارة علاقات العملاء قوالب HTML التكيفية للإدارة مباشرة.
Django هو إطار عمل موثق بشكل ممتاز مع الكثير من الأمثلة.
التوثيق على موقع الإدارة يشغل صفحة ويب واحدة فقط.
💡 **الفكرة الأصلية** هي أنه بما أن إدارة Django هي بالفعل واجهة احترافية لإدارة الكائنات مع نظام أذونات مرن للمستخدمين (عرض، تغيير، إضافة، وحذف الكائنات)، كل ما تحتاجه هو إنشاء نماذج للكائنات (مثل العملاء المحتملين، الطلبات، الصفقات، الشركات، إلخ) وإضافة منطق الأعمال.

كل هذا يضمن:

- تخصيص المشروع وتطويره بشكل أسهل بكثير
- نشر المشروع ودعم خادم الإنتاج بشكل أبسط

تقدم حزمة البرنامج موقعين:

- موقع إدارة علاقات العملاء لجميع المستخدمين
- موقع للمسؤولين

**المشروع ناضج ومستقر**، وقد تم استخدامه بنجاح في التطبيقات الحقيقية لسنوات عديدة.

## التطبيقات الرئيسية

تتكون حزمة برامج إدارة علاقات العملاء من التطبيقات **الرئيسية** التالية ونماذجها:

- **تطبيق إدارة المهام**:
  (متاح لجميع المستخدمين افتراضيًا، بغض النظر عن دورهم)
  - المهمة (مع الملفات ذات الصلة، الدردشة، التذكيرات، العلامات - انظر [ميزات المهمة](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md))
    - المهام الفرعية
  - المذكرة (مذكرة المكتب) - انظر [ميزات المذكرة](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)
    - المهام / المشروع
  - المشروع (*مجموعة المهام*):
  - ... (+ *4 نماذج أخرى <a href="https://github.com/DjangoCRM/django-crm/tree/main/tasks/models" target="_blank">نماذج</a>*)
- **تطبيق إدارة علاقات العملاء**:
  - الطلبات (الاستفسارات التجارية)
  - العملاء المحتملين (العملاء المحتملين)
  - الشركات
  - الأشخاص المتصلين (مرتبطون بشركاتهم)
  - الصفقات (مثل "الفرص")
  - رسائل البريد الإلكتروني (مزامنة مع حسابات البريد الإلكتروني للمستخدمين)
  - المنتجات (السلع والخدمات)
  - نظام التسعير
  - المدفوعات (المستلمة، المضمونة، ذات الاحتمالية العالية والمنخفضة)
  - ... (*+ 12 نموذجًا آخر <a href="https://github.com/DjangoCRM/django-crm/tree/main/crm/models" target="_blank">نماذج</a>*)
[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="تقرير تحليلي لنظام إدارة علاقات العملاء" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)
- **تطبيق التحليلات**: ([نظرة عامة مفصلة على البرنامج](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md))
  - تقرير ملخص الدخل (*انظر [لقطة الشاشة](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)*)
  - تقرير قمع المبيعات
  - تقرير ملخص مصدر العملاء المحتملين
  - ... (+ *5 تقارير تحليلية أخرى*)
- **تطبيق البريد الجماعي**:
  - حسابات البريد الإلكتروني
  - رسائل البريد الإلكتروني (النشرات الإخبارية)
  - توقيعات البريد الإلكتروني (توقيعات المستخدمين)
  - البريد الجماعي

## التطبيقات الداعمة

تحتوي حزمة إدارة علاقات العملاء أيضًا على **تطبيقات داعمة** مثل:

- تطبيق الدردشة (الدردشة متاحة في كل مهمة، مشروع، مذكرة مكتب وصفقة)
- تطبيق VoIP (الاتصال بالعملاء من الصفقات)
- تطبيق المساعدة (صفحات المساعدة الديناميكية حسب دور المستخدم)
- تطبيق مشترك:
  - 🪪 ملفات تعريف المستخدمين
  - ⏰ التذكيرات (للمهام، المشاريع، مذكرات المكتب والصفقات)
  - 📝 العلامات (للمهام، المشاريع، مذكرات المكتب والصفقات)
  - 📂 الملفات (للمهام، المشاريع، مذكرات المكتب والصفقات)

## الوظائف الإضافية

- تكامل نموذج الويب: يحتوي نموذج الاتصال لإدارة علاقات العملاء على:
  - حماية reCAPTCHA v3
  - تحديد الموقع الجغرافي التلقائي
- تكامل ومزامنة حساب البريد الإلكتروني للمستخدم. يتم حفظ رسائل البريد الإلكتروني تلقائيًا:
  - في قاعدة بيانات إدارة علاقات العملاء
  - مرتبطة بالكائنات المناسبة في إدارة علاقات العملاء (مثل: الطلبات، العملاء المحتملين، الصفقات، إلخ)
- الاتصال عبر VoIP إلى الهاتف الذكي
- إرسال الرسائل عبر المراسلات (مثل: Viber، WhatsApp، ...)
- دعم Excel: استيراد/تصدير تفاصيل الاتصال بسهولة.

## عميل البريد الإلكتروني

يتضمن نظام إدارة علاقات العملاء Python عميل بريد إلكتروني مدمج يعمل باستخدام بروتوكولات **SMTP** و**IMAP**.
يتيح ذلك لنظام إدارة علاقات العملاء Django تخزين نسخ من جميع المراسلات المتعلقة بكل طلب وصفقة تلقائيًا داخل قاعدة بياناته.
تضمن هذه الوظيفة أنه حتى إذا تمت الاتصالات عبر حساب البريد الإلكتروني الخارجي للمستخدم (خارج إدارة علاقات العملاء)، يتم التقاطها وتنظيمها داخل النظام باستخدام **آلية التذاكر**.

يمكن لنظام إدارة علاقات العملاء التكامل مع مزودي خدمات البريد الإلكتروني (مثل Gmail) الذين يتطلبون مصادقة ثنائية إلزامية (باستخدام بروتوكول **OAuth 2.0**) للتطبيقات الخارجية.

## مساعدة المستخدم

- تتضمن كل صفحة في نظام إدارة علاقات العملاء رابطًا إلى صفحة مساعدة ذات صلة بالسياق، مع محتوى مخصص ديناميكيًا لدور المستخدم للحصول على إرشادات أكثر صلة.
- تتوفر تلميحات الأدوات في جميع أنحاء الواجهة، مما يوفر معلومات فورية عند التمرير فوق العناصر مثل الأيقونات، الأزرار، الروابط، أو رؤوس الجداول.
- يتضمن أيضًا دليل مستخدم شامل [دليل المستخدم](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md) للرجوع إليه ودعمه بشكل متعمق.

## رفع إنتاجية فريقك باستخدام حلول إدارة علاقات العملاء التعاونية

تم تصميم هذا النظام لتعزيز التعاون داخل الفرق وتبسيط عمليات إدارة المشاريع.
كنظام إدارة علاقات العملاء تعاوني، يتيح للمستخدمين إنشاء وإدارة المذكرات، المهام، والمشاريع بسهولة.
يمكن توجيه [مذكرات المكتب](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md) إلى رؤساء الأقسام أو المديرين التنفيذيين للشركة، الذين يمكنهم بعد ذلك تحويل هذه المذكرات إلى مهام أو مشاريع، وتعيين الأشخاص المسؤولين أو المنفذين.
يمكن أن تكون [المهام](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md) فردية أو جماعية.
توفر المهام ميزات مثل مناقشات الدردشة، التذكيرات، مشاركة الملفات، إنشاء المهام الفرعية، ومشاركة النتائج.
يتلقى المستخدمون إشعارات مباشرة في إدارة علاقات العملاء وعبر البريد الإلكتروني، مما يضمن بقائهم على اطلاع.
يتمتع كل مستخدم برؤية واضحة لمجموعة مهامه، بما في ذلك الأولويات، الحالات، والخطوات التالية، مما يعزز الإنتاجية والمساءلة في إدارة علاقات العملاء التعاونية.

## توطين المشروع

يدعم نظام إدارة علاقات العملاء Django الترجمة الكاملة للواجهة، وتنسيق التواريخ، الأوقات، والمناطق الزمنية.
<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="شعار django" width="30" height="30" style="vertical-align: middle"> برنامج خدمة العملاء متاح الآن بلغات **متعددة:**  
`de, en, es, fr, hi, it, nl, pt-BR, ru, uk`

## لماذا تختار نظام إدارة علاقات العملاء Django؟

- **نظام إدارة علاقات العملاء التعاوني**: عزز إنتاجية الفريق باستخدام أدوات لإدارة المهام، التعاون في المشاريع، والاتصالات الداخلية.
- **نظام إدارة علاقات العملاء التحليلي**: احصل على رؤى قابلة للتنفيذ مع التقارير المدمجة مثل قمع المبيعات، ملخص الدخل، وتحليل مصدر العملاء المحتملين.
- **مبني على Python وDjango**: لا حاجة لإطارات عمل خاصة - كل شيء مبني على Django بواجهة إدارة بديهية.

## البدء

يمكن نشر نظام إدارة علاقات العملاء Django بسهولة كمشروع Django عادي.

📚 يرجى الرجوع إلى:

- [دليل التثبيت والتكوين](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
- [دليل المستخدم](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)

إذا وجدت نظام إدارة علاقات العملاء Django مفيدًا، يرجى ⭐️ **تقييم** هذا المستودع على GitHub لدعم نموه!
<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/Django-CRM_star_history.png" alt="تاريخ تقييم نظام إدارة علاقات العملاء Django" align="center" style="float: center"/>

### التوافق

- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Django 5.1.x
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="python logo" width="30" height="30" style="vertical-align: middle"> Python 3.10+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="mysql logo" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30" style="vertical-align: middle"> PostgreSQL 12+  

## المساهمة

المساهمات مرحب بها! هناك مجال للتحسينات والميزات الجديدة.
تحقق من [دليل المساهمة](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md) لتتعلم كيفية البدء.
كل مساهمة، كبيرة أو صغيرة، تحدث فرقًا.

## الترخيص

تم إصدار نظام إدارة علاقات العملاء Django تحت ترخيص AGPL-3.0 - انظر ملف [الترخيص](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE) للحصول على التفاصيل.

## الشكر

- أيقونات Google material [icons](https://fonts.google.com/icons).
- [NicEdit](https://nicedit.com) - محرر محتوى WYSIWYG.
- جميع الموارد المستخدمة بموجب تراخيص أخرى.