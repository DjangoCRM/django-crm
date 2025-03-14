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

*(Software de Gestión de Relaciones con Clientes Colaborativo y Analítico)*

**Django-CRM** es una solución CRM de código abierto diseñada con dos objetivos principales:

- **Para los usuarios**: Ofrecer software CRM de nivel empresarial de código abierto con una suite completa de soluciones empresariales.
- **Para los desarrolladores**: Simplificar los procesos de desarrollo, personalización y soporte de servidores de producción.

**No es necesario aprender un marco de trabajo propietario**: todo está construido utilizando el popular marco de trabajo Django.
CRM también aprovecha al máximo el sitio de administración de Django, con documentación contenida en una sola página web.

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Captura de pantalla de Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

## Características de Gestión de Relaciones con Clientes
|                                     |                                                      |                                          |
|-------------------------------------|------------------------------------------------------|------------------------------------------|
| ☑️ **Tareas y Proyectos en Equipo** | ☑️ **Gestión de Leads**                              | ☑️ **Marketing por Email**               |
| ☑️ **Gestión de Contactos**         | ☑️ **Seguimiento de Ofertas y Pronóstico de Ventas** | ☑️ **Control de Acceso Basado en Roles** |
| ☑️ **Análisis de Ventas**           | ☑️ **Integración de Chat Interno**                   | ☑️ **Diseño Adaptado a Móviles**         |
| ☑️ **Informes Personalizables**     | ☑️ **Sincronización Automática de Emails**           | ☑️ **Soporte Multimoneda**               |

Aprende más sobre [las capacidades del software](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview-spanish.md).

Django CRM es un software de gestión de relaciones con clientes de código abierto.  
Este CRM está escrito en <a href="https://www.python.org" target="_blank"><img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" style="vertical-align: middle" alt="logo de python" width="25" height="25"> Python</a>.
El frontend y el backend están completamente basados en el [sitio de administración de Django](https://docs.djangoproject.com/en/dev/ref/contrib/admin/).
La aplicación CRM utiliza plantillas HTML adaptativas de administración de forma predeterminada.
Django es un marco de trabajo excelentemente documentado con muchos ejemplos.
La documentación en el sitio de administración ocupa solo una página web.  
💡 La **idea original** es que, dado que el sitio de administración de Django ya es una interfaz profesional de gestión de objetos con un sistema de permisos flexible para los usuarios (ver, cambiar, agregar y eliminar objetos), todo lo que necesitas hacer es crear modelos para los objetos (como Leads, Solicitudes, Ofertas, Empresas, etc.) y agregar lógica de negocio.

Todo esto asegura:

- una personalización y desarrollo de proyectos significativamente más fácil
- una implementación de proyectos y soporte de servidores de producción más simple

El paquete de software proporciona dos sitios web:

- Sitio CRM para todos los usuarios
- Sitio para administradores

El **proyecto es maduro y estable**, y ha sido utilizado con éxito en aplicaciones reales durante muchos años.

## Aplicaciones Principales

La suite de software CRM consta de las siguientes **aplicaciones principales** y sus modelos:

- **Aplicación de Gestión de TAREAS**:
  (disponible para todos los usuarios por defecto, independientemente de su rol)
  - Tarea (con relacionados: archivos, chat, recordatorios, etiquetas - ver [características de tareas](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features-spanish.md))
    - subtareas
  - Memo (memo de oficina) - ver [características de memo](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features-spanish.md)
    - tareas / proyecto
  - Proyecto (*colección de tareas*):
  - ... (+ *4 más <a href="https://github.com/DjangoCRM/django-crm/tree/main/tasks/models" target="_blank">modelos</a>*)
- **Aplicación CRM**:
  - Solicitudes (consultas comerciales)
  - Leads (clientes potenciales)
  - Empresas
  - Personas de contacto (asociadas con sus empresas)
  - Ofertas (como "Oportunidades")
  - Mensajes de correo electrónico (sincronización con cuentas de correo de usuarios)
  - Productos (bienes y servicios)
  - Pagos (recibidos, garantizados, alta y baja probabilidad)
  - ... (*+ 12 más <a href="https://github.com/DjangoCRM/django-crm/tree/main/crm/models" target="_blank">modelos</a>*)
[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Informe analítico de crm" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)
- **Aplicación de ANALÍTICA**: (visión general detallada del software [aquí](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview-spanish.md))
  - Informe de Resumen de Ingresos (*ver [captura de pantalla](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)*)
  - Informe de embudo de ventas
  - Informe de Resumen de Fuente de Leads
  - ... (+ *5 más informes analíticos*)
- **Aplicación de CORREO MASIVO**:
  - Cuentas de correo electrónico
  - Mensajes de correo electrónico (boletines)
  - Firmas de correo electrónico (firmas de usuario)
  - Envíos

## Aplicaciones de Soporte

El paquete CRM también contiene **aplicaciones de soporte** como:

- Aplicación de chat (el chat está disponible en cada instancia de una tarea, proyecto, memo de oficina y oferta)
- Aplicación VoIP (contactar clientes desde ofertas)
- Aplicación de ayuda (páginas de ayuda dinámicas dependiendo del rol del usuario)
- Aplicación común:
  - 🪪 Perfiles de usuario
  - ⏰ Recordatorios (para tareas, proyectos, memos de oficina y ofertas)
  - 📝 Etiquetas (para tareas, proyectos, memos de oficina y ofertas)
  - 📂 Archivos (para tareas, proyectos, memos de oficina y ofertas)

## Funcionalidad Adicional

- Integración de formularios web: El formulario de contacto de CRM tiene incorporado:
  - protección reCAPTCHA v3
  - geolocalización automática
- Integración y sincronización de la cuenta de correo del usuario. Los mensajes de correo electrónico se guardan automáticamente:
  - en la base de datos del CRM
  - vinculados a los objetos CRM correspondientes (como: solicitudes, leads, ofertas, etc.)
- Llamada VoIP a smartphone
- Envío de mensajes a través de mensajeros (como: Viber, WhatsApp, ...)
- Soporte de Excel: Importar/exportar detalles de contacto con facilidad.

## Cliente de Correo Electrónico

El sistema CRM de Python incluye un cliente de correo electrónico integrado que opera utilizando los protocolos **SMTP** e **IMAP**.  
Esto permite que Django-CRM almacene automáticamente copias de toda la correspondencia relacionada con cada solicitud y oferta dentro de su base de datos.
La funcionalidad asegura que incluso si las comunicaciones ocurren a través de la cuenta de correo electrónico externa del usuario (fuera del CRM).
Se capturan y organizan dentro del sistema utilizando un **mecanismo de tickets**.

El CRM puede integrarse con proveedores de servicios de correo electrónico (como Gmail) que requieren autenticación de dos pasos obligatoria (utilizando el protocolo **OAuth 2.0**) para aplicaciones de terceros.

## Asistencia al Usuario

- Cada página del CRM incluye un enlace a una página de ayuda contextual, con contenido dinámicamente adaptado al rol del usuario para una orientación más relevante.
- Hay tooltips disponibles en toda la interfaz, proporcionando información instantánea al pasar el cursor sobre elementos como íconos, botones, enlaces o encabezados de tablas.
- También se incluye un [manual de usuario](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md) completo para referencia y soporte en profundidad.

## Eleva la Productividad de tu Equipo con Soluciones CRM Colaborativas

Este CRM está diseñado para mejorar la colaboración dentro de los equipos y agilizar los procesos de gestión de proyectos.  
Como un CRM colaborativo, permite a los usuarios crear y gestionar memos, tareas y proyectos con facilidad.  
[Los memos de oficina](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features-spanish.md) pueden ser dirigidos a jefes de departamento o ejecutivos de la empresa, quienes luego pueden transformar estos memos en tareas o proyectos, asignando personas responsables o ejecutores.  
[Las tareas](https://github.com/DjangoCRM/django-crm/blob/main/docs/docs/django-crm_task_features-spanish.md) pueden ser individuales o colectivas.  
Las tareas proporcionan características como discusiones de chat, recordatorios, intercambio de archivos, creación de subtareas y compartir resultados.
Los usuarios reciben notificaciones directamente en el CRM y por correo electrónico, asegurando que se mantengan informados.  
Cada usuario tiene una vista clara de su pila de tareas, incluyendo prioridades, estados y próximos pasos, mejorando así la productividad y la responsabilidad en la gestión colaborativa de relaciones con clientes.

## Localización del Proyecto

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> El software de atención al cliente ahora está disponible en **varios idiomas**:

`ar, cs, de, el, en, es, fr, he, hi, id, it, ja, ko, nl, pl, pt-br, ro, ru, tr, uk, vi, zh-hans`

Django CRM tiene [soporte completo](https://docs.djangoproject.com/en/dev/topics/i18n/) para la traducción de la interfaz, el formato de fechas, horas y zonas horarias.  

## ¿Por qué Elegir Django-CRM?

- **Autoalojamiento**: el software de la aplicación CRM está diseñado para alojarse en su propio servidor, lo que le permite tener un control total sobre los datos y el entorno de CRM. Al alojarse en su propio servidor, puede personalizar el CRM para que se ajuste a las necesidades específicas de su empresa y garantizar que sus datos permanezcan privados y seguros.
- **CRM Colaborativo**: Aumenta la productividad del equipo con herramientas para la gestión de tareas, colaboración en proyectos y comunicación interna.
- **CRM Analítico**: Obtén información accionable con informes integrados como embudo de ventas, resumen de ingresos y análisis de fuentes de leads.
- **Basado en Python y Django**: No es necesario aprender un marco propietario: todo está construido en Django con una interfaz de administración intuitiva. El frontend y backend, basados en Django Admin, hacen mucho más fácil la personalización y el desarrollo de proyectos, así como la implementación y el mantenimiento de un servidor de producción.

## Empezando

Django-CRM se puede implementar fácilmente como un proyecto regular de Django.

📚 Por favor, consulta:

- [Guía de Instalación y Configuración](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide-spanish.md)
- [Manual de Usuario](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide-spanish.md)

Si encuentras útil Django-CRM, por favor ⭐️ **da una estrella** a este repositorio en GitHub para apoyar su crecimiento.

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/Django-CRM_star_history.png" alt="Django-CRM star history" align="center" style="float: center"/>

### Compatibilidad

- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="logo de django" width="30" height="30" style="vertical-align: middle"> Django 5.1.x
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="logo de python" width="30" height="30" style="vertical-align: middle"> Python 3.10+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="logo de mysql" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="logo de postgresql" width="30" height="30" style="vertical-align: middle"> PostgreSQL 12+

## Contribuyendo

¡Las contribuciones son bienvenidas! Hay espacio para mejoras y nuevas características.
Consulta nuestra [Guía de Contribución](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md) para aprender cómo empezar.
Cada contribución, grande o pequeña, marca la diferencia.

## Licencia

Django-CRM se publica bajo la licencia AGPL-3.0 - consulta el archivo [LICENSE](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE) para más detalles.

## Créditos

- Iconos de Google [material](https://fonts.google.com/icons).
- [NicEdit](https://nicedit.com) - Editor de Contenido WYSIWYG.
- Todos los recursos utilizados bajo otras licencias.