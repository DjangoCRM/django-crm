<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview-spanish.md">Español</a>
</p>

# Resumen de Django-CRM

El [software](https://github.com/DjangoCRM/django-crm/) gratuito de gestión de CRM está diseñado para optimizar la gestión de interacciones con clientes, agilizar procesos y mejorar la toma de decisiones basada en datos.  
El software de CRM aprovecha el marco Django, garantizando facilidad de desarrollo, personalización e implementación.

A continuación, se presenta un resumen detallado de sus características y funcionalidades clave:

## Características clave de todas las aplicaciones del paquete de software CRM

La **aplicación CRM** en Django-CRM es el núcleo central para gestionar interacciones con clientes, solicitudes comerciales y procesos de ventas.  
Sus funciones están diseñadas para agilizar operaciones y proporcionar información útil para gerentes de ventas, operadores y administradores.

### Acceso y Roles de Usuario

- **Control de Acceso Basado en Roles a Secciones y Objetos**: El acceso de los usuarios a diversas secciones y objetos dentro del CRM se determina según los roles asignados.  
  Estos roles tienen derechos específicos (permisos), que pueden ser permanentes o dinámicos.  
  Por ejemplo, el autor de un memorándum puede verlo, pero podría perder el derecho a editarlo o eliminarlo después de que sea revisado por un superior.
- **Gestión de Roles Personalizados**: Los administradores pueden crear nuevos roles de usuario con permisos personalizados, permitiendo un control de acceso altamente adaptado a la jerarquía de la organización.

### Filtros y Ordenamiento

- **Panel de Filtros**: Ubicado en el lado derecho de cada página de listas de objetos, permite a los usuarios reducir los datos mostrados.  
  Algunos filtros tienen valores predeterminados (por ejemplo, solo mostrar tareas activas). Los filtros pueden personalizarse y guardarse para uso futuro.
- **Ordenamiento Avanzado**: Además del ordenamiento básico por encabezados de columnas, los usuarios pueden aplicar ordenamientos multinivel para vistas de datos más complejas.  
  Por ejemplo, las tareas pueden ordenarse primero por fecha límite y luego por nivel de prioridad.

### Identificación de Objetos y Búsqueda

- **Búsqueda Basada en ID**: Los objetos pueden localizarse rápidamente ingresando "ID" seguido del número del objeto (por ejemplo, ID1234).
- **Búsqueda por Ticket**: Solicitudes comerciales y objetos relacionados como correos electrónicos, acuerdos, etc., pueden encontrarse por su identificador único de ticket escribiendo "ticket:" seguido del valor (por ejemplo, ticket:tWRMaat3n8Y).
- **Algoritmos Automáticos de Búsqueda**: El CRM utiliza varios identificadores (por ejemplo, nombre, correo electrónico, número de teléfono) para coincidir y vincular objetos, como solicitudes a empresas y personas de contacto.  
  El sistema sugiere automáticamente entidades relacionadas durante las búsquedas.

### Integración de Chat Interno

Facilita la comunicación dentro del equipo mediante un chat integrado.

## Navegación y Usabilidad

- **Página Principal**: La página principal del CRM proporciona acceso a diversas secciones y funcionalidades según el rol del usuario.  
  Se muestran notificaciones del sistema CRM para ofrecer un resumen de actividades recientes y tareas.
- **Tooltips y Páginas de Ayuda**: Páginas de ayuda y tooltips integrados guían a los usuarios a través de funciones desconocidas.  
  Los tooltips aparecen al pasar el cursor sobre elementos como íconos o botones, ofreciendo explicaciones inmediatas. También se encuentra disponible un **manual de usuario** detallado dentro del sistema.
- **Recordatorios**: Los usuarios pueden establecer recordatorios personales para tareas críticas, reuniones o plazos próximos.  
  Estos recordatorios pueden vincularse a objetos específicos dentro del CRM, asegurando que no se pierda ninguna tarea importante.

## La Aplicación CRM en el paquete de software Django-CRM

La **aplicación CRM** del sistema Django-CRM está diseñada para gestionar relaciones con clientes de manera efectiva.  
Proporciona un conjunto completo de funciones para manejar diversos objetos empresariales como solicitudes, clientes potenciales, empresas, contactos, acuerdos, mensajes de correo electrónico, productos, pagos y otros doce más.

### Gestión de Solicitudes Comerciales

- Automatiza la creación de solicitudes desde formularios web o correos electrónicos.
- Permite la entrada manual de solicitudes por llamadas telefónicas.
- Asegura que todas las solicitudes estén vinculadas a las empresas, clientes potenciales o contactos relevantes.
- Ofrece herramientas para verificar y completar los datos faltantes de los clientes.

### Gestión de clientes potenciales y de la empresa

- Identifica automáticamente prospectos o empresas duplicados para mantener la integridad de la base de datos.
- Simplifica la conversión de clientes potenciales en empresas y contactos tras la validación.
- Vincula todos los datos asociados, incluidas solicitudes, oportunidades y correos electrónicos, a las entidades correctas.

### Gestión del Ciclo de Vida de Oportunidades

- Permite el seguimiento de oportunidades desde su creación hasta su cierre.
- Ofrece etapas personalizables y motivos de cierre adaptados a las necesidades del negocio.
- Se integra con la comunicación por correo electrónico, etiquetas y recordatorios para una gestión fluida.
- Proporciona actualizaciones de estado en tiempo real mediante iconos intuitivos.

### Herramientas de Comunicación Integradas

- Centraliza la correspondencia por correo electrónico vinculando los correos a las solicitudes y oportunidades relevantes.
  - Sincroniza automáticamente los correos con los objetos del CRM.
  - Genera tickets únicos para rastrear los hilos de correos.
- Admite llamadas VoIP y mensajería a través de plataformas como WhatsApp, Viber y otras.
- Incluye un chat interno para la colaboración entre los miembros del equipo.

### Búsqueda y Filtrado Avanzados

- Permite buscar objetos por ID, tickets u otros identificadores.
- Ofrece opciones de filtrado robustas para oportunidades, solicitudes y empresas.

### Manejo de Moneda y Pagos

- Soporta múltiples monedas para el seguimiento y reporte de pagos.
- Permite actualizaciones manuales o automáticas de tasas de cambio para datos financieros precisos.
- Rastrea pagos directamente desde oportunidades o la lista de pagos.
- Integra datos de pagos en la analítica del CRM para reportes completos.

[Leer más sobre las características de la aplicación CRM](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_app_features-spanish.md)

## La Aplicación de Tareas en el conjunto de software Django-CRM

### Memorando (*nota de servicio*)

**Memorandos**: Los memorandos pueden ser creados por cualquier usuario y están sujetos a acceso basado en roles.

- **Roles de Usuario**: Los roles relacionados incluyen propietario, destinatario, suscriptores y operadores de tareas.
- **Estados de un Memorando**: borrador, pendiente, revisado, pospuesto.
- **Destinatario del Memorando**: Puede ser el usuario mismo, el jefe de un departamento o de la empresa. El destinatario puede tomar medidas o crear tareas desde los memorandos.
- **Notificaciones Automáticas del CRM**: Los participantes son notificados automáticamente de la creación y revisión de memorandos en el CRM y por correo electrónico para un seguimiento rápido.
- **Borrador**: Los memorandos guardados como borradores solo son visibles para sus propietarios y administradores del CRM.
- **Chat del Memorando**: Los participantes pueden intercambiar mensajes y archivos en el chat del memorando.
- **Control Visual de Tareas**: Un botón "ver tarea" aparece junto a los memorandos que resultaron en tareas, con colores que indican el estado de la tarea.

[Leer más sobre las características del memorando](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features-spanish.md)

### Gestión de Tareas

- **Tipos de Tareas**: Las tareas pueden ser personales o colectivas, con la posibilidad de crear subtareas dentro de las principales.  
  El CRM realiza un seguimiento del progreso de las tareas y envía notificaciones a todos los participantes.  
  - **Trabajo en una Tarea Colectiva**: Las tareas colectivas implican la creación de subtareas personales, y las etapas se actualizan automáticamente a medida que avanza el progreso de la tarea.
- **Roles de Usuario**: Los roles relacionados con las tareas incluyen propietarios, responsables, suscriptores y operadores de tareas.
- **Asignar Tareas a Subordinados**: Las tareas pueden crearse para uno mismo o para subordinados, y los jefes de departamento tienen supervisión sobre ellas.  
  - **Por Qué Crear Tareas Propias**: Las tareas autogeneradas sirven como una lista de pendientes y un registro del trabajo realizado, visible para los gestores.
- **Flujo de Trabajo de las Tareas**: Cada tarea pasa por etapas como "pendiente", "en progreso" y "completada", con los próximos pasos registrados en los campos "Próximo Paso" y "Fecha del Paso".  
  Las notificaciones automáticas y las funcionalidades de chat apoyan la gestión de tareas.  
  - **Campo "Próximo Paso"**: Ingrese la acción planeada y su fecha en los campos "Próximo Paso" y "Fecha del Paso". Esto se guarda automáticamente en el campo "Flujo de Trabajo".
  - **Chat de Tareas**: Los participantes de las tareas pueden discutir el progreso, compartir documentos y comunicarse dentro del chat de la tarea.
  - **Filtros de Tareas**: Las tareas pueden filtrarse por diversos criterios (por ejemplo, fecha de vencimiento, prioridad, usuario asignado) y los usuarios pueden asignar etiquetas para una mejor organización.
  - **Etiquetas**: Los usuarios pueden etiquetar tareas y filtrarlas por estas etiquetas.
  - **Orden de Tareas**: Las nuevas tareas se ordenan por defecto en la parte superior de la lista, pero pueden clasificarse según la fecha del próximo paso.

  Más información detallada sobre las [características de las tareas](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features-spanish.md).

## Correo Electrónico y Campañas de Mailing

- **Integración de Correo Electrónico**: La aplicación CRM almacena correos electrónicos vinculados a negocios específicos, solicitudes o contactos.  
  - El sistema importa automáticamente los correos que contienen tickets de CRM y sincroniza con los buzones de los servidores de los proveedores de servicios.
  - El sistema CRM puede integrarse con proveedores de correo que requieran configuración OAuth2 (autenticación en dos pasos), como Gmail.
- **Campañas de Mailing**: Los usuarios pueden crear campañas de correo dirigidas, realizar un seguimiento de su éxito y gestionar listas de suscriptores.  
  Los correos se envían desde las cuentas de los gestores de ventas con limitaciones para evitar los filtros de spam.

## La Aplicación de Análisis en el Software Django-CRM

El sistema Django-CRM incluye funciones analíticas que proporcionan diversos informes para ayudarle a tomar decisiones comerciales informadas:

- **Informe Resumen de Ingresos**: Resumen de ingresos y su previsión.  
  - Proporciona un resumen de ingresos y previsiones basadas en los estados de pago.
- **Informe del Embudo de Ventas**: Representación visual del proceso de ventas.
- **Informe Resumen de Fuentes de Clientes Potenciales**: Análisis de las fuentes de clientes potenciales y su efectividad.
- **Informe de Conversión de Clientes Potenciales**: Resumen de las tasas de conversión de clientes potenciales.
- **Informe Resumen de Negocios**: Resumen de negocios y sus estados.

### Embudo de Ventas

- **Análisis del Embudo de Ventas**: El CRM proporciona un embudo de ventas visual que muestra el porcentaje de negocios que permanecen después de cada etapa, ayudando a identificar dónde se pierden más negocios y dónde se necesitan mejoras.  
  Un embudo de ventas integrado representa visualmente la conversión de solicitudes comerciales en negocios cerrados.  
  Esto ayuda a los equipos de ventas a comprender dónde pierden clientes potenciales y tomar medidas para mejorar.

## Implementación y uso

- Fácil de implementar como un proyecto Django normal.
- Documentación completa disponible para instalación, configuración y guía de usuario.
- Se agradece el apoyo y las contribuciones de la comunidad.

### Aspectos técnicos:

- **Localización:** Compatible con varios idiomas  
  (actualmente: ar, cs, de, el, en, es, fr, he, hi, id, it, ja, ko, nl, pl, pt-br, ro, ru, tr, uk, vi, zh-hans).
- **Pila tecnológica:** Desarrollado sobre Django 5.1.x, Python 3.10+, MySQL 8.0.11+ o PostgreSQL 12+.
- **Licencia:** Publicado bajo la licencia de código abierto AGPL-3.0.

## Conclusión

El sistema Django-CRM es una solución potente y flexible para la gestión de relaciones con clientes.  
Ofrece una amplia gama de funciones para manejar diversos objetos comerciales, automatizar el marketing por correo electrónico y obtener información a través de análisis.  
Al aprovechar estas características, las empresas pueden mejorar sus procesos de gestión de relaciones con clientes y tomar decisiones informadas.

(***El contenido está en proceso de ser complementado.***)

Puede obtener información más detallada en el [**manual del usuario**](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md). 
