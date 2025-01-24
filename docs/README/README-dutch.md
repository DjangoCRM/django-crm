
<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/README.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-spanish.md">Español</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-portuguese.md">Português</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-french.md">Français</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-german.md">Deutsch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-dutch.md">Dutch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-italian.md">Italiano</a>
</p>

# Django-CRM

*(Collaboratieve en Analytische Klantrelatiebeheer Software)*

**Django-CRM** is een open-source CRM-oplossing ontworpen met twee primaire doelen:

- **Voor gebruikers**: Biedt enterprise-level open-source CRM-software met een uitgebreide suite van zakelijke oplossingen.
- **Voor ontwikkelaars**: Vereenvoudig de processen van ontwikkeling, aanpassing en productie serverondersteuning.

**Geen noodzaak om een propriëtair framework te leren**: alles is gebouwd met behulp van het populaire Django-framework.
CRM maakt ook volledig gebruik van de Django Admin-site, met documentatie die allemaal op één webpagina is opgenomen!

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Screenshot Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

## Klantrelatiebeheer Functies

|                               |                                          |                                       |
|-------------------------------|------------------------------------------|---------------------------------------|
| ☑️ **Team Taken & Projecten** | ☑️ **Leadbeheer**                        | ☑️ **E-mailmarketing**                |
| ☑️ **Contactbeheer**          | ☑️ **Deal Tracking & Verkoopprognoses**  | ☑️ **Rolgebaseerde Toegangscontrole** |
| ☑️ **Verkoopanalyses**        | ☑️ **Interne Chat Integratie**           | ☑️ **Mobielvriendelijk Ontwerp**      |
| ☑️ **Aanpasbare Rapporten**   | ☑️ **Automatische E-mail Sync**          | ☑️ **Multi-Valuta Ondersteuning**     |

Lees meer over [de mogelijkheden van de software](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md).

Django CRM is een open-source klantrelatiebeheer software. Deze CRM is geschreven in <a href="https://www.python.org" target="_blank"><img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" style="vertical-align: middle" alt="python logo" width="25" height="25"> Python</a>.
Frontend en backend zijn volledig gebaseerd op de Django [Admin site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/).  
De CRM-app gebruikt adaptieve Admin HTML-sjablonen out-of-the-box.  
Django is een uitstekend gedocumenteerd framework met veel voorbeelden.
De documentatie op de Admin-site neemt slechts één webpagina in beslag.  
💡 Het **oorspronkelijke idee** is dat aangezien Django Admin al een professionele objectbeheer interface is met een flexibel permissiesysteem voor gebruikers (bekijken, wijzigen, toevoegen en verwijderen van objecten), alles wat je hoeft te doen is modellen maken voor de objecten (zoals Leads, Verzoeken, Deals, Bedrijven, enz.) en bedrijfslogica toevoegen.

Dit alles zorgt voor:

- aanzienlijk eenvoudigere projectaanpassing en ontwikkeling
- eenvoudigere projectimplementatie en productie serverondersteuning

Het softwarepakket biedt twee websites:

- CRM-site voor alle gebruikers
- site voor beheerders

Het **project is volwassen en stabiel**, en is al vele jaren succesvol gebruikt in echte toepassingen.

## Hoofdtoepassingen

De CRM-software suite bestaat uit de volgende **hoofdtoepassingen** en hun modellen:

- **TAKEN Beheer app**:
  (beschikbaar voor alle gebruikers standaard, ongeacht hun rol)
  - Taak (met gerelateerde: bestanden, chat, herinneringen, tags - zie [taakfuncties](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md))
    - subtaken
  - Memo (kantoormemo) - zie [memo functies](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)
    - taken / project
  - Project (*takenverzameling*):
  - ... (+ *4 meer <a href="https://github.com/DjangoCRM/django-crm/tree/main/tasks/models" target="_blank">modellen</a>*)
- **CRM app**:
  - Verzoeken (commerciële aanvragen)
  - Leads (potentiële klanten)
  - Bedrijven
  - Contactpersonen (geassocieerd met hun bedrijven)
  - Deals (zoals "Kansen")
  - E-mailberichten (sync met gebruikers e-mailaccounts)
  - Producten (goederen en diensten)
  - Betalingen (ontvangen, gegarandeerd, hoge en lage waarschijnlijkheid)
  - ... (*+ 12 meer <a href="https://github.com/DjangoCRM/django-crm/tree/main/crm/models" target="_blank">modellen</a>*)
[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Analytisch crm rapport" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)
- **ANALYTICS app**: ([gedetailleerd softwareoverzicht](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md))
  - Inkomensoverzicht rapport (*zie [screenshot](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)*)
  - Verkoopfunnel rapport
  - Leadbron Samenvatting rapport
  - ... (+ *5 meer analytische rapporten*)
- **MASS MAIL app**:
  - E-mailaccounts
  - E-mailberichten (nieuwsbrieven)
  - E-mailsignaturen (gebruikershandtekeningen)
  - Mailings

## Ondersteunende Toepassingen

Het CRM-pakket bevat ook **ondersteunende toepassingen** zoals:

- Chat app (chat is beschikbaar in elke instantie van een taak, project, kantoormemo en deal)
- VoIP app (contacteer klanten vanuit deals)
- Help app (dynamische helppagina's afhankelijk van gebruikersrol)
- Gemeenschappelijke app:
  - 🪪 Gebruikersprofielen
  - ⏰ Herinneringen (voor taken, projecten, kantoormemo's en deals)
  - 📝 Tags (voor taken, projecten, kantoormemo's en deals)
  - 📂 Bestanden (voor taken, projecten, kantoormemo's en deals)

## Extra Functionaliteit

- Webformulier integratie: CRM contactformulier heeft ingebouwde:
  - reCAPTCHA v3 bescherming
  - automatische geolocatie
- Integratie en synchronisatie van gebruikers e-mailaccount. E-mailberichten worden automatisch:
  - opgeslagen in de CRM-database
  - gekoppeld aan de juiste CRM-objecten (zoals: verzoeken, leads, deals, enz.)
- VoIP terugbellen naar smartphone
- Berichten verzenden via messengers (zoals: Viber, WhatsApp, ...)
- Excel Ondersteuning: Importeer/exporteer contactgegevens met gemak.

## E-mailclient

Het Python CRM-systeem bevat een ingebouwde e-mailclient die werkt met **SMTP** en **IMAP** protocollen.
Dit stelt Django-CRM in staat om automatisch kopieën van alle correspondentie met betrekking tot elk verzoek en deal in zijn database op te slaan.
De functionaliteit zorgt ervoor dat zelfs als communicatie plaatsvindt via het externe e-mailaccount van de gebruiker (buiten de CRM).
Ze worden vastgelegd en georganiseerd binnen het systeem met behulp van een **ticketing mechanisme**.  
De CRM kan integreren met e-mailserviceproviders (zoals Gmail) die verplichte tweestapsverificatie vereisen (met behulp van het **OAuth 2.0** protocol) voor toepassingen van derden.

## Gebruikershulp

- Elke CRM-pagina bevat een link naar een contextgevoelige helppagina, met inhoud die dynamisch is afgestemd op de rol van de gebruiker voor relevantere begeleiding.
- Tooltips zijn beschikbaar in de hele interface en bieden directe informatie wanneer u over elementen zoals pictogrammen, knoppen, links of tabelkoppen zweeft.
- Een uitgebreide [gebruikershandleiding](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md) is ook inbegrepen voor diepgaande referentie en ondersteuning.

## Verhoog de Productiviteit van Uw Team met Collaboratieve CRM-oplossingen

Deze CRM is ontworpen om samenwerking binnen teams te verbeteren en projectmanagementprocessen te stroomlijnen.
Als een collaboratieve CRM stelt het gebruikers in staat om memo's, taken en projecten met gemak te creëren en te beheren.
[Kantoormemo's](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md) kunnen worden gericht aan afdelingshoofden of bedrijfsleiders, die deze memo's vervolgens kunnen omzetten in taken of projecten en verantwoordelijke personen of uitvoerders kunnen toewijzen.
[Taken](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md) kunnen individueel of collectief zijn.
Taken bieden functies zoals chat discussies, herinneringen, bestandsdeling, het maken van subtaken en het delen van resultaten.
Gebruikers ontvangen meldingen direct in de CRM en via e-mail, zodat ze op de hoogte blijven.
Elke gebruiker heeft een duidelijk overzicht van zijn takenstapel, inclusief prioriteiten, statussen en volgende stappen, wat de productiviteit en verantwoordelijkheid in collaboratief klantrelatiebeheer verbetert.

## Projectlokalisatie

Django CRM heeft volledige ondersteuning voor vertaling van interface, formattering van data, tijden en tijdzones.  
<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Klantenservice software is nu beschikbaar in **meerdere talen**:  
`de, en, es, fr, it, nl, pt-BR, ru, uk`

## Waarom Kiezen voor Django-CRM?

- **Collaboratieve CRM**: Verhoog de productiviteit van het team met tools voor taakbeheer, project samenwerking en interne communicatie.
- **Analytische CRM**: Verkrijg bruikbare inzichten met ingebouwde rapporten zoals verkoopfunnel, inkomensoverzicht en leadbron analyse.
- **Python en Django-gebaseerd**: Geen propriëtaire frameworks vereist - alles is gebouwd op Django met een intuïtieve Admin-interface.

## Aan de Slag

Als u Django-CRM nuttig vindt, geef dan ⭐️ **een ster** aan deze repo op GitHub om de groei te ondersteunen!

Django-CRM kan eenvoudig worden geïmplementeerd als een regulier Django-project.

📚 Raadpleeg:

- [Installatie- en Configuratiehandleiding](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
- [Gebruikershandleiding](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)

### Compatibiliteit

- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Django 5.1.x
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="python logo" width="30" height="30" style="vertical-align: middle"> Python 3.10+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="mysql logo" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30" style="vertical-align: middle"> PostgreSQL 12+

## Bijdragen

Bijdragen zijn welkom! Er is ruimte voor verbeteringen en nieuwe functies.
Bekijk onze [Bijdragegids](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md) om te leren hoe u kunt beginnen.
Elke bijdrage, groot of klein, maakt een verschil.

## Licentie

Django-CRM wordt uitgebracht onder de AGPL-3.0-licentie - zie het [LICENSE](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE) bestand voor details.

## Credits

- Google material [icons](https://fonts.google.com/icons).
- [NicEdit](https://nicedit.com) - WYSIWYG Content Editor.
