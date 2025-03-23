# [<img src="img/django-crm_logo.png" alt="Captura de pantalla de Django CRM" width="50px" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/){target="_blank"} Bienvenido a la Documentación de Django-CRM

[Django CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} (software de gestión de relaciones con clientes) es una aplicación de código abierto con interfaz web.  
Este CRM está basado en el [sitio de administración de Django](https://docs.djangoproject.com/en/dev/ref/contrib/admin/){target="_blank"} y está escrito en el lenguaje de programación [Python](https://www.python.org/){target="_blank"}.

[<img src="img/django-crm_deals_screenshot_2x1v2.png" alt="Captura de pantalla de Django CRM" align="center" style="float: center"/>](img/django-crm_deals_screenshot_2x1v2.png){target="_blank"}
<hr/>
<div align="center">
<a class="md-button" href="https://github.com/DjangoCRM/django-crm/archive/refs/heads/main.zip">Descargar software</a>
<a class="md-button" href="/en/latest/installation/">Instalación del software</a>
<a class="md-button" href="/en/latest/introduction/">Guía del usuario</a>
</div><br>

Django CRM ofrece una solución CRM integral y consta de las siguientes aplicaciones principales:

- __TAREAS__
- __CRM__
- __ANÁLISIS__
- __CORREO MASIVO__

La aplicación de TAREAS no requiere configuración de CRM y permite a usuarios individuales o equipos trabajar con los siguientes objetos:

- [Tareas](tasks_section.md#tasks) -> Subtareas
- Proyectos -> Tareas -> Subtareas
- [Memorandos](tasks_section.md#memos) (memorandos de oficina) -> Proyectos o Tareas 

Cada instancia de estos objetos también tiene integración con:

- [<img src="icons/chat-left-text.svg" alt="Icono de chat" style="vertical-align: sub;" width="17" height="17"> Chat](tasks_section.md#chat-in-objects)
- <span style="vertical-align: baseline"><img src="icons/tags.svg" alt="Icono de etiqueta" width="17" height="17"></span>  Etiquetas
- <span style="vertical-align: baseline"><img src="icons/alarm.svg" alt="Icono de alarma" width="17" height="17"></span> Recordatorios
- [<img src="icons/paperclip.svg" alt="Icono de clip" style="vertical-align: sub;" width="17" height="17"> Archivos](introduction.md#file-object)

Las notificaciones dentro del sistema CRM y por correo electrónico también están disponibles.  
Todos los usuarios de CRM tienen acceso a esta aplicación por defecto.

El acceso al resto de las aplicaciones de Django CRM solo está disponible para usuarios con los [roles](adding_crm_users.md#user-groups-roles) apropiados, como [gerentes de ventas](guide_for_sales_manager.md), [ejecutivos de la empresa](guide_for_company_executives.md), etc.  
Para usar todas las funciones de estas aplicaciones, necesita configurar la __integración del software CRM__:

- con los sitios web de su empresa
- con los buzones de correo de su empresa y los buzones de los gerentes de ventas
- si es necesario:
    - con el servicio de recepción de tasas de [cambio de divisas](currencies.md)
    - con el servicio de telefonía VoIP