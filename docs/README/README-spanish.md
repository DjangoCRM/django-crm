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

## CRM Python Open-Source Gratuito con Gestión de Tareas, Email Marketing y Analítica

**Django CRM** es un software gratuito de gestión de relaciones con clientes (CRM) desarrollado con [Python](https://www.python.org) y [Django](https://www.djangoproject.com), diseñado para equipos que necesitan un CRM autohospedado, gestor de tareas CRM, mailing CRM y software de analítica CRM en una única plataforma extensible.

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Captura de pantalla Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

**Estado del proyecto:** Producción / Estable
Utilizado en entornos empresariales reales durante muchos años.

⭐️ Si este proyecto te resulta útil, **por favor marca el repositorio con una estrella** — ayuda a que otros descubran este CRM Python gratuito y de código abierto.

---

## ¿Por qué Django-CRM?

Django CRM combina CRM y software de gestión de tareas, CRM con integración de correo electrónico, y CRM con email marketing, sin frameworks propietarios, sin dependencia de proveedores (vendor lock-in) ni limitaciones SaaS.

### Para empresas y usuarios finales

* Gestiona **leads, oportunidades, contactos, tareas, proyectos y campañas de email** en un solo sistema
* Sustituye múltiples herramientas por un **CRM colaborativo único**
* Obtén información estratégica con el **software de analítica CRM integrado**

### Para desarrolladores e integradores

* CRM 100% Python basado en el framework Django
* Sin capa de interfaz propietaria — todo funciona sobre [Django Admin](https://docs.djangoproject.com/en/dev/ref/contrib/admin/)
* Personalización rápida, actualizaciones predecibles y despliegues sencillos
* Ideal para **CRM autohospedado** e instalaciones on-premise

---

## Funcionalidades Principales del CRM

| CRM y Ventas                    | Tareas y Colaboración    | Email y Marketing            |
| ------------------------------- | ------------------------ | ---------------------------- |
| Gestión de leads                | Gestor de tareas CRM     | Mailing CRM                  |
| Seguimiento y previsión         | Proyectos y subtareas    | CRM y email marketing        |
| Gestión de empresas y contactos | Chat interno             | CRM con integración de email |
| Control de acceso por roles     | Recordatorios y archivos | Soporte SMTP / IMAP          |
| Analítica CRM                   | Memos internos           | Automatización de campañas   |

🔎 Más información en el [resumen del sistema CRM](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md).

---

## CRM Python Basado en Django Admin

Django-CRM es un CRM Python que aprovecha completamente la **interfaz Django Admin**:

* Plantillas adaptativas (escritorio y móvil)
* Filtros avanzados, ordenación y búsqueda
* Permisos a nivel de objeto (ver, añadir, modificar, eliminar)
* Documentación administrativa en una sola página

En lugar de reinventar un framework de interfaz, Django-CRM se centra en la **lógica de negocio**, la **integridad de datos** y la **extensibilidad**, lo que lo hace ideal para **pequeñas y medianas empresas** que buscan un software CRM gratuito que puedan alojar y controlar.

---

## Aplicaciones Principales

### Aplicación CRM

* Solicitudes (consultas, incidencias)
* Leads y oportunidades
* Empresas y personas de contacto
* Negocios (pipeline de ventas)
* Productos y pagos
* Sistema de precios
* Correos electrónicos vinculados a objetos CRM

➡️ Más de 80 modelos CRM interconectados para flujos de ventas complejos.

---

### Gestión de Tareas y Proyectos (Gestor de Tareas CRM)

Un módulo completo de **CRM y gestión de tareas**:

* Tareas y subtareas
* Proyectos como colecciones de tareas
* Memos internos convertibles en tareas o proyectos
* Chat, archivos, recordatorios, etiquetas
* Asignación de tareas individual y por equipo

🔗 [Funciones de tareas](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md)

---

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Informe analítico CRM" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)

### Aplicación de Analítica (CRM Analítico)

Software de **analítica CRM integrado** para obtener información accionable:

* Análisis del embudo de ventas
* Informes de resumen de ingresos
* Analítica de fuentes de leads
* Resumen de solicitudes

🔗 [Resumen de la aplicación de analítica](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md)

---

### Mailing CRM y Email Marketing

El módulo de Mailing CRM incluye un sistema completo de CRM y email marketing:

* Cuentas de correo (SMTP / IMAP)
* Campañas de email y newsletters
* Plantillas dinámicas
* Firmas de correo
* Segmentación de contactos

Esto convierte a Django-CRM en un CRM con integración de correo electrónico y cliente de email interno.

---

## Cliente de Correo e Integración

El **cliente de correo integrado** soporta:

* SMTP e IMAP
* Gmail y otros proveedores
* OAuth 2.0 (autenticación en dos pasos)
* Sincronización automática de correos

Toda la correspondencia:

* Se almacena en la base de datos del CRM
* Se vincula a solicitudes, leads y negocios
* Se organiza mediante un mecanismo tipo ticket

---

## Funcionalidades Adicionales

* Integración de formularios web con reCAPTCHA v3
* Geolocalización automática
* Soporte de devolución de llamada VoIP
* Integración con mensajería (WhatsApp, Viber, etc.)
* Importación/exportación Excel
* Páginas de ayuda contextuales
* Tooltips y documentación en línea

---

## Multilenguaje y Preparado para Localización

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="django logo" width="30" height="30" style="vertical-align: bottom"> Idiomas disponibles de la interfaz:

`ar, cs, de, el, en, es, fr, he, hi, id, it, ja, ko, nl, pl, pt-br, ro, ru, tr, uk, vi, zh-hans`

Soporte completo para:

* Traducciones
* Zonas horarias
* Formatos locales de fecha y hora

---

## ¿Por Qué Elegir Este CRM Gratuito?

* ✅ Software gratuito de gestión de relaciones con clientes
* ✅ Totalmente autohospedado
* ✅ Basado en Python y Django
* ✅ CRM, tareas, email y analítica en un solo sistema
* ✅ Ideal para pymes, agencias y herramientas empresariales internas
* ✅ Sin cuotas SaaS ni dependencia de proveedor

---

## Primeros Pasos

Django-CRM funciona como un proyecto estándar de Django.

Para pruebas y evaluación:

* No se requiere base de datos externa
* SQLite funciona de forma inmediata

📘 Documentación:

* [Instalación y Configuración](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
* [Guía de Usuario](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)
* [Documentación Online](https://django-crm-admin.readthedocs.io)
* [Registro de Cambios](https://github.com/DjangoCRM/django-crm/blob/main/CHANGELOG.md)

---

## Compatibilidad

* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Django 6.0+
* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="python logo" width="30" height="30" style="vertical-align: middle"> Python 3.12+
* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="mysql logo" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
* <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30" style="vertical-align: middle"> PostgreSQL 14+

La versión del CRM compatible con Django 5.2.11 LTS está disponible [aquí](https://github.com/DjangoCRM/django-crm/tree/v1.7.x-LTS).

---

## Contribuciones

Las contribuciones son bienvenidas — nuevas funcionalidades, correcciones y mejoras en la documentación.

📄 Consulta la [Guía de Contribución](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md).

---

## Licencia

Publicado bajo la licencia **AGPL-3.0**.
Consulta el archivo [LICENSE](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE).

---

## Apoya el Código Abierto ❤️

Si este proyecto te ha resultado útil, por favor **⭐ marca el repositorio con una estrella en GitHub** — ayuda a otros a descubrir este CRM Python gratuito.
