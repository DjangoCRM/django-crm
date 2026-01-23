<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md">English</a>
</p>

---

# Django-CRM - guía de instalación y configuración

## Tabla de contenidos

- [Introducción](#introducción)
- [Instalación del proyecto](#instalación-del-proyecto)
  - [Bifurcar el repositorio](#bifurcar-el-repositorio)
  - [Clonar el proyecto](#clonar-el-proyecto)
  - [Instalar los requisitos](#instalar-los-requisitos)
- [Configuración de Django CRM](#configuración-de-django-crm)
  <details>

  - [Configuración de DATABASES](#configuración-de-databases)
  - [Configuración de EMAIL_HOST](#configuración-de-email_host)
  - [Configuración de ADMINS](#configuración-de-admins)

  </details>

- [Pruebas de CRM y base de datos](#pruebas-de-crm-y-base-de-datos)
- [Instalación de los datos iniciales](#instalación-de-los-datos-iniciales)
- [Ejecutar CRM en el servidor integrado](#ejecutar-crm-en-el-servidor-integrado)
- [Acceso a los sitios de CRM y admin](#acceso-a-los-sitios-de-crm-y-admin)
- [Especificar el dominio del sitio CRM](#especificar-el-dominio-del-sitio-crm)
- [Actualización del software de Django CRM](#actualización-del-software-de-django-crm)
- [Capacidad de traducir la interfaz de Django CRM a otro idioma](#capacidad-de-traducir-la-interfaz-de-django-crm-a-otro-idioma)
- [Sistema de asistencia integrado](#sistema-de-asistencia-integrado)
- [Agregar usuarios a Django CRM](#agregar-usuarios-a-django-crm)
    <details>

    <summary>Permisos, Grupos, Departamentos</summary>
  
  - [Permisos para usuarios](#permisos-para-usuarios)
  - [Grupos de usuarios](#grupos-de-usuarios)
  - [Departamentos](#departamentos)
  - [Agregar usuarios](#agregar-usuarios)

  </details>
  
- [Acceso de usuarios a aplicaciones y objetos](#acceso-de-usuarios-a-aplicaciones-y-objetos)
- [Ayudando a los usuarios a dominar Django CRM](#ayudando-a-los-usuarios-a-dominar-django-crm)
- [Configuración de la adición de solicitudes comerciales en Django CRM](#configuración-de-la-adición-de-solicitudes-comerciales-en-django-crm)
  - [Fuentes de Leads](#fuentes-de-leads)
  - [Formularios](#formularios)
    <details>

    - [Enviar datos del formulario con una solicitud POST](#enviar-datos-del-formulario-con-una-solicitud-post)
    - [Incrustar un formulario de CRM en un iframe de una página web](#incrustar-un-formulario-de-crm-en-un-iframe-de-una-página-web)
    - [Activar la protección del formulario con reCAPTCHA v3 de Google](#activar-la-protección-del-formulario-con-recaptcha-v3-de-google)
    - [Activar la geolocalización del país y la ciudad de la contraparte por su IP](#activación-de-la-geolocalización-del-país-y-la-ciudad-de-la-contraparte-por-su-ip)
    - [Agregar un formulario personalizado para iframe](#agregar-un-formulario-personalizado-para-iframe)

    </details>
  
- [Configuración de cuentas de correo electrónico](#configuración-de-cuentas-de-correo-electrónico)
  <details>

  <summary>Campos</summary>

  - [Campos](#campos)
    - ["Principal"](#principal)
    - ["Massmail"](#massmail)
    - ["Importar"](#importar)
    - ["Contraseña de la aplicación de correo electrónico"](#contraseña-de-la-aplicación-de-correo-electrónico)
    - [Sección "Información del servicio"](#sección-información-del-servicio)
    - [Sección "Información adicional"](#sección-información-adicional)
  
  </details>

- [Cliente del protocolo IMAP4](#cliente-del-protocolo-imap4)
- [Configuración de la autenticación de dos pasos OAuth 2.0](#configuración-de-la-autenticación-de-dos-pasos-oauth-20)
- [Categorías de productos de la empresa](#categorías-de-productos-de-la-empresa)
- [Productos de la empresa](#productos-de-la-empresa)
- [Monedas](#monedas)
- [Boletín informativo](#boletín-informativo)
- [Telefonía VoIP](#telefonía-voip)
- [Integración del CRM con mensajeros](#integración-del-crm-con-mensajeros)

## Introducción

[Django-CRM](https://github.com/DjangoCRM/django-crm/) (software de relación con clientes) es una aplicación de código abierto con interfaz web.  
Está basada en el [sitio de administración de Django](https://docs.djangoproject.com/en/dev/ref/contrib/admin/) y está escrita en el lenguaje de programación [Python](https://www.python.org/).

El proyecto CRM consta de las siguientes aplicaciones principales:

- TAREAS
- CRM
- ANALÍTICA
- CORREO MASIVO

La aplicación TAREAS no requiere configuración de CRM y permite a usuarios individuales o equipos trabajar con los siguientes objetos:

- Tareas / subtareas
- Proyectos
- Memorandos (memorandos de oficina)

Cada instancia de estos objetos también tiene integración con:

- Chat
- Etiquetas
- Recordatorios
- Archivos

Las notificaciones dentro de CRM y al correo electrónico también están disponibles.  
Todos los usuarios de CRM tienen acceso a esta aplicación por defecto.

El acceso al resto de las aplicaciones solo está disponible para usuarios con los roles apropiados, como gerentes de ventas, ejecutivos de la empresa, etc.  
Para usar todas las funciones de estas aplicaciones, necesita configurar la integración de CRM:

- con los sitios web de su empresa;
- con los buzones de correo de su empresa y los buzones de los gerentes de ventas;
- con el servicio de recepción de tasas de cambio actuales (si es necesario);
- con el servicio de telefonía VoIP (si es necesario).

## Instalación del proyecto

Para desplegar el proyecto, necesitarás: [Python](https://www.python.org/) y una base de datos.  
Este software CRM en Python está desarrollado teniendo en cuenta la compatibilidad con las bases de datos [MySQL](https://www.mysql.com/) y [PostgreSQL](https://www.postgresql.org).

### Bifurcar el repositorio

Haz clic en el botón Fork en la esquina superior derecha de la página principal del repositorio [Django CRM GitHub](https://github.com/DjangoCRM/django-crm/).
Ahora tienes una copia del repositorio en tu cuenta personal de GitHub.

### Clonar el proyecto

Para clonar un repositorio, debes tener [Git](https://git-scm.com/downloads) instalado en tu sistema y usar terminal o cmd.  
Clona este repositorio de GitHub:

```cmd
git clone https://github.com/DjangoCRM/django-crm.git
```

O clona tu repositorio bifurcado de GitHub:

```cmd
git clone https://github.com/<TU NOMBRE DE CUENTA>/django-crm.git
```

El proyecto se clonará en la carpeta 'django-crm'.

### Instalar los requisitos

Se recomienda primero crear un entorno virtual:

| acción   | en Unix/macOS                 | en Windows                |
|----------|-------------------------------|---------------------------|
| crear    | `python3 -m venv myvenv`      | `py -m venv myvenv`       |
| activar  | `source /myvenv/bin/activate` | `myvenv\Scripts\activate` |

#### Luego instala los requisitos del proyecto:

```cmd
pip install -r requirements.txt
```

Si el proyecto se despliega en un servidor de producción, también se requerirá un servidor web
(por ejemplo, [Apache](https://httpd.apache.org/)).  
Tutorial completo [aquí](https://docs.djangoproject.com/en/dev/topics/install/).

> [!IMPORTANT]
> **Por favor, da una estrella ⭐️ a este proyecto CRM para apoyar a sus desarrolladores!**  
> Haz clic en el botón "Starred" en la esquina superior derecha del repositorio [Django CRM GitHub](https://github.com/DjangoCRM/django-crm/).  

## Configuración de Django CRM

Para una introducción inicial al CRM, puede usar la configuración predeterminada.
Esta incluye el uso de una base de datos SQLite3, por lo que no es necesario instalar ninguna.

> [!WARNING]
> SQLite3 no es adecuado para el trabajo habitual con CRM. Utilice MySQL
> o PostgreSQL en su lugar.

La configuración del proyecto se encuentra en los archivos `settings.py`.  
La configuración principal del proyecto se encuentra en el archivo  
`webcrm/settings.py`  
La sintaxis de los datos en estos archivos debe coincidir con la sintaxis del lenguaje Python.

La mayoría de las configuraciones del proyecto son configuraciones del framework Django.
Su lista completa está [aquí](https://docs.djangoproject.com/en/dev/ref/settings/).  
Las configuraciones que faltan en esta lista son configuraciones específicas del CRM. Las explicaciones se pueden encontrar en los comentarios a ellas.  
La mayoría de las configuraciones se pueden dejar en sus valores predeterminados.

Las configuraciones predeterminadas son para ejecutar el proyecto en un servidor de desarrollo.
Cámbialas para el servidor de producción.  

Para comenzar a utilizar CRM regularmente, especifique la configuración `DATABASES` en el archivo `webcrm/settings.py`
y al menos las configuraciones `EMAIL_HOST` y `ADMINS`.

### Configuración de DATABASES

Proporciona los datos para conectarse a la base de datos:

- `ENGINE` y `PORT` están especificados por defecto para la base de datos MySQL. Cámbialos para PostgreSQL
- Especifica `PASSWORD`

Instrucciones detalladas [aquí](https://docs.djangoproject.com/en/dev/ref/settings/#std-setting-DATABASES). 

En la base de datos, configura el `USER` (por defecto 'crm_user') especificado en la configuración de `DATABASES` 
para que tenga el derecho de crear y eliminar bases de datos (ejecutar pruebas creará
y luego destruirá una [base de datos de prueba](https://docs.djangoproject.com/en/dev/topics/testing/overview/#the-test-database) separada).

#### Para la base de datos MySQL, se recomienda  

- configurar la tabla de zona horaria;  
- establecer la codificación extendida:
  - charset `utf8mb4`
  - collation  `utf8mb4_general_ci`

Y también si ocurre un error de agregación o anotación al ejecutar las pruebas, necesitas cambiar sql_mode a `ONLY_FULL_GROUP_BY`.

#### Optimización de la configuración de PostgreSQL

Necesitarás el paquete [psycopg](https://www.psycopg.org/install/)
```cmd
pip install psycopg[binary]
```
Configura la zona horaria a 'UTC' (cuando USE_TZ es True),
default_transaction_isolation: 'read committed'.  
Puedes configurarlos directamente en postgresql.conf `(/etc/postgresql/<versión>/main/)`

### Configuración de EMAIL_HOST

Especifica los detalles para conectarse a una cuenta de correo electrónico a través de la cual el CRM podrá enviar notificaciones a los usuarios y administradores.  

- `EMAIL_HOST` (servidor smtp)
- `EMAIL_HOST_PASSWORD`
- `EMAIL_HOST_USER` (login)

### Configuración de ADMINS

Agrega las direcciones de los administradores del CRM a la lista, para que puedan recibir registros de errores.  
`ADMINS = [("<NombreAdmin1>", "<admin1_box@example.com>"), (...)]`

## Pruebas de CRM y base de datos

Ejecuta las pruebas integradas:

```cmd
python manage.py test tests/ --noinput
```

## Instalación de los datos iniciales

Para llenar el CRM con datos iniciales, necesitas ejecutar el comando "setupdata" en el directorio raíz del proyecto:

```cmd
python manage.py setupdata
```

Este comando ejecutará `migrate`, `loaddata` y `createsuperuser`.
Como resultado, la base de datos se poblará con objetos como  
países, monedas, departamentos, industrias, etc.  
También se creará el superusuario.
Podrás modificarlos o agregar los tuyos propios.  
Usa las credenciales del superusuario del resultado para iniciar sesión en el sitio del CRM.

## Ejecutar CRM en el servidor integrado

No uses este servidor en nada que se asemeje a un entorno de producción (con acceso a internet al CRM).  
Está destinado solo para uso en una computadora personal o en una red local privada (por ejemplo, durante el desarrollo).

```cmd
python manage.py runserver
```

En este caso, el CRM estará disponible solo en tu computadora en la dirección IP 127.0.0.1 (localhost) y el puerto 8000.  
Pero si abres esta dirección en tu navegador, verás una página de error.  
La dirección para iniciar sesión en CRM se proporciona en la siguiente sección.

> [!IMPORTANT]
> Los sitios de administración están pensados para usuarios experimentados.  
> Úselos para la configuración inicial y las acciones que no se pueden realizar en el sitio de CRM. Por ejemplo, acciones con departamentos, usuarios, permisos, etc.  
> Para todo lo demás, utilice el sitio de CRM con el rol de usuario correspondiente.

Si necesitas proporcionar acceso al CRM desde una intranet (red local), especifica la dirección IP de tu tarjeta de red y el puerto  
(pero primero, [especifica el dominio del sitio del CRM](#especificar-el-dominio-del-sitio-crm)).
Por ejemplo:

```cmd
python manage.py runserver 1.2.3.4:8000
```

Es posible que vea mensajes como **"Ya se está ejecutando otra instancia, cerrando"** en los registros de la terminal o del servidor.  
Esto es normal y no requiere ninguna acción.  
Django CRM es una aplicación web, y el servidor web suele ejecutar varias instancias (trabajadores) del CRM simultáneamente. Sin embargo, algunos componentes del CRM están diseñados para ejecutarse en una sola instancia para funcionar correctamente. Cuando el sistema detecta que dicho componente ya se está ejecutando, evita automáticamente que se inicien instancias duplicadas.

## Acceso a los sitios de CRM y admin

Ahora tienes dos sitios web: CRM y sitios de administración.  
Usa las credenciales del superusuario para iniciar sesión.

### Sitio de CRM para todos los usuarios

`http://127.0.0.1:8000/en/123/`  
Está de acuerdo con la plantilla  
`<tu host de CRM>/<LANGUAGE_CODE>/<SECRET_CRM_PREFIX>`

### El sitio de administración para administradores (superusuarios)

`http://127.0.0.1:8000/en/456-admin`  
`<tu host de CRM>/<LANGUAGE_CODE>/<SECRET_ADMIN_PREFIX>`

`LANGUAGE_CODE`, `SECRET_CRM_PREFIX` y `SECRET_ADMIN_PREFIX`
pueden ser cambiados en el archivo `webcrm/settings.py`

> [!NOTE]
> No intentes acceder a la dirección `<tu host de CRM>` sin más (`http://127.0.0.1:8000/`).  
> Esta dirección no es compatible.  
> Para proteger el CRM con un servidor de sitios (por ejemplo, [Apache](https://httpd.apache.org/)), se puede colocar una redirección a una página de inicio de sesión falsa en esta dirección.

## Especificar el dominio del sitio CRM

Por defecto, el software CRM está configurado para trabajar en un dominio "localhost" (ip: 127.0.0.1).  
Para trabajar en otro dominio (o dirección IP), necesitas hacer lo siguiente:

- En la sección SITES para administradores (superusuarios):  
`(sitio ADMIN) Inicio > Sitios > Sitios`  
Agrega un sitio de CRM y especifica su nombre de dominio.
- En el archivo `webcrm/settings.py`:
  - específica su id en la configuración `SITE_ID`,
  - agrégalo a la configuración `ALLOWED_HOSTS`.

## Actualización del software de Django CRM

Django-CRM está en desarrollo activo: se mejora la funcionalidad existente, se añaden nuevas funcionalidades y se corrigen errores.
Además, se actualizan las versiones del software utilizado por el CRM.
Por lo tanto, es importante configurar las actualizaciones del sistema basadas en los nuevos lanzamientos de Django-CRM.
Aquí hay algunos consejos sobre cómo hacerlo mejor:

- Para evitar que tus configuraciones del sistema se sobrescriban cuando actualices el CRM, se recomienda que las guardes en un archivo de configuraciones separado, como local_settings.py.
En este archivo, agrega la línea `from .settings import *` y guarda todas tus configuraciones. De esta manera, las configuraciones predeterminadas del proyecto contenidas en el archivo settings.py serán sobrescritas por tus configuraciones.  
Para asegurar la ejecución estable de las pruebas cuando se sobrescriben las configuraciones de idioma, agrega el siguiente código al final del archivo:

```cmd
if TESTING:
    SECURE_SSL_REDIRECT = False
    LANGUAGE_CODE = 'en'
    LANGUAGES = [('en', ''), ('uk', '')]
```

Ahora, especifica tu archivo de configuraciones al iniciar el CRM.

```cmd
python manage.py runserver --settings=webcrm.local_settings
```

- El nuevo lanzamiento puede contener archivos de migración de la base de datos, por lo que necesitas ejecutar el comando de migración.

```cmd
python manage.py migrate --settings=webcrm.local_settings
```

- Un nuevo lanzamiento puede contener archivos estáticos nuevos o modificados. Por lo tanto, el comando de recolección de archivos estáticos debe ejecutarse en el servidor de producción.

```cmd
python manage.py collectstatic --settings=webcrm.local_settings
```

- Proporciona comentarios significativos sobre el código que estás modificando. Esto ayudará en caso de conflicto al fusionar tu proyecto con un nuevo lanzamiento de Django-CRM.

## Capacidad de traducir la interfaz de Django CRM a otro idioma

Los usuarios pueden elegir el idioma de la interfaz de [Django-CRM](https://github.com/DjangoCRM/django-crm/).  
La lista de idiomas disponibles (LANGUAGES) y el idioma predeterminado (LANGUAGE_CODE) se definen en el archivo:
`webcrm/settings.py`

Agrega el idioma deseado, por ejemplo, alemán:

```cmd
LANGUAGES = [
    ("de", _("German")),
    ("en", _("English")),
]
```

Guarda el archivo.  
Ejecuta el siguiente comando en el terminal en el directorio raíz del proyecto:

```cmd
python manage.py makemessages -l de
```

En el directorio  
`locale/de/LC_MESSAGES`  
aparecerá el archivo django.po.  
Usa el editor de archivos po para traducir su contenido y crear un archivo mo.  
Coloca el archivo mo en el mismo directorio.

CRM recuerda la elección de idioma del usuario, por lo que no es necesario cambiar el idioma predeterminado.

Reinicia CRM.

Si los objetos que agregaste, como etapas de negociación, razones para cerrar tratos, tienen nombres en inglés, estos nombres también pueden ser traducidos. Para hacerlo, realiza los pasos anteriores nuevamente, comenzando con el comando "makemessages".

Más detalles [aquí](https://docs.djangoproject.com/en/5.0/topics/i18n/translation/).

## Sistema de asistencia integrado

Muchas páginas tienen un ícono (?) en la esquina superior derecha.  
Este es un enlace a una página de ayuda.

Muchos botones e íconos en las páginas de CRM tienen descripciones emergentes que aparecen cuando pasas el cursor sobre ellos.

## Agregar usuarios a Django CRM

Después de completar los pasos anteriores de esta instrucción, puedes comenzar a agregar usuarios. Pero para que los gerentes de ventas puedan usar todas las funciones de Django CRM, deben seguir los puntos restantes de esta instrucción.  
Por favor, revisa las siguientes secciones antes de agregar usuarios.

### Permisos para usuarios

Hay cuatro permisos para los usuarios en relación con los objetos (por ejemplo, Tareas, Negociaciones, etc.):

- agregar (crear),
- ver,
- cambiar,
- eliminar.

Los permisos pueden asignarse a usuarios individuales o a grupos de usuarios.  
En relación con una instancia particular de un objeto, CRM puede cambiar dinámicamente el conjunto de permisos para el tipo de objeto. Por ejemplo, un usuario que tiene permiso para modificar correos electrónicos no podrá modificar un correo electrónico si es un correo entrante.

### Grupos de usuarios

Los grupos son una forma conveniente de asignar a los usuarios un conjunto específico de permisos o atributos. Un usuario puede pertenecer a cualquier número de grupos. Por ejemplo, el jefe del departamento de ventas necesita ser agregado a los grupos "managers", "department heads" y al grupo del departamento en el que trabaja (por ejemplo, "Global sales").  
Los grupos "department heads" y "Global sales" otorgan a sus miembros el atributo correspondiente, pero no proporcionan ningún permiso.  
El grupo "managers" (gerentes de ventas) proporciona a sus miembros conjuntos de permisos en relación con objetos como: Solicitud, Negociación, Cliente potencial, Empresa, Persona de contacto, etc.  
Un grupo que otorga a sus miembros ciertos derechos se llama rol.

Los siguientes roles están disponibles:

| Rol            | Descripción                                                                      |
|----------------|----------------------------------------------------------------------------------|
| chiefs         | Ejecutivos de la empresa                                                         |
| managers       | Gerentes de ventas                                                               |
| operators      | Empleados que reciben solicitudes comerciales que llegan a la empresa            |
| superoperators | Operador pero con derechos para atender varios departamentos de ventas           |
| co-workers     | Este grupo se agrega a todos los usuarios por defecto para trabajar con TAREAS   |
| task_operators | Proporciona permisos para editar Memorias de Oficina y Tareas de otros usuarios  |
| accountants    | Proporciona acceso a la analítica de CRM y a los objetos de Pago y Moneda        |

El rol de operador generalmente lo desempeñan secretarias o recepcionistas.  
A veces, el "gran jefe" comete errores o errores tipográficos al crear tareas, pero no tiene tiempo para corregirlos.
Para corregir errores evidentes, necesitas el rol de operador de tareas.

Puedes ver los conjuntos de permisos para cada rol aquí:  
 `(sitio ADMIN) Inicio > Autenticación y Autorización > Grupos`

Un usuario puede tener múltiples roles.  
Por ejemplo, si tu empresa no tiene un empleado que pueda desempeñar el rol de operador, entonces este rol debe ser otorgado a un empleado con el rol de gerente de ventas.

> [!NOTE]
> Es posible que algunas combinaciones de roles puedan llevar a un funcionamiento incorrecto de CRM. En este caso, puedes crear varias cuentas para el usuario en CRM con diferentes roles.

### Departamentos

El objeto Departamento contiene el nombre y las propiedades de un departamento específico.
Necesitas crear un departamento en la página:  
`(sitio ADMIN) Inicio > Común > Departamentos`

Al crear un departamento, se crea automáticamente un grupo con el mismo nombre.  
**Ten en cuenta** que crear un grupo para usarlo como departamento sin crear un objeto Departamento resultará en un funcionamiento incorrecto de CRM.
Los siguientes departamentos están preinstalados en CRM:

- Global sales,
- Local sales,
- Bookkeeping.

Puedes renombrarlos o agregar nuevos.

### Agregar usuarios

`(sitio ADMIN) Inicio > Autenticación y Autorización > Usuarios`

Para permitir el acceso del usuario al sitio de CRM, marca las siguientes casillas:  
Estado Activo y Personal.

Si no hay un rol adecuado para un usuario, entonces el conjunto de permisos para él puede establecerse individualmente.
Todos los usuarios deben ser agregados a su grupo de departamento. Las únicas excepciones son los gerentes de la empresa (usuarios con los roles de "chiefs").
Para los superusuarios (administradores de CRM), asignar un departamento es opcional.

Un perfil de usuario se crea automáticamente para cada usuario. Puedes especificar datos adicionales en el perfil de usuario.  
 `(sitio ADMIN) Inicio > Común > Perfiles de usuario`

Este perfil estará disponible para todos los usuarios de CRM en:  
 `(sitio CRM) Inicio > Común > Perfiles de usuario`

## Acceso de usuarios a aplicaciones y objetos

CRM puede contener información comercial o confidencial. Por lo tanto, el acceso de un usuario a aplicaciones y objetos se determina por su rol (conjunto de derechos).  
Los derechos pueden ser permanentes o dinámicos.  
Por ejemplo, si una empresa tiene dos departamentos de ventas, los gerentes de ventas solo podrán ver los objetos (Solicitudes, Negociaciones, Informes, etc.) relacionados con su departamento.

Los derechos dinámicos pueden depender de muchos factores. Por ejemplo, el valor de los filtros. Incluso los gerentes de la empresa o los administradores de CRM que pueden ver todos los objetos no podrán ver un objeto perteneciente a un departamento diferente al seleccionado actualmente en el filtro de departamento. Para ver este objeto, debe seleccionar el departamento correspondiente en el filtro o seleccionar el valor "todos".

## Ayudando a los usuarios a dominar Django CRM

Antes de comenzar a trabajar en Django CRM, los usuarios deben ser informados sobre lo siguiente:  

- Es importante familiarizarse con la guía del usuario para aprender a usar el CRM más fácilmente.
- Muchas páginas de CRM tienen un botón para ir a la página de ayuda - (?). Está ubicado en la esquina superior derecha. Las páginas de ayuda deben ser leídas.
- Muchos elementos de la página, como botones, íconos, enlaces, tienen descripciones emergentes. Para verlas, debe pasar el cursor del ratón sobre ellos.  
También es importante que el administrador ayude a los usuarios a dominar el CRM.

> [!NOTE]
> Las páginas de ayuda son dinámicas. Su contenido depende del rol del usuario.  
> Los usuarios a los que se les asignan derechos individualmente (sin asignación de rol) no podrán acceder a la página de ayuda. Dichos usuarios deben ser instruidos para trabajar en CRM por el administrador.

## Configuración de la adición de solicitudes comerciales en Django CRM

En Django CRM puede agregar solicitudes comerciales ("Solicitudes") en modo manual, automático y semiautomático.
En modo manual, debe presionar el botón "AGREGAR SOLICITUDES" en:  
  `Inicio > Crm > Solicitudes`  
y completar el formulario.

Las solicitudes que provienen de formularios en el sitio web de su empresa se crean automáticamente (si están configuradas adecuadamente).  
En modo semiautomático, las solicitudes son creadas por gerentes de ventas u operadores al importar correos electrónicos recibidos en su correo a CRM.  
Para hacer esto, debe especificar los detalles de sus [cuentas de correo](#configuración-de-cuentas-de-correo-electrónico) en CRM para asegurar el acceso de CRM a estas cuentas.
CRM asigna automáticamente el propietario de la solicitud importada al propietario de la cuenta de correo electrónico.

### Fuentes de Leads

`(ADMIN) Inicio > Crm > Fuentes de Leads`  
Para fines de marketing, cada "Solicitud", "Lead", "Contacto" y "Empresa" tiene un enlace a la correspondiente "Fuente de Lead".  
Cada Fuente de Lead se identifica por el valor de su campo UUID, que se genera automáticamente cuando se agrega una nueva Fuente de Lead al CRM.  
Para mayor comodidad, CRM tiene varias "Fuentes de Leads" predefinidas. Estas pueden ser editadas.
Cada "Fuente de Lead" tiene un enlace a un "Departamento". Por lo tanto, cada departamento puede tener su propio conjunto de fuentes de leads.  
Los campos "Nombre de la plantilla del formulario" y "Nombre de la plantilla de la página de éxito" solo se completan al [agregar un formulario iframe personalizado](#agregar-un-formulario-personalizado-para-iframe).  
El campo "Correo electrónico" solo se especifica en la "Fuente de Lead" de su sitio web. Debe especificar el valor del correo electrónico indicado en su sitio.

### Formularios

CRM puede recibir automáticamente datos de formularios en los sitios web de su empresa y, con base en ellos, crear solicitudes comerciales en la base de datos.
Para hacer esto, debe configurar el sitio para enviar datos del formulario POST a través de una solicitud a CRM. O usar formularios de CRM agregándolos a los sitios a través de iframe.

#### Enviar datos del formulario con una solicitud POST

Su sitio puede pasar los valores de los siguientes campos de formulario a CRM mediante una solicitud POST:  

| Campo del formulario | Descripción                                        |
|----------------------|----------------------------------------------------|
| `name`               | CharField (max_length=200, requerido)              |
| `email`              | EmailField / CharField (max_length=254, requerido) |
| `subject`            | CharField (max_length=200, requerido)              |
| `phone`              | CharField (max_length=200, requerido)              |
| `company`            | CharField (max_length=200, requerido)              |
| `message`            | TextField                                          |
| `country`            | CharField (max_length=40)                          |
| `city`               | CharField (max_length=40)                          |
| `leadsource_token`   | UUIDField (requerido, entrada oculta)              |

El valor del campo "leadsource_token" debe coincidir con el valor del campo "UUID" de la correspondiente (seleccionada por usted) "Fuente de Lead".  
`(ADMIN site) Inicio > Crm > Fuentes de Leads`

Url para la solicitud POST:  
`https://<suCRM.dominio>/<código_idioma>/add-request/`

#### Incrustar un formulario de CRM en un iframe de una página web

Coloque una cadena de iframe en el código HTML de una página web.  
Aquí hay un ejemplo de una cadena simple:

```html
<iframe src="<url>" style="width: 600px;height: 450px;"></iframe>
```

La url debe seguir el formato:  
`https://<suCRM.dominio>/<código_idioma>/contact-form/<uuid>/`
donde uuid es el valor del campo "UUID" de la "Fuente de Lead" seleccionada.

#### Activar la protección del formulario con reCAPTCHA v3 de Google

El formulario de CRM tiene protección integrada con reCAPTCHA v3.  
Para activarla, especifique los valores de las claves recibidas durante el registro en este servicio:  
`GOOGLE_RECAPTCHA_SITE_KEY = ''<su clave del sitio>"`  
`GOOGLE_RECAPTCHA_SECRET_KEY = ''<su clave secreta>"`

#### Activación de la geolocalización del país y la ciudad de la contraparte por su IP

El formulario de CRM tiene la capacidad integrada de geo localizar el país y la ciudad de la contraparte (visitante del sitio) por su IP. Para este propósito, se utiliza el módulo GeoIP2.  
Para activar su funcionamiento:

- guarde los archivos de las bases de datos de la ciudad y el país de [MaxMind](https://dev.maxmind.com/geoip/docs/databases) (GeoLite2-Country.mmdb y GeoLite2-City.mmdb) en el directorio media/geodb;
- establezca GEOIP = True en el archivo

#### Agregar un formulario personalizado para iframe

Puede cambiar el estilo de un formulario preestablecido o agregar formularios con diferentes estilos para que se ajusten a diferentes páginas del sitio o a diferentes sitios.  
Para agregar un nuevo formulario, coloque la plantilla HTML para ese formulario y la plantilla del mensaje de éxito de envío del formulario en la siguiente ubicación:  
`<crmproject>/crm/templates/crm/`

Guarde los nombres de estos archivos en los campos "Nombre de la plantilla del formulario" y "Nombre de la plantilla de la página de éxito" de la "Fuente de Lead" seleccionada en el siguiente formato:  
 `"crm/<nombre del archivo>.html"`

## Configuración de cuentas de correo electrónico

`(ADMIN) Inicio > Mass mail > Cuentas de correo electrónico`

Las cuentas de correo deben configurarse para los usuarios con los roles "Operador", "Superoperador" y "Gerente" (Gerente de Ventas).
Esto permitirá realizar lo siguiente:

- Los usuarios podrán enviar correos electrónicos desde CRM a través de su cuenta de correo electrónico.
- CRM tendrá acceso a la cuenta del usuario y podrá importar y vincular a Negociaciones cartas enviadas no desde CRM (si hay un ticket correspondiente en las cartas).
- Los usuarios podrán importar solicitudes desde el correo electrónico a CRM.
- Al realizar un boletín, CRM podrá enviar correos electrónicos a través de la cuenta del usuario en nombre del usuario.

### Campos

#### "Principal"

Un usuario puede tener varias cuentas, pero el envío de correos electrónicos de trabajo desde CRM se realizará solo a través de la cuenta marcada como "Principal".

#### "Massmail"

El envío masivo de correos electrónicos se puede realizar a través de todas las cuentas marcadas como "Massmail".

#### "Importar"

La marca "Importar" debe hacerse para las cuentas a través de las cuales los gerentes realizan correspondencia comercial o para las cuentas especificadas en el sitio web de la empresa, ya que pueden recibir solicitudes de clientes.

#### "Contraseña de la aplicación de correo electrónico"

El valor del campo "Contraseña de la aplicación de correo electrónico" se especifica para aquellas cuentas donde puede establecerse una contraseña para aplicaciones. En este caso, CRM la utilizará al iniciar sesión en la cuenta del usuario.

#### Sección "Información del servicio"

Esta sección muestra estadísticas e información del servicio de la actividad de CRM en esta cuenta.

#### Sección "Información adicional"

Aquí debe especificar el propietario de la cuenta y su departamento.  
Los otros campos se describen en detalle en la sección "[Configuración](https://docs.djangoproject.com/en/dev/ref/settings/#std-setting-EMAIL_HOST)" de la documentación de Django.

## Cliente del protocolo IMAP4

Django CRM utiliza un cliente del protocolo IMAP4 para permitir a los usuarios ver, importar y eliminar correos electrónicos en su cuenta de correo electrónico.  
Desafortunadamente, el funcionamiento del cliente IMAP4 depende del servicio de correo. Porque no todos los servicios de correo electrónico cumplen estrictamente con el protocolo IMAP4.  
En algunos casos, cambiar la configuración de CRM no ayudará. Necesita hacer cambios en el código o cambiar el proveedor de servicios. Por ejemplo, si el servicio no admite IMAP4 o solo admite algunos comandos.

Las configuraciones de CRM relacionadas con el funcionamiento del cliente IMAP4 están en el archivo:  
`<crmproject>/crm/settings.py`  
En la mayoría de los casos, no necesitan ser cambiadas.

## Configuración de la autenticación de dos pasos OAuth 2.0

En algunos casos, para acceder al CRM desde la cuenta de Gmail, será necesario configurar en la cuenta de Gmail el acceso para aplicaciones de terceros y pasar una vez la autenticación de dos factores.
El procedimiento no es sencillo. Por lo tanto, primero asegúrese de que sin su paso, el CRM realmente no tendrá acceso a su cuenta.  
Las API de Google utilizan el [protocolo OAuth 2.0](https://tools.ietf.org/html/rfc6749) para la autenticación y autorización.
Visite la [Consola de API de Google](https://console.developers.google.com/). Cree configuraciones de "ID de cliente OAuth 2.0" para "Aplicación web" para especificar el URI de redirección autorizado en el formato:  
 `https://<suCRM.dominio>/OAuth-2/authorize/?user=<nombre_caja>@gmail.com`

Y también obtenga las credenciales OAuth 2.0 "CLIENT_ID" y "CLIENT_SECRET". Guárdelas en la configuración del proyecto  
`<crmproject>/webcrm/settings.py`

Luego, en la página deseada de "Cuenta de correo electrónico"  
 `(ADMIN) Inicio > Correo masivo > Cuentas de correo electrónico`  
En la esquina superior derecha, haga clic en el botón "Obtener o actualizar un token de actualización".  
El CRM abrirá la página de autorización. Después de la autorización exitosa, se recibirá el valor del "token de actualización" y el CRM obtendrá acceso a esta cuenta.  
Tenga en cuenta que para recibir un token de actualización, el CRM debe estar ejecutándose en un servidor que soporte el esquema HTTPS.  
El token de actualización también se puede obtener por separado del CRM, por ejemplo, usando curl.

## Categorías de productos de la empresa

Agregue categorías de los productos, bienes o servicios de su empresa.  
`(ADMIN) Inicio > Crm > Categorías de productos`

## Productos de la empresa

Agregue los productos, servicios o bienes de su empresa
(esto puede hacerse más tarde por los gerentes de ventas).  
`(ADMIN) Inicio > Crm > Productos`

## Monedas

Dado que el CRM utiliza monedas para fines de marketing, los usuarios pueden cambiar las tasas de cambio ellos mismos.  
Pero también es posible configurar el CRM para recibir automáticamente tasas de cambio precisas de un banco u otro servicio en su país.  
Para hacer esto, necesita crear un archivo backend, colocarlo en el directorio  
`crm/backends`  
Puede usar backends ya existentes como base.  
Luego, en el archivo de configuración, especifique el nombre de la clase backend en la configuración  
`LOAD_RATE_BACKEND`

## Boletín informativo

La aplicación **Massmail** en Django CRM te permite enviar boletines a contactos, oportunidades y empresas directamente desde el CRM.
Necesitas:

* Destinatarios dentro del CRM
* [Cuentas de correo electrónico](#setting-up-email-accounts) configuradas para los gestores de ventas (marcadas como "Massmail")

Los envíos desde la cuenta del **gestor de ventas principal** se envían solo a **destinatarios VIP** para evitar los filtros de spam. Marca como VIP a los destinatarios desde el menú de **Acciones** en las páginas de contacto, empresa u oportunidad. Para los demás destinatarios, utiliza cuentas de correo adicionales.

### Configuración

`(Sitio ADMIN) Inicio > Configuración > Configuración de Massmail`

> [!NOTA]
> Cambiado en Django CRM 1.4.0:
> La configuración se ha trasladado del archivo `settings.py` a la interfaz web de administración.

**Envío en Horario Laboral:**
Para limitar los envíos al horario laboral (excluyendo de viernes a domingo), marque la casilla `Usar horario laboral`.

**Opción de Cancelar Suscripción:**

* Cree una página de “cancelación de suscripción exitosa” en el sitio web de su empresa (¡no en el sitio del CRM!).
* Ingrese su URL en el campo: `URL para cancelar suscripción`.
* Incluya un botón de enlace **CANCELAR SUSCRIPCIÓN** en cada plantilla de mensaje con la etiqueta `unsubscribe_url` – `href="{{ unsubscribe_url }}"`.

### Crear un Mailing

1. **Método rápido:** Selecciona los destinatarios (por ejemplo, en la página de lista de empresas), luego usa el menú de **Acciones**.
2. **Método detallado:** Usa el botón **Make Massmail**, aplicando filtros — ideal para listas grandes.

Prepara el mensaje y la firma opcional con anticipación.
El progreso del mailing se muestra en la página de lista de envíos (actualiza para ver cambios).

> [!NOTA]
> El gestor de ventas solo puede enviar mailings a los destinatarios asignados a él y solo usando las cuentas de correo que tenga asignadas.

**Gestión de respuestas:**
Solo los correos relacionados con Solicitudes o Negociaciones (con ticket) se importan automáticamente.
Si una respuesta a un mailing es una solicitud comercial, impórtala usando el botón en la página de **Solicitudes**. Las futuras respuestas se importarán automáticamente.

**Importante:** ¡No uses esta aplicación para hacer spam!

## Telefonía VoIP

Una aplicación configurada correctamente le permite hacer llamadas directamente desde Django CRM.
Esta aplicación le permite integrar el CRM con los servicios del proveedor de VoIP ZADARMA. Pero también se puede usar para crear archivos de integración con otros proveedores.

Es necesario recibir del proveedor (zadarma.com) y especificar en el archivo voip/settings.py los siguientes valores: SECRET_ZADARMA_KEY, SECRET_ZADARMA.
Las configuraciones de FORWARD se especifican de forma independiente, pero solo si tiene una segunda instancia de CRM en funcionamiento (por ejemplo, para una empresa subsidiaria).

Luego agregue objetos de Conexiones para los usuarios en  
 `(ADMIN) Inicio > Voip > Conexiones`

Para conectarse a un proveedor diferente, debe crear nuevos archivos para su backend (voip/backends) y (voip/views).  
Y también agregar los datos del proveedor a la lista VOIP en el archivo  
`voip/settings.py`

## Integración del CRM con mensajeros

Django CRM tiene la capacidad de enviar mensajes a través de mensajeros. Tales como  
Viber, WhatsApp. Para hacer esto, estas aplicaciones deben estar instaladas en el dispositivo del usuario.

---
**Por favor, lea [la guía del usuario de Django-CRM](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md).**
