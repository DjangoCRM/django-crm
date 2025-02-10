<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features-spanish.md">Español</a>
</p>

# Características de Memo en Django-CRM

En [Django-CRM](https://github.com/DjangoCRM/django-crm), un memo es un memorándum de oficina que puede ser dirigido a jefes de departamento (líderes de equipo) o ejecutivos de la empresa, permitiendo a los usuarios informarles o tomar decisiones. Un usuario también puede crear memos para sí mismo (lista de tareas).

---

## Roles y Control de Acceso

Los usuarios pueden tener uno de tres roles relacionados con un memo:

### Propietario (Autor)

La persona que creó el memo tiene control total sobre él.

### Destinatario

La persona que recibe el memo, típicamente para revisión o acción. Puede ver el memo y responder a él.

### Suscriptor

Usuarios notificados y con acceso al memo. Pueden ver el memo pero no pueden editarlo.

---

## Estados de un Memo

Un memo puede estar en uno de cuatro estados:

### 1. Borrador

No es visible para nadie excepto el autor (y los administradores del CRM), no se envían notificaciones.

### 2. Pendiente

El memo ha sido enviado a los destinatarios, pero aún no lo han revisado.

### 3. Revisado

El destinatario ha revisado el memo y puede haber tomado acción o asignado [tareas](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md)/proyectos.

### 4. Pospuesto

El memo sigue pendiente de revisión, pero su estado indica que fue pospuesto para una consideración posterior.

---

## Visibilidad

Solo los usuarios con una relación con el memo (propietario, destinatario o suscriptor) y los administradores pueden ver el memo. Esto asegura que la información sensible solo sea accesible para quienes la necesitan.

---

## Creación de un Memo

Para crear un nuevo memo, los usuarios pueden seguir estos pasos:

1. Navegar a la sección de Tareas.
2. Hacer clic en el botón "Crear" o usar el ícono "+" para agregar un nuevo memo.
3. Seleccionar la opción "Memo" del menú desplegable.

Además, se puede crear un nuevo memo directamente desde un trato, y estarán vinculados.

Los usuarios pueden crear memos para:

* Sí mismos (lista de tareas)
* Jefes de departamento (líderes de equipo)
* Gerentes de la empresa

Al crear un memo, los usuarios pueden adjuntar archivos y establecer recordatorios.

---

## Edición de un Memo

Para editar un memo existente, los usuarios pueden seguir estos pasos:

1. Navegar a la sección de Tareas.
2. Buscar el memo que desean editar y hacer clic en él.
3. Realizar los cambios necesarios en los detalles del memo o adjuntar nuevos archivos.

---

## Contenido y Colaboración en el Memo

Un memo contiene:

* Archivos adjuntos por el propietario o los destinatarios
* Chat con los participantes para discutir el contenido del memo
* Recordatorios para tareas o plazos relacionados con el memo

---

## Creación de Tareas/Proyectos desde Memos

Después de que un memo ha sido revisado, la administración puede crear [tareas](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features-spanish.md) o proyectos basados en su contenido. La tarea/proyecto se vincula automáticamente al memo, y los usuarios reciben notificaciones.

Una vez que un memo ha sido revisado por el destinatario, no puede ser cambiado por el propietario.

---

## Visualización del Estado de la Tarea

En la lista de memos, se muestra el estado de las tareas asociadas, indicando su progreso.
