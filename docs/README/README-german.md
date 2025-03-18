<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/README.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-hindi.md">हिन्दी</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-spanish.md">Español</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-chinese.md">中文</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-portuguese.md">Português</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-arabic.md">اَلْعَرَبِيَّةُ</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-french.md">Français</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-german.md">Deutsch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-dutch.md">Nederlands</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-italian.md">Italiano</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-ukrainian.md">Українська</a>
</p>

# Django-CRM

*(Kollaborative und analytische Kundenbeziehungsmanagement-Software)*

**Django-CRM** ist eine Open-Source-CRM-Lösung, die mit **zwei Hauptzielen** entwickelt wurde:

- **Für Benutzer**: Bereitstellung von Open-Source-CRM-Software auf Unternehmensebene mit einer umfassenden Suite von Geschäftslösungen.
- **Für Entwickler**: Vereinfachung der Entwicklungs-, Anpassungs- und Produktionsserverunterstützungsprozesse.

**Keine Notwendigkeit, ein proprietäres Framework zu erlernen**: Alles ist mit dem beliebten Django-Framework aufgebaut.
CRM nutzt auch die Vorteile der Django-Admin-Site, wobei die Dokumentation auf einer einzigen Webseite enthalten ist!

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Screenshot Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

## Funktionen des Kundenbeziehungsmanagements

|                                 |                                             |                                             |
|---------------------------------|---------------------------------------------|---------------------------------------------|
| ☑️ **Teamaufgaben & Projekte**  | ☑️ **Lead-Management**                      | ☑️ **E-Mail-Marketing**                     |
| ☑️ **Kontaktmanagement**        | ☑️ **Deal-Tracking & Verkaufsprognosen**    | ☑️ **Rollenbasierte Zugriffskontrolle**     |
| ☑️ **Verkaufsanalysen**         | ☑️ **Interne Chat-Integration**             | ☑️ **Mobilfreundliches Design**             |
| ☑️ **Anpassbare Berichte**      | ☑️ **Automatische E-Mail-Synchronisierung** | ☑️ **Unterstützung für mehrere Währungen**  |

Erfahren Sie mehr über [die Fähigkeiten der Software](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md).

Django CRM ist eine Open-Source-Software für das Kundenbeziehungsmanagement.
Dieses CRM ist in <a href="https://www.python.org" target="_blank"><img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" style="vertical-align: bottom" alt="python logo" width="25" height="25"> Python</a> geschrieben.
Frontend und Backend basieren vollständig auf der [Django-Admin-Site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/).
Die CRM-App verwendet adaptive Admin-HTML-Vorlagen direkt aus der Box.
Django ist ein hervorragend dokumentiertes Framework mit vielen Beispielen.
Die Dokumentation auf der Admin-Site nimmt nur eine Webseite ein.
💡 Die **ursprüngliche Idee** ist, dass, da die Django-Admin-Site bereits eine professionelle Objektverwaltungsoberfläche mit einem flexiblen Berechtigungssystem für Benutzer (Anzeigen, Ändern, Hinzufügen und Löschen von Objekten) ist, alles, was Sie tun müssen, ist, Modelle für die Objekte (wie Leads, Anfragen, Deals, Unternehmen usw.) zu erstellen und Geschäftslogik hinzuzufügen.

**All dies gewährleistet**:

- **deutlich einfachere Projektanpassung und -entwicklung**
- **einfachere Projektbereitstellung und Produktionsserverunterstützung**

Das Softwarepaket bietet zwei Websites:

1. CRM-Site für alle Benutzer
2. Site für Administratoren

Das **Projekt ist ausgereift und stabil** und wird seit vielen Jahren erfolgreich in realen Anwendungen eingesetzt.

## Hauptanwendungen

Die CRM-Software-Suite besteht aus den folgenden **Hauptanwendungen** und ihren Modellen:

- **TASKS-Management-App**:
  (standardmäßig für alle Benutzer verfügbar, unabhängig von ihrer Rolle)
  - Aufgabe (mit zugehörigen: Dateien, Chat, Erinnerungen, Tags - siehe [Aufgabenfunktionen](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md))
    - Unteraufgaben
  - Memo (Büromemo) - siehe [Memofunktionen](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)
    - Aufgaben / Projekt
  - Projekt (*Aufgabensammlung*):
  - ... (+ *4 weitere <a href="https://github.com/DjangoCRM/django-crm/tree/main/tasks/models" target="_blank">Modelle</a>*)
- **CRM-App**:
  - Anfragen (kommerzielle Anfragen)
  - Leads (potenzielle Kunden)
  - Unternehmen
  - Kontaktpersonen (mit ihren Unternehmen verbunden)
  - Deals (wie "Opportunities")
  - E-Mail-Nachrichten (Synchronisierung mit Benutzer-E-Mail-Konten)
  - Produkte (Waren und Dienstleistungen)
  - Zahlungen (erhalten, garantiert, hohe und niedrige Wahrscheinlichkeit)
  - ... (*+ 12 weitere <a href="https://github.com/DjangoCRM/django-crm/tree/main/crm/models" target="_blank">Modelle</a>*)
[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Analytischer CRM-Bericht" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)
- **ANALYTICS-App**: ([detaillierte Softwareübersicht](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md))
  - Einkommensübersicht-Bericht (*siehe [Screenshot](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)*)
  - Verkaufs-Trichter-Bericht
  - Lead-Quellen-Übersicht-Bericht
  - ... (+ *5 weitere analytische Berichte*)
- **MASS MAIL-App**:
  - E-Mail-Konten
  - E-Mail-Nachrichten (Newsletter)
  - E-Mail-Signaturen (Benutzersignaturen)
  - Mailings

## Unterstützende Anwendungen

Das CRM-Paket enthält auch **unterstützende Anwendungen** wie:

- Chat-App (Chat ist in jeder Instanz einer Aufgabe, eines Projekts, eines Büromemos und eines Deals verfügbar)
- VoIP-App (Kontaktaufnahme mit Kunden aus Deals)
- Hilfe-App (dynamische Hilfeseiten je nach Benutzerrolle)
- Common-App:
  - 🪪 Benutzerprofile
  - ⏰ Erinnerungen (für Aufgaben, Projekte, Büromemos und Deals)
  - 📝 Tags (für Aufgaben, Projekte, Büromemos und Deals)
  - 📂 Dateien (für Aufgaben, Projekte, Büromemos und Deals)

## Zusätzliche Funktionalität

- Webformular-Integration: Das CRM-Kontaktformular hat eingebaut:
  - reCAPTCHA v3-Schutz
  - automatische Geolokalisierung
- Integration und Synchronisierung des E-Mail-Kontos des Benutzers. E-Mail-Nachrichten werden automatisch:
  - in der CRM-Datenbank gespeichert
  - den entsprechenden CRM-Objekten zugeordnet (wie: Anfragen, Leads, Deals usw.)
- VoIP-Rückruf zum Smartphone
- Nachrichtenversand über Messenger (wie: Viber, WhatsApp, ...)
- Excel-Unterstützung: Import/Export von Kontaktdaten mit Leichtigkeit.

## E-Mail-Client

Das Python-CRM-System enthält einen integrierten E-Mail-Client, der **SMTP**- und **IMAP**-Protokolle verwendet.
Dies ermöglicht es Django-CRM, automatisch Kopien aller Korrespondenz, die sich auf jede Anfrage und jeden Deal bezieht, in seiner Datenbank zu speichern.
Die Funktionalität stellt sicher, dass selbst wenn die Kommunikation über das externe E-Mail-Konto des Benutzers (außerhalb des CRM) erfolgt.
Sie werden im System erfasst und organisiert, indem ein **Ticketing-Mechanismus** verwendet wird.

Das CRM kann sich mit E-Mail-Dienstanbietern (wie Gmail) integrieren, die eine obligatorische Zwei-Faktor-Authentifizierung (unter Verwendung des **OAuth 2.0**-Protokolls) für Drittanbieteranwendungen erfordern.

## Benutzerunterstützung

- Jede CRM-Seite enthält einen Link <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/question-mark.svg" alt="Fragezeichen-Symbol" style="vertical-align: bottom" width="25" height="25"> zu einer kontextbezogenen Hilfeseite, deren Inhalt dynamisch auf die Benutzerrolle zugeschnitten ist, um relevantere Anleitungen zu bieten.
- Tooltips sind im gesamten Interface verfügbar und bieten sofortige Informationen, wenn Sie über Elemente wie Symbole, Schaltflächen, Links oder Tabellenüberschriften fahren.
- Eine umfassende [Benutzeranleitung](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md) ist ebenfalls enthalten, um eine eingehende Referenz und Unterstützung zu bieten.

## Steigern Sie die Produktivität Ihres Teams mit kollaborativen CRM-Lösungen

Dieses CRM ist darauf ausgelegt, die Zusammenarbeit innerhalb von Teams zu verbessern und Projektmanagementprozesse zu optimieren.
Als kollaboratives CRM ermöglicht es Benutzern, Memos, Aufgaben und Projekte mit Leichtigkeit zu erstellen und zu verwalten.
[Büromemos](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md) können an Abteilungsleiter oder Unternehmensleiter gerichtet werden, die diese Memos dann in Aufgaben oder Projekte umwandeln und verantwortliche Personen oder Ausführende zuweisen können.
[Aufgaben](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md) können individuell oder kollektiv sein.
Aufgaben bieten Funktionen wie Chat-Diskussionen, Erinnerungen, Dateifreigabe, Erstellung von Unteraufgaben und Ergebnisfreigabe.
Benutzer erhalten Benachrichtigungen direkt im CRM und per E-Mail, um sicherzustellen, dass sie informiert bleiben.
Jeder Benutzer hat einen klaren Überblick über seinen Aufgabenstapel, einschließlich Prioritäten, Status und nächster Schritte, was die Produktivität und Verantwortlichkeit im kollaborativen Kundenbeziehungsmanagement verbessert.

## Projektlokalisierung

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="django logo" width="30" height="30" style="vertical-align: bottom"> Die Kundenservice-Software ist jetzt in **vielen Sprachen** verfügbar:

`ar, cs, de, el, en, es, fr, he, hi, id, it, ja, ko, nl, pl, pt-br, ro, ru, tr, uk, vi, zh-hans`

Django CRM unterstützt vollständig die Übersetzung der Benutzeroberfläche sowie die Formatierung von Daten, Zeiten und Zeitzonen.

## Warum Django-CRM wählen?

- **Selbst-Hosting**: Die CRM-Anwendungssoftware ist so konzipiert, dass sie selbst gehostet werden kann, sodass Sie die volle Kontrolle über Ihre CRM-Daten und -Umgebung haben. Durch das Selbst-Hosting können Sie das CRM an Ihre spezifischen Geschäftsanforderungen anpassen und sicherstellen, dass Ihre Daten privat und sicher bleiben.
- **Kollaboratives CRM**: Steigern Sie die Produktivität Ihres Teams mit Tools für Aufgabenmanagement, Projektzusammenarbeit und interne Kommunikation.
- **Analytisches CRM**: Gewinnen Sie umsetzbare Erkenntnisse mit integrierten Berichten wie Verkaufs-Trichter, Einkommensübersicht und Lead-Quellen-Analyse.
- **Python- und Django-basiert**: Es ist nicht erforderlich, ein proprietäres Framework zu erlernen - alles basiert auf Django mit einer intuitiven Admin-Oberfläche. Das Frontend und Backend, basierend auf Django Admin, erleichtern die Anpassung und Entwicklung von Projekten sowie die Bereitstellung und Wartung eines Produktionsservers erheblich.


## Erste Schritte

Django-CRM kann einfach als reguläres Django-Projekt bereitgestellt werden.

📚 Bitte beachten Sie:

- [Installations- und Konfigurationshandbuch](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
- [Benutzerhandbuch](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)

Wenn Sie Django-CRM hilfreich finden, bitte ⭐️ **markieren** Sie dieses Repository auf GitHub, um sein Wachstum zu unterstützen!

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/Django-CRM_star_history.png" alt="Django-CRM Sternverlauf" align="center" style="float: center"/>

### Kompatibilität

- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Django 5.1.x
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="python logo" width="30" height="30" style="vertical-align: middle"> Python 3.10+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="mysql logo" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30" style="vertical-align: middle"> PostgreSQL 12+  

## Mitwirken

Beiträge sind willkommen! Es gibt Raum für Verbesserungen und neue Funktionen.
Schauen Sie sich unseren [Leitfaden für Mitwirkende](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md) an, um zu erfahren, wie Sie loslegen können.
Jeder Beitrag, ob groß oder klein, macht einen Unterschied.

## Lizenz

Django-CRM wird unter der AGPL-3.0-Lizenz veröffentlicht - siehe die [LICENSE](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE)-Datei für Details.

## Danksagungen

- Google Material [Icons](https://fonts.google.com/icons).
- [NicEdit](https://nicedit.com) - WYSIWYG-Content-Editor.
- Alle Ressourcen, die unter anderen Lizenzen verwendet werden.
