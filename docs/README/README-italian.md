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

*(Software collaborativo e analitico per la gestione delle relazioni con i clienti)*

**Django-CRM** è una soluzione CRM open source progettata con due obiettivi principali:

- **Per gli utenti**: fornisci software CRM open source di livello aziendale con una suite completa di soluzioni aziendali.  
- **Per sviluppatori**: semplifica i processi di sviluppo, personalizzazione e supporto del server di produzione.

**Non è necessario apprendere un framework proprietario**: tutto è creato utilizzando il popolare framework Django.  
CRM sfrutta appieno anche il sito Django Admin, con la documentazione tutta contenuta in un'unica pagina web!

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Screenshot Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

## Funzionalità di gestione delle relazioni con i clienti
|                              |                                          |                                  |
|------------------------------|------------------------------------------|----------------------------------|
| ☑️ **Attività e progetti del team** | ☑️ **Gestione dei contatti**                   | ☑️ **Marketing tramite posta elettronica**           |
| ☑️ **Gestione dei contatti**    | ☑️ **Monitoraggio delle trattative e previsione delle vendite** | ☑️ **Controllo degli accessi basato sui ruoli** |
| ☑️ **Analisi delle vendite**       | ☑️ **Integrazione chat interna**         | ☑️ **Design ottimizzato per dispositivi mobili**    |
| ☑️ **Rapporti personalizzabili**  | ☑️ **Sincronizzazione automatica della posta elettronica**              | ☑️ **Supporto multivaluta**    |

Scopri di più sulle [capacità del software](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md).

Django CRM è un software di gestione delle relazioni con i clienti open source. Questo CRM è scritto in  <a href="https://www.python.org" target="_blank"><img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" style="vertical-align: middle" alt="python logo" width="25" height="25"> Python</a>.  
Frontend e backend sono interamente basati sul [sito di amministrazione](https://docs.djangoproject.com/en/dev/ref/contrib/admin/) di Django.  
L'app CRM utilizza modelli HTML di amministrazione adattivi pronti all'uso.  
Django è un framework ottimamente documentato con molti esempi.  
La documentazione sul sito di amministrazione occupa solo una pagina web.  
💡 L'**idea originale** è che, poiché il sito di Amministrazione di Django è già un'interfaccia professionale di gestione degli oggetti con un sistema di permessi flessibile per gli utenti (visualizzazione, modifica, aggiunta ed eliminazione di oggetti), tutto ciò che devi fare è creare modelli per gli oggetti (come Lead, Richieste, Offerte, Aziende, ecc.) e aggiungi logica di progetto.

Tutto ciò garantisce:

- personalizzazione e sviluppo del progetto notevolmente più semplici
- Implementazione del progetto più semplice e supporto del server di produzione

Il pacchetto software fornisce due siti Web:

- Sito CRM per tutti gli utenti
- sito per gli amministratori

Il **progetto è maturo e stabile** e viene utilizzato con successo in applicazioni reali da molti anni.

## Applicazioni principali

La suite software CRM è composta dalle seguenti **applicazioni principali** e dai relativi modelli:

- **App Gestione ATTIVITÀ**:
  (disponibile per tutti gli utenti per impostazione predefinita, indipendentemente dal loro ruolo)
  - Attività (con relativi: file, chat, promemoria, tag - vedi [caratteristiche task](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md))
    - attività secondarie
  - Memo (memo d'ufficio) - vedi [caratteristiche memo](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)
    - Attività / progetto
  - Progetto (*raccolta attività*):
  - ... (+ *4 altri <a href="https://github.com/DjangoCRM/django-crm/tree/main/tasks/models" target="_blank">modelli</a>*)
- **App CRM**:
  - Richieste (richieste commerciali)
  - Lead (potenziali clienti)
  - Aziende
  - Persone di contatto (associate alle loro aziende)
  - Offerte (come "Opportunità")
  - Messaggi e-mail (sincronizzazione con gli account e-mail degli utenti)
  - Prodotti (beni e servizi)
  - Pagamenti (ricevuti, garantiti, ad alta e bassa probabilità)
  - ...(*+ altri 12 <a href="https://github.com/DjangoCRM/django-crm/tree/main/crm/models" target="_blank">modelli</a>*)
[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Analytical crm report" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)
- **App ANALYTICS**: ([panoramica dettagliata del software](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md))
  - Rapporto riepilogativo delle entrate (*vedi [screenshot](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)*)
  - Rapporto sulla canalizzazione delle vendite
  - Rapporto di riepilogo della fonte principale
  - ... (+ *altri 5 report analitici*)
- **App POSTA DI MASSA**:
  - Account di posta elettronica
  - Messaggi e-mail (newsletter)
  - Firme e-mail (firme utente)
  - Invii

## Applicazioni di supporto

Il pacchetto CRM contiene anche **applicazioni di supporto** come:

- App di chat (la chat è disponibile in ogni istanza di un'attività, progetto, promemoria dell'ufficio offerte)
- App VoIP (contatta i clienti per le offerte)
- App di aiuto (pagine di aiuto dinamiche a seconda del ruolo dell'utente)
- Applicazione comune:
  - 🪪 Profili utente
  - ⏰ Promemoria (per attività, progetti, promemoria di ufficio e offerte)
  - 📝 Tag (per attività, progetti, promemoria d'ufficio e offerte)
  - 📂 File (per attività, progetti, promemoria di ufficio e offerte)

## Funzionalità aggiuntive

- Integrazione del modulo Web: il modulo di contatto CRM ha integrato:
  - Protezione reCAPTCHA v3
  - geolocalizzazione automatica
- Integrazione e sincronizzazione dell'account e-mail dell'utente. I messaggi email sono automatici:
  - salvato nel database CRM
  - collegati agli oggetti CRM appropriati (come: richieste, lead, offerte, ecc.)
- Servizio di richiamata VoIP sullo smartphone
- Invio di messaggi tramite messenger (come: Viber, WhatsApp, ...)
- Supporto Excel: importa/esporta facilmente i dettagli dei contatti.

## Client di posta elettronica

Il sistema Python CRM include un client di posta elettronica integrato che funziona utilizzando i protocolli **SMTP** e **IMAP**.  
Ciò consente a Django-CRM di archiviare automaticamente copie di tutta la corrispondenza relativa a ciascuna richiesta e transazione all'interno del suo database.  
La funzionalità garantisce che anche se le comunicazioni avvengono tramite l'account di posta elettronica esterno dell'utente (al di fuori del CRM).  
Vengono acquisiti e organizzati all'interno del sistema utilizzando un **meccanismo di ticketing**.

Il CRM può integrarsi con i provider di servizi di posta elettronica (come Gmail) che richiedono l'autenticazione obbligatoria in due passaggi (utilizzando il protocollo **OAuth 2.0**) per applicazioni di terze parti.

## Assistenza all'utente  

- Ogni pagina CRM include un collegamento a una pagina di aiuto sensibile al contesto, con contenuti adattati dinamicamente al ruolo dell'utente per una guida più pertinente.  
- Le descrizioni comandi sono disponibili in tutta l'interfaccia e forniscono informazioni istantanee quando si passa sopra elementi come icone, pulsanti, collegamenti o intestazioni di tabella.  
- Una [guida per l'utente] completa(https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md) è incluso anche un file per riferimento e supporto approfonditi.

## Aumenta la produttività del tuo team con soluzioni CRM collaborative

Questo CRM è progettato per migliorare la collaborazione all'interno dei team e semplificare i processi di gestione dei progetti.  
In quanto CRM collaborativo, consente agli utenti di creare e gestire facilmente promemoria, attività e progetti.  
[Promemoria di ufficio](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md) possono essere indirizzate a capi reparto o dirigenti aziendali, che potranno poi trasformare tali promemoria in incarichi o progetti, assegnandovi responsabili o esecutori.  
[Attività](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md) può essere individuale o collettivo.  
Le attività forniscono funzionalità come discussioni in chat, promemoria, condivisione di file, creazione di attività secondarie e condivisione di risultati.  
Gli utenti ricevono notifiche direttamente nel CRM e via e-mail, assicurandosi che rimangano informati.  
Ogni utente ha una visione chiara della propria serie di attività, comprese priorità, stati e passaggi successivi, migliorando così la produttività e la responsabilità nella gestione collaborativa delle relazioni con i clienti.

## Localizzazione del progetto

Django CRM ha il supporto completo per la traduzione dell'interfaccia, la formattazione di date, orari e fusi orari.
<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Il software del servizio clienti è ora disponibile in **più lingue:**  
`de, en, es, fr, it, nl, pt-BR, ru, uk`

## Perché scegliere Django-CRM?

- **CRM collaborativo**: aumenta la produttività del team con strumenti per la gestione delle attività, la collaborazione sui progetti e la comunicazione interna.
- **CRM analitico**: ottieni informazioni utili con report integrati come canalizzazione delle vendite, riepilogo dei ricavi e analisi delle fonti di lead.
- **Basato su Python e Django**: non sono richiesti framework proprietari: tutto è basato su Django con un'interfaccia di amministrazione intuitiva.

## Iniziare

Se trovi utile Django-CRM, metti una ⭐️ **stella** a questo repository su GitHub per supportarne la crescita!

Django-CRM può essere facilmente distribuito come un normale progetto Django.

📚 Si prega di fare riferimento a:

- [Guida all'installazione e alla configurazione](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
- [Guida per l'utente](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)

### Compatibilità

- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Django 5.1.x
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="python logo" width="30" height="30" style="vertical-align: middle"> Python 3.10+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="mysql logo" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30" style="vertical-align: middle"> PostgreSQL 12+  


## Contribuire

I contributi sono benvenuti! C'è spazio per miglioramenti e nuove funzionalità.  
Dai un'occhiata alla nostra [Guida per contribuire](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md) per sapere come iniziare.  
Ogni contributo, grande o piccolo, fa la differenza.

## Licenza

Django-CRM è rilasciato sotto la licenza AGPL-3.0 - vedere la [LICENZA](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE) file per i dettagli.

## Crediti

- Materiale Google [icone](https://fonts.google.com/icons).
- [NicEdit](https://nicedit.com) - Editor di contenuti WYSIWYG.
