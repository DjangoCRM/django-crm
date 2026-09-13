<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/README.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-hindi.md">हिन्दी</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-spanish.md">Español</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-portuguese.md">Português</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-french.md">Français</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-german.md">Deutsch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-dutch.md">Dutch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-italian.md">Italiano</a>
</p>

---

# Django-CRM

## निःशुल्क ओपन-सोर्स Python CRM जिसमें टास्क प्रबंधन, ईमेल मार्केटिंग और एनालिटिक्स शामिल हैं

**Django CRM** एक निःशुल्क ग्राहक संबंध प्रबंधन (Customer Relationship Management) सॉफ्टवेयर है, जिसे [Python](https://www.python.org) और [Django](https://www.djangoproject.com) पर विकसित किया गया है। यह उन टीमों के लिए डिज़ाइन किया गया है जिन्हें एक ही विस्तारणीय प्लेटफ़ॉर्म में self-hosted CRM, CRM टास्क मैनेजर, मेलिंग CRM और CRM एनालिटिक्स सॉफ्टवेयर की आवश्यकता होती है।

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="स्क्रीनशॉट Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

**प्रोजेक्ट स्थिति:** प्रोडक्शन / स्थिर
कई वर्षों से वास्तविक व्यावसायिक वातावरण में उपयोग किया जा रहा है।

⭐️ यदि यह प्रोजेक्ट आपके लिए उपयोगी है, तो कृपया इस रिपॉजिटरी को **star** करें — इससे अन्य उपयोगकर्ताओं को इस निःशुल्क और ओपन-सोर्स Python CRM को खोजने में सहायता मिलती है।

---

## Django-CRM क्यों चुनें?

Django CRM, CRM और टास्क मैनेजमेंट सॉफ्टवेयर, ईमेल इंटीग्रेशन के साथ CRM, तथा CRM और ईमेल मार्केटिंग सॉफ्टवेयर को एकीकृत करता है — बिना किसी प्रोपाइटरी फ्रेमवर्क, vendor lock-in या SaaS सीमाओं के।

### व्यवसायों और अंतिम उपयोगकर्ताओं के लिए

* एक ही सिस्टम में **लीड्स, डील्स, संपर्क, टास्क, प्रोजेक्ट और ईमेल कैंपेन** प्रबंधित करें
* कई टूल्स को एक **सिंगल सहयोगात्मक CRM** से प्रतिस्थापित करें
* अंतर्निहित **CRM एनालिटिक्स सॉफ्टवेयर** के माध्यम से व्यावसायिक अंतर्दृष्टि प्राप्त करें

### डेवलपर्स और सिस्टम इंटीग्रेटर्स के लिए

* Django फ्रेमवर्क पर आधारित 100% Python CRM
* कोई प्रोपाइटरी UI लेयर नहीं — सब कुछ [Django Admin](https://docs.djangoproject.com/en/dev/ref/contrib/admin/) पर चलता है
* तेज़ कस्टमाइज़ेशन, पूर्वानुमेय अपग्रेड और सरल डिप्लॉयमेंट
* **Self-hosted CRM** और ऑन-प्रिमाइज़ इंस्टॉलेशन के लिए आदर्श

---

## मुख्य CRM फीचर्स

| CRM एवं बिक्री              | टास्क एवं सहयोग   | ईमेल एवं मार्केटिंग             |
|--------------------------| ----------------|--------------------------- |
| लीड प्रबंधन                | CRM टास्क मैनेजर   | मेलिंग CRM                   |
| डील ट्रैकिंग एवं पूर्वानुमान      | प्रोजेक्ट एवं सबटास्क | CRM एवं ईमेल मार्केटिंग सॉफ्टवेयर |
| कंपनी एवं संपर्क प्रबंधन       | आंतरिक चैट       | ईमेल इंटीग्रेशन के साथ CRM      |
| भूमिका-आधारित एक्सेस नियंत्रण | रिमाइंडर एवं फाइलें  | SMTP / IMAP समर्थन          |
| CRM एनालिटिक्स सॉफ्टवेयर     | ऑफिस मेमो       | ईमेल कैंपेन ऑटोमेशन          |

🔎 अधिक जानकारी के लिए [CRM सिस्टम ओवरव्यू देखें](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md)।

---

## Django Admin पर निर्मित Python CRM

Django-CRM, **Django Admin इंटरफ़ेस** का पूर्ण उपयोग करता है:

* अनुकूलनशील एडमिन टेम्पलेट्स (डेस्कटॉप एवं मोबाइल)
* उन्नत फ़िल्टरिंग, सॉर्टिंग और सर्च
* ऑब्जेक्ट-स्तरीय परमिशन (देखें, जोड़ें, बदलें, हटाएँ)
* सिंगल-पेज एडमिन डॉक्यूमेंटेशन

नया UI फ्रेमवर्क बनाने के बजाय, Django-CRM का फोकस **व्यावसायिक लॉजिक**, **डेटा अखंडता**, और **विस्तार क्षमता** पर है — जिससे यह छोटे और मध्यम व्यवसायों के लिए एक आदर्श निःशुल्क CRM समाधान बनता है।

---

## मुख्य एप्लिकेशन

### CRM एप्लिकेशन

* अनुरोध (जांच, घटनाएँ)
* लीड्स और अवसर
* कंपनियाँ और संपर्क व्यक्ति
* डील्स (सेल्स पाइपलाइन)
* उत्पाद और भुगतान
* मूल्य निर्धारण प्रणाली
* CRM ऑब्जेक्ट्स से जुड़े ईमेल संदेश

➡️ जटिल सेल्स वर्कफ़्लो के लिए 20+ परस्पर जुड़े CRM मॉडल।

---

### टास्क एवं प्रोजेक्ट प्रबंधन (CRM टास्क मैनेजर)

एक पूर्ण **CRM और टास्क मैनेजमेंट सॉफ्टवेयर** मॉड्यूल:

* टास्क और सबटास्क
* टास्क संग्रह के रूप में प्रोजेक्ट
* ऑफिस मेमो को टास्क या प्रोजेक्ट में परिवर्तित करना
* चैट, फाइलें, रिमाइंडर, टैग
* व्यक्तिगत और टीम टास्क असाइनमेंट

🔗 [कार्य सुविधाएँ](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md)

---

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Analytical crm report" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)

### एनालिटिक्स एप्लिकेशन (Analytical CRM)

कार्यान्वयन योग्य अंतर्दृष्टि के लिए अंतर्निहित **CRM एनालिटिक्स सॉफ्टवेयर**:

* सेल्स फनल विश्लेषण
* आय सारांश रिपोर्ट
* लीड स्रोत विश्लेषण
* अनुरोध सारांश

🔗 [एनालिटिक्स ऐप ओवरव्यू](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md)

---

### मेलिंग CRM एवं ईमेल मार्केटिंग

मेलिंग CRM में पूर्ण **CRM और ईमेल मार्केटिंग सॉफ्टवेयर** मॉड्यूल शामिल है:

* ईमेल खाते (SMTP / IMAP)
* ईमेल कैंपेन और न्यूज़लेटर
* डायनामिक टेम्पलेट्स
* ईमेल हस्ताक्षर
* संपर्क विभाजन (सेगमेंटेशन)

यह Django-CRM को ईमेल इंटीग्रेशन और आंतरिक ईमेल क्लाइंट के साथ CRM के रूप में उपयुक्त बनाता है।

---

## ईमेल क्लाइंट एवं इंटीग्रेशन

अंतर्निहित **ईमेल क्लाइंट** निम्नलिखित का समर्थन करता है:

* SMTP और IMAP
* Gmail और अन्य प्रदाता
* OAuth 2.0 (दो-स्तरीय प्रमाणीकरण)
* स्वचालित ईमेल सिंक्रोनाइजेशन

सभी पत्राचार:

* CRM डेटाबेस में संग्रहीत
* अनुरोधों, लीड्स और डील्स से लिंक
* टिकट-शैली तंत्र के माध्यम से व्यवस्थित

---

## अतिरिक्त कार्यक्षमता

* reCAPTCHA v3 के साथ वेब फ़ॉर्म इंटीग्रेशन
* स्वचालित जियोलोकेशन
* VoIP कॉल-बैक समर्थन
* मैसेंजर इंटीग्रेशन (WhatsApp, Viber आदि)
* Excel आयात/निर्यात
* संदर्भ-संवेदनशील सहायता पृष्ठ
* टूलटिप्स और इनलाइन डॉक्यूमेंटेशन

---

## बहुभाषी एवं लोकलाइज़ेशन समर्थित

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="django logo" width="30" height="30" style="vertical-align: bottom"> उपलब्ध इंटरफ़ेस भाषाएँ:

`ar, cs, de, el, en, es, fr, he, hi, id, it, ja, ko, nl, pl, pt-br, ro, ru, tr, uk, vi, zh-hans`

पूर्ण समर्थन:

* अनुवाद
* टाइम ज़ोन
* लोकल-विशिष्ट तिथि और समय प्रारूप

---

## यह निःशुल्क CRM क्यों चुनें?

* ✅ निःशुल्क ग्राहक संबंध प्रबंधन सॉफ्टवेयर
* ✅ पूर्णतः self-hosted
* ✅ Python एवं Django आधारित
* ✅ CRM, टास्क, ईमेल और एनालिटिक्स एक ही सिस्टम में
* ✅ SMBs, एजेंसियों और एंटरप्राइज आंतरिक टूल्स के लिए उपयुक्त
* ✅ कोई SaaS शुल्क या vendor lock-in नहीं

---

## शुरुआत कैसे करें

Django-CRM एक मानक Django प्रोजेक्ट की तरह चलता है।

परीक्षण और मूल्यांकन के लिए:

* किसी बाहरी डेटाबेस की आवश्यकता नहीं
* SQLite डिफ़ॉल्ट रूप से उपलब्ध

📘 दस्तावेज़ीकरण:

* इंस्टॉलेशन एवं कॉन्फ़िगरेशन गाइड
* उपयोगकर्ता मार्गदर्शिका
* ऑनलाइन दस्तावेज़ीकरण
* चेंजलॉग

---

## संगतता

* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Django 6.0+
* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="python logo" width="30" height="30" style="vertical-align: middle"> Python 3.12+
* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="mysql logo" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30" style="vertical-align: middle"> PostgreSQL 14+

Django 5.2.11 LTS के साथ संगत CRM संस्करण [अलग](https://github.com/DjangoCRM/django-crm/tree/v1.7.x-LTS) से उपलब्ध है।

---

## योगदान

फीचर्स, सुधार और डॉक्यूमेंटेशन अपडेट का स्वागत है।

📄 कृपया [योगदान गाइड](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md) देखें।

---

## लाइसेंस

**AGPL-3.0** लाइसेंस के अंतर्गत जारी।
अधिक जानकारी के लिए [LICENSE](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE) फ़ाइल देखें।

---

## ओपन सोर्स का समर्थन करें ❤️

यदि यह प्रोजेक्ट आपके लिए उपयोगी है, तो कृपया GitHub पर इस रिपॉजिटरी को ⭐ star करें — इससे अन्य उपयोगकर्ताओं को इस निःशुल्क Python CRM को खोजने में सहायता मिलती है।
