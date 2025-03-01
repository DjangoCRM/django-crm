# Guía del usuario de Django-CRM

## Tabla de contenidos

- [Introducción](#introducción)
  - [Historial del objeto](#historial-del-objeto)
  - [Objeto de archivo](#objeto-de-archivo)

- [Trabajando en la sección "Tareas" (para todos los usuarios)](#trabajando-en-la-sección-tareas-para-todos-los-usuarios)
  - [Chat en objetos](#chat-en-objetos)
  - [Recordatorios](#recordatorios)
  - [Tareas](#tareas)
  - [Memorandos](#memorandos)
- [Guía para ejecutivos de la empresa](#guía-para-ejecutivos-de-la-empresa)
  - [Sección de análisis](#sección-de-análisis)
    - [Resumen de ingresos](#resumen-de-ingresos)
- [Directrices para usuarios con los roles de "operador" y "gerente de ventas"](#directrices-para-usuarios-con-los-roles-de-operador-y-gerente-de-ventas)
  - [Trabajando con solicitudes](#trabajando-con-solicitudes)
  - [Geolocalización del país y ciudad del contraparte por su IP](#geolocalización-del-país-y-ciudad-del-contraparte-por-su-ip)
  - [Búsqueda de objetos por ticket](#búsqueda-de-objetos-por-ticket)
  - [Objeto de empresa](#objeto-de-empresa)
  - [Objeto de personas de contacto de la empresa](#objeto-de-personas-de-contacto-de-la-empresa)
  - [Objeto de lead](#objeto-de-lead)
  - [Objeto de correo electrónico](#objeto-de-correo-electrónico)
- [Guía para el gerente de ventas](#guía-para-el-gerente-de-ventas)
  - [Objeto de acuerdo](#objeto-de-acuerdo)
  - [Objeto de pago](#objeto-de-pago)
  - [Lista de acuerdos](#lista-de-acuerdos)
  - [Boletín de la empresa](#boletín-de-la-empresa)
  - [Transferencia de objetos de empresa a otro gerente de ventas](#transferencia-de-objetos-de-empresa-a-otro-gerente-de-ventas)

- [Guía del administrador de Django CRM](#guía-del-administrador-de-django-crm)
  - [Transferencia masiva de empresas a otro gerente de ventas](#transferencia-masiva-de-empresas-a-otro-gerente-de-ventas)
  - [Objetos de contactos masivos](#objetos-de-contactos-masivos)

## Introducción

[Django-CRM](https://github.com/DjangoCRM/django-crm/) es una aplicación con una interfaz web. Por lo tanto, puede usar un navegador de internet en su computadora, tableta y teléfono inteligente para trabajar con ella.

Para facilitar su trabajo, CRM proporciona páginas de ayuda y descripciones emergentes cuando pasa el mouse sobre ciertos elementos de la página, como íconos, botones, etc.  
Muchas páginas tienen un ícono <span style="vertical-align: bottom"><img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/question-mark.svg" alt="Icono de signo de interrogación" width="25" height="25"></span> en la esquina superior derecha. Al hacer clic en él, se abrirá la página de ayuda.

Django CRM es un paquete de software potente que requiere personalización e integración con otros servicios. Si algo no funciona como se espera, repórtelo a su administrador de CRM.

La base de datos de CRM puede contener una gran cantidad de información comercial.
Por lo tanto, las habilidades y el acceso de un usuario a las secciones de CRM están determinados por un conjunto de permisos (roles) asignados al usuario por el administrador de CRM.

Muchos **objetos** se crean y almacenan en CRM. Tales como **tareas**, **memorandos**, **leads**, **acuerdos**, **correos electrónicos**, etc.
La página de inicio de CRM enumera las secciones y los objetos de uso frecuente disponibles para el usuario. Para ver todos los objetos disponibles, debe hacer clic en el título de la sección.

En relación con objetos específicos, un usuario puede tener todos o solo algunos de los siguientes permisos:

- ver,
- crear (agregar),
- cambiar,
- eliminar

Estos permisos pueden ser permanentes y dinámicos (dependientes de condiciones).
Por ejemplo, el propietario (autor) de un memorando siempre puede verlo.  
Pero pierde los permisos para modificarlo y los permisos para eliminarlo después de que haya sido revisado por el gerente.  
La mayoría de los objetos tienen un propietario. Por lo general, es el usuario que creó este objeto. Pero algunos objetos pueden ser transferidos a otro usuario (se asigna otro propietario).

Todos los objetos tienen un ID. Se indica en la página del objeto.  
Puede buscar un objeto por su ID.  
Para hacer esto, escriba "ID" y su valor juntos en la barra de búsqueda.

Los objetos pueden tener un enlace a otros objetos. Por ejemplo, un objeto de memorando tendrá una relación con la tarea creada y los archivos adjuntos.  
Cuando elimina un memorando, todos los objetos vinculados se eliminarán.  
La lista de objetos eliminados se mostrará en la página de confirmación de eliminación.

### Historial del objeto

Todos los objetos conservan su historial de modificaciones. Al hacer clic en el botón "Historial", puede ver quién cambió qué y cuándo.

### Objeto de archivo

El objeto de archivo no contiene el archivo en sí, sino solo un enlace a él. Puede haber muchos objetos del mismo archivo en el CRM.  
Por lo tanto, al eliminar un objeto de archivo, solo se eliminará la referencia al archivo.
El archivo se eliminará cuando se elimine el último enlace a él en CRM.  
Por ejemplo, un memorando tiene un archivo adjunto. Un objeto de este archivo también estará adjunto a una tarea creada a partir de él. Si elimina una tarea, el objeto de archivo también se eliminará, pero no el archivo en sí. Porque todavía hay un objeto de archivo adjunto al memorando. Si este último objeto de archivo también se elimina, entonces el archivo se eliminará.

## Trabajando en la sección "Tareas" (para todos los usuarios)

En esta sección, los usuarios pueden trabajar con memorandos, tareas y proyectos (colecciones de tareas).
Los usuarios participantes reciben notificaciones sobre todos los eventos en CRM y por correo electrónico.
Solo los usuarios especificados en ellos en cualquier rol y los gerentes de la empresa tienen acceso a memorandos, tareas y proyectos específicos. Otros usuarios no los verán.  
Si es necesario realizar ediciones regularmente o corregir errores en estos objetos, el administrador puede asignar el rol de "operador de tareas" a un usuario. Este usuario tendrá el derecho de editar objetos de otros usuarios.

### Chat en objetos

Los objetos tienen chat. Por ejemplo, en cada tarea, todos los participantes pueden discutir su implementación y compartir archivos en el chat. En consecuencia, todos los mensajes estarán vinculados a una tarea específica. Para crear un mensaje, haga clic en el botón "Mensaje +".  
Los mensajes se envían a los usuarios en CRM y por correo electrónico.

### Recordatorios

En muchos objetos, puede crear un recordatorio asociado con este objeto.  
Puede establecer la fecha y hora en que el recordatorio aparecerá en CRM y se enviará por correo electrónico.  
En la sección general, puede ver una lista de todos los recordatorios creados. Si es necesario, puede desactivar los recordatorios que se han vuelto irrelevantes.

### Tareas

Las tareas pueden ser colectivas e individuales, principales y subtareas.  
La tarea puede incluir suscriptores. Estos son los usuarios que deben ser notificados cuando se crea y se completa la tarea. Pueden ver la tarea.  
Por defecto, solo se muestran las tareas activas en la lista de tareas.

Si se asignan varios usuarios (responsables) para realizar una tarea, entonces esta es una tarea colectiva. Para trabajar en una tarea colectiva, los ejecutores:

- deben crear subtareas para sí mismos;
- pueden crear subtareas entre sí.

Las tareas pueden tener el siguiente estado:

- pendiente;
- en progreso;
- hecho;
- cancelado.

Django CRM marca automáticamente una tarea colectiva como completada si cada persona responsable tiene al menos una subtarea y todas las subtareas están completadas.  
En otros casos, depende del propietario (copropietario) de la tarea cambiar el estado de la tarea principal.

Los usuarios pueden crear tareas para sí mismos. En este caso, CRM asigna automáticamente un copropietario de la tarea al jefe del departamento del ejecutor. Esto permite que los jefes de departamento estén al tanto de las tareas de sus empleados.

### Memorandos

Los usuarios pueden crear memorandos para los gerentes de departamento o de la empresa para informarles o para tomar decisiones.  
Si hay usuarios que necesitan conocer el memorando y su contenido, pueden ser especificados como suscriptores de esta tarea.  
El destinatario del memorando y los suscriptores serán notificados y tendrán acceso al memorando.

Puede guardar un memorando con el estado "borrador". En este caso, no se enviarán notificaciones y solo el autor (propietario) tendrá acceso a él.

El autor puede modificar el memorando hasta que el destinatario establezca el estado a "revisado". El autor será notificado de esto.

Una tarea o proyecto puede ser creado como resultado del memorando. Para mayor comodidad, la información del memorando se copia en ellos. Pero el destinatario puede modificarla o agregarla.  
El autor del memorando y los suscriptores se convierten automáticamente en suscriptores de la tarea o proyecto creado.

Los gerentes de ventas pueden crear un memorando a partir de un acuerdo. En este caso, aparecerá el botón "Ver acuerdo" en el memorando.  
El chat está disponible en el memorando para los participantes y la administración de la empresa.
El chat también está disponible en una tarea o proyecto.  
Se puede usar, por ejemplo, para notificar a los participantes sobre los cambios que han ocurrido desde que se revisó el memorando.

En la lista de memorandos, puede ver el estado de la tarea creada para él. El color del botón "Ver tarea" refleja el estado de la tarea. Además, si coloca el cursor del mouse sobre él, aparece la información del estado.
## Guía para ejecutivos de la empresa

Por defecto, los gerentes de la empresa tienen acceso a todas las secciones. Si algunas secciones u objetos no son de interés, se pueden ocultar usando configuraciones individuales - contacte a su administrador de Django CRM.

### Sección de análisis

Esta sección contiene informes estadísticos y analíticos. Actualmente hay ocho de ellos.

- Embudo de ventas;
- Informe de ventas;
- Resumen de ingresos;
- Resumen de solicitudes;
- Resumen de fuentes de leads;
- Resumen de conversión (consultas en acuerdos exitosos);
- Resumen de razones de cierre;
- Resumen de acuerdos;

Los informes contienen tablas y diagramas.  
Por defecto, los gerentes de la empresa, los gerentes de ventas y el administrador de CRM tienen acceso a esta sección.

#### Resumen de ingresos

La primera tabla muestra información sobre qué acuerdos, para qué productos y en qué volumen se recibieron pagos en el mes actual.

Las siguientes tablas muestran el pronóstico para el mes actual y los dos meses futuros para pagos garantizados, pagos con alta y baja probabilidad.

Los diagramas muestran:

- ingresos de los últimos 12 meses;
- ingresos de 12 meses en el período anterior;
- ingresos acumulados de 12 meses.

## Directrices para usuarios con los roles de "operador" y "gerente de ventas"

Las tareas del operador incluyen la creación y procesamiento de solicitudes comerciales en el CRM.
En empresas más pequeñas, los gerentes de ventas también cumplen este rol.  
Además de las solicitudes, los operadores también trabajan con objetos de leads, empresas y contactos.  
Los operadores deben tener derechos a los buzones de correo de la empresa que reciben solicitudes comerciales.

### Trabajando con solicitudes

Las solicitudes que llegan a través de los formularios de contacto de los sitios web de su empresa crean objetos en Django CRM automáticamente.  
Las solicitudes que llegan al correo electrónico de su empresa deben ser importadas.  
Para hacer esto, haga clic en el botón "Importar solicitud desde correo" en la esquina superior derecha de la página de solicitudes.  
  `Inicio > Crm > Solicitudes`
 
La lista de correos electrónicos entrantes de la cuenta de correo electrónico de su empresa o la lista de cuentas de correo electrónico si hay más de una.  
Marque los correos electrónicos sobre los cuales desea crear solicitudes en CRM y haga clic en el botón de importar.  
Contacte a su administrador de CRM si algo de esto no funciona.

También puede crear una solicitud llenando un formulario. Para obtener el formulario, haga clic en el botón "Agregar solicitud".

Las solicitudes recién creadas reciben el estado "pendiente" (pendiente de procesamiento).  
Cuando se crea una solicitud, se le asigna un ticket único.  
Este ticket se asigna posteriormente al acuerdo y a todos los correos electrónicos.

Al procesar una solicitud, es importante verificar que los datos de contacto sean correctos y completos. Es necesario solicitar datos faltantes al cliente.  
Al crear una solicitud, así como cada vez que guarde sus cambios, CRM realiza una comparación de todos los datos de contacto especificados en la solicitud con los datos acumulados en la base de datos. Esto se hace para vincular la solicitud a la empresa y persona de contacto o lead ya creados en la base de datos. El resultado se reflejará en la sección "Relaciones".
Puede establecer los enlaces usted mismo. Para hacer esto, debe presionar el icono de "lupa" cerca del campo correspondiente y seleccionar un objeto de la lista que aparece. O puede especificar el ID de este objeto.

Después de completar el procesamiento de la solicitud, debe seleccionar un gerente de ventas que trabajará con el objeto de acuerdo creado sobre la base de esta solicitud. Esto se puede hacer en el menú desplegable del campo "propietario".  
Luego cree el objeto de acuerdo presionando el botón correspondiente.
Si en este punto los enlaces a los objetos: empresa, persona de contacto o lead no están establecidos, se creará un nuevo lead. La solicitud y el acuerdo estarán vinculados a este lead. Y se notificará al gerente de ventas sobre el nuevo acuerdo.

El objeto del acuerdo no es un signo de concluir un acuerdo con el contraparte.  
Contiene información para concluir un acuerdo con el contraparte y muestra el progreso del trabajo en esto.  
Los acuerdos deben crearse para todas las solicitudes excluyendo las solicitudes con el estado "duplicado".  
El estado de la solicitud "pendiente" se elimina automáticamente cuando se crea un acuerdo o cuando se establece el estado de la solicitud en "duplicado".

Las solicitudes se utilizan en el análisis de marketing. Por lo tanto, solo deben eliminarse las solicitudes irrelevantes.  
Los operadores de CRM y los administradores tienen los permisos para eliminar solicitudes.

### Geolocalización del país y ciudad del contraparte por su IP

En Django CRM se puede configurar y activar la geolocalización del país y ciudad del contraparte por su IP. En este caso, el país y la ciudad se llenarán automáticamente en las solicitudes. Pero en casos donde se use VPN, estos datos pueden ser poco fiables.

### Búsqueda de objetos por ticket

Puede buscar solicitudes, acuerdos y correos electrónicos por ticket.
Para hacer esto, en la barra de búsqueda debe ingresar, por ejemplo,
 *ticket:lzeH07E8aHI* o *ticket lzeH07E8aHI*

### Objeto de empresa

Un objeto de empresa es necesario para almacenar información sobre la empresa, su contraparte, así como visualizar su interacción con esta empresa.
Muchos objetos tendrán una conexión con este objeto.  
Esto le permite ver la lista:

- empleados de esta empresa con los que está tratando (personas de contacto),
- correspondencia con esta empresa,
- todos los acuerdos,
- una lista de los boletines enviados por su empresa.

En la página del objeto de la empresa puede:

- crear y enviar un correo electrónico a la empresa,
- contactar a la empresa por teléfono,
- ir al sitio web de la empresa,
- agregar el objeto de una nueva persona de contacto.

Es importante evitar crear objetos duplicados de la misma empresa.
Esto sucede cuando los datos especificados en la solicitud no coinciden con los datos en el objeto de la empresa.  
Si se detecta un objeto duplicado, se puede eliminar fácilmente usando el botón "eliminar correctamente el objeto duplicado". Todos los enlaces se reconectarán al objeto original especificado.

### Objeto de personas de contacto de la empresa

Un objeto de persona de contacto es necesario para almacenar información sobre la persona de contacto, así como visualizar su interacción con la persona de contacto.  
Este objeto proporciona las mismas capacidades que el objeto de empresa y está asociado con él.

### Objeto de lead

A veces, cuando se recibe una solicitud, no contiene información sobre la empresa o la persona de contacto.  
En este caso, se crea un objeto de lead.  
Este objeto proporciona las mismas características que el objeto de empresa.  
Más tarde, cuando se reciban los datos faltantes, el objeto de lead se puede convertir en objetos de empresa y persona de contacto. En este caso, el objeto de lead se eliminará y todas las conexiones se reconectarán a la empresa y persona de contacto.

Si es necesario, los objetos de empresas, contactos y leads se pueden exportar a archivos de Excel. Usando archivos similares, es posible cargar datos existentes en CRM para la creación automática de objetos en la base de datos.

### Objeto de correo electrónico

En CRM puede crear y enviar correos electrónicos.  
Para hacer esto, el administrador debe configurar el acceso de CRM a los buzones de correo de los usuarios.  
Django CRM escanea los buzones de correo de los operadores y gerentes de ventas e importa automáticamente los correos electrónicos que contienen un ticket pero no están en la base de datos de CRM.  
Por lo tanto, es suficiente enviar la primera carta (con un ticket) desde el CRM. El usuario puede llevar a cabo la correspondencia posterior desde su buzón de correo.

Por varias razones, los correos electrónicos importados se almacenan en CRM en formato de texto.  
Por lo tanto, algunas cartas, por ejemplo, las que contienen tablas, pueden ser difíciles de leer. Use el botón con el icono de ojo. La carta se descargará del servidor de correo y se mostrará en el original.  
Los correos electrónicos de los clientes que no contienen un ticket no se cargarán automáticamente en CRM.  
Se pueden descargar y asociar con la solicitud y el acuerdo usando el botón "Importar carta". Esto se puede hacer en la página de la solicitud o del acuerdo.

Tenga en cuenta que un correo electrónico enviado desde CRM no se puede importar a CRM porque ya está en la base de datos de CRM. Si intenta hacer esto, se activará la protección.  
En este caso, puede vincular el correo electrónico a los objetos especificando sus IDs en la sección "Enlaces" del correo electrónico.

Antes de que un usuario comience a trabajar con el correo, se recomienda crear una o más firmas de usuario. Una de ellas debe ser seleccionada como la firma predeterminada.  
 `Inicio > Correo masivo > Firmas`

## Guía para el gerente de ventas

### Objeto de acuerdo

Un objeto de acuerdo se crea sobre la base de una solicitud como se describe en la sección "[Trabajando con solicitudes](#trabajando-con-solicitudes)".  
Un objeto de acuerdo puede ser asignado a un copropietario - un segundo gerente de ventas que también puede trabajar en este acuerdo.

El objeto del acuerdo permite:

- ver la solicitud del cliente;
- enviar y recibir correos electrónicos y ver toda la correspondencia relacionada con este acuerdo;
- contactar al contraparte por teléfono y usar mensajeros;
- almacenar todos los archivos asociados con este acuerdo;
- crear memorandos sobre el acuerdo;
- intercambiar mensajes con la administración de la empresa, el segundo gerente de ventas y el administrador.

El objeto del acuerdo representa:

- detalles de contacto del contraparte;
- todos los acuerdos con la empresa contraparte;
- información sobre bienes/servicios del acuerdo;
- información de pago.

Cuando creas un correo electrónico, Django CRM inserta un ticket en él. Esto permite que CRM encuentre correos electrónicos relacionados con este acuerdo en las cuentas de correo de los gerentes de ventas y los cargue en la base de datos de CRM. Por lo tanto, al menos la primera carta debe ser enviada desde el CRM. La correspondencia posterior puede llevarse a cabo desde las cuentas de correo si se guarda el ticket en los correos electrónicos.
Si por alguna razón se creó una carta relacionada con un acuerdo pero sin un ticket, entonces puede ser importada y vinculada al acuerdo usando el botón "Importar carta".

Las etapas del acuerdo, las razones para cerrar, y mucho más pueden ser personalizadas para adaptarse a las especificidades de su empresa - contacte a su administrador de CRM.

Los datos especificados en los acuerdos se utilizan en análisis. Por ejemplo, las etapas de una transacción se utilizan para construir un informe de "embudo de ventas". Se puede ver aquí:  
 `Inicio > Análisis > Embudo de ventas`

Actualmente, hay ocho informes diferentes disponibles en la sección "Análisis".

### Objeto de pago

Puedes crear objetos de pago en un acuerdo.
Además de los datos habituales, el pago puede tener uno de los siguientes estados:

- recibido;
- garantizado;
- alta probabilidad;
- baja probabilidad.

Esto se utiliza para crear un resumen de ingresos, incluyendo su pronóstico.  
El resumen de ingresos es importante para la toma de decisiones de la administración de la empresa.  
 `Inicio > Análisis > Resumen de ingresos`

### Lista de acuerdos

Por defecto, los nuevos acuerdos se colocan en la parte superior de la lista. Pero al presionar el botón de alternar orden, puedes cambiar entre este orden y el orden por fecha del próximo paso. En este modo, las transacciones cuya fecha del próximo paso se acerca serán empujadas a la parte superior de la lista.

Por defecto, solo se muestran los acuerdos activos en la lista. Cuando se completa el trabajo en el acuerdo, necesitas seleccionar la razón para cerrar el acuerdo en el menú desplegable del acuerdo. Entonces el acuerdo ya no estará activo y no aparecerá en la lista por defecto.

Para proporcionar más información sobre los acuerdos, están marcados con diferentes iconos. Para obtener una pista sobre el significado de un icono, coloca el cursor del ratón sobre él.

### Boletín de la empresa

CRM te permite enviar automáticamente noticias de la empresa.
Los destinatarios pueden ser empresas, contactos y leads de la base de datos de CRM.
Los destinatarios no interesados tienen la oportunidad de darse de baja de recibir futuros envíos.

El envío se realiza a través de las cuentas de correo principales y adicionales de los gerentes de ventas. Las cuentas de correo adicionales deben ser creadas y configuradas por el administrador de CRM para reducir el riesgo de que los filtros de spam bloqueen las cuentas principales de los gerentes. Para el mismo propósito, los envíos desde la cuenta principal solo se envían a destinatarios marcados como VIP. Esto se puede hacer a través del menú desplegable de acciones en las páginas de la lista de destinatarios (empresas, contactos y leads).

Si se utilizan cuentas que requieren autenticación en dos pasos para aplicaciones de terceros para el envío, debes contactar al administrador para obtener ayuda en pasarla por primera vez.

Prepara un mensaje para el boletín:  
 `Inicio > Correo masivo > Mensajes de correo electrónico`

Para incrustar imágenes en tu mensaje, puedes usar el botón para subir un archivo de imagen al servidor de CRM y el botón para ver las imágenes subidas.  
Debajo de cada imagen, hay una etiqueta html de la ruta al archivo. Debe ser copiada y pegada en la plantilla del mensaje.

Puedes copiar un mensaje terminado de otro gerente de ventas a ti mismo (el mensaje no contiene una firma).  
Puedes usar el botón "Enviar prueba" para verificar la visualización del mensaje. CRM hará una lista de las cuentas de correo disponibles del gerente de ventas y enviará el mensaje desde la primera cuenta a las otras cuentas.

El objeto de envío se crea en las páginas de las listas de destinatarios (empresas, contactos y leads). Para hacer esto, puedes usar el botón "Crear envío" o el menú desplegable de acciones.
Usando el menú de acciones, puedes crear un envío a destinatarios seleccionados en una página. Si tienes que crear varias listas de envío, puedes combinarlas usando el menú de acciones en la página de la lista de envíos.  
En el objeto de envío creado, especifica el mensaje a enviar, la firma deseada y guarda el objeto con el estado "activo". Para simular un ser humano, CRM enviará correos electrónicos uniformemente a lo largo del día laboral a intervalos aleatorios. El envío se pausará automáticamente los viernes, sábados y domingos.

### Transferencia de objetos de empresa a otro gerente de ventas

Un gerente de ventas puede transferir un objeto de empresa a otro gerente. Las personas de contacto se transferirán automáticamente.  
Pero para cambiar el propietario de un grupo de empresas, debes contactar al administrador.

## Guía del administrador de Django CRM

Para que los usuarios tengan éxito en Django CRM, el administrador debe hacer un buen trabajo y ayudar a otros usuarios con su trabajo. Para hacer esto, el administrador debe estudiar todas las secciones anteriores de esta guía, así como la guía de instalación y configuración de CRM.

### Transferencia masiva de empresas a otro gerente de ventas

Esto se puede hacer usando el menú desplegable de acciones en la página de la empresa.
Las personas de contacto se transferirán automáticamente.

### Objetos de contactos masivos

Para asegurar que los destinatarios siempre reciban mensajes de envío desde la misma cuenta de correo, se crean automáticamente objetos de contacto masivos.
Estos objetos corresponden al destinatario del envío y a la cuenta de correo desde la cual se le envían los mensajes.
