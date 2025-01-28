<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features-spanish.md">Español</a>
</p>

# Descripción Detallada de las Funcionalidades de Tareas para Usuarios de Django-CRM

La **aplicación de Tareas en [Django-CRM](https://github.com/DjangoCRM/django-crm)** optimiza la gestión de tareas, permitiendo a los usuarios crear, asignar, rastrear y colaborar en tareas de manera eficiente. Soporta tareas individuales y colectivas, se integra con los flujos de trabajo del proyecto y asegura una comunicación fluida entre los miembros del equipo.

---

## Funcionalidades Principales

### Creación de Tareas

- Las tareas pueden ser creadas por los usuarios para sí mismos o asignadas por jefes de departamento y gerencia.
- Se pueden agregar subtareas para desglosar el trabajo en partes más pequeñas y manejables.
- Las tareas pueden asociarse con proyectos para una gestión de proyectos más fluida.
- Se pueden adjuntar archivos y etiquetas a las tareas para una mejor organización.

#### Pasos para Crear una Tarea

1. Navega a la sección "Tareas" desde la página principal.
2. Haz clic en "Crear Tarea" y completa los detalles:
   - Nombre de la tarea, descripción, fecha de vencimiento, prioridad (alta/media/baja).
   - Asigna tareas a usuarios o equipos.
   - Opcionalmente, especifica suscriptores y adjunta archivos relevantes.
   - Guarda para notificar a los participantes.

---

#### Roles de Tareas

- **Propietarios y Copropietarios de Tareas**: Aquellos que crean tareas y comparten derechos de gestión con copropietarios (por ejemplo, jefes de departamento por defecto).
- **Responsables (Ejecutores)**: Individuos responsables de la ejecución de la tarea.
- **Suscriptores**: Notificados sobre el progreso o actualizaciones de la tarea.
- **Operadores de Tareas**: Administradores opcionales con permisos a nivel de propietario.

---

#### Estado y Etapas de las Tareas

- Las tareas pasan por estados personalizables:
  *Pendiente*, *En Progreso*, *Completada*, *Pospuesta* y *Cancelada*.
- Las actualizaciones de estado pueden ser realizadas por ejecutores, propietarios u operadores. En tareas colectivas, los cambios de estado son parcialmente automáticos basados en el progreso de las subtareas.

---

#### Notificaciones y Chat de Tareas

- **Notificaciones:**
  - Todos los participantes (propietarios, ejecutores, suscriptores) reciben alertas por correo electrónico y CRM para actualizaciones de tareas, incluyendo cambios de estado y finalizaciones.
- **Chat:**
  - Mensajería integrada para colaboración, intercambio de archivos y discusiones de tareas.
  - Accesible a través del botón "Mensaje+", que se transforma en un botón de "Chat" después de su uso.

---

#### Filtros, Ordenación y Etiquetas de Tareas

- **Filtros:**
- Ubicados a la derecha de la lista de tareas para refinar los resultados.
- Incluye criterios como estado, prioridad y fecha de vencimiento.
- **Ordenación:**
- Predeterminado: Por fecha de creación.
- Recomendado: Por fecha del "Próximo Paso" para priorización de tareas activas.
- **Etiquetas:**
- Las etiquetas personalizadas pueden etiquetar tareas (por ejemplo, "Reunión de Producción").
- Las tareas pueden ser filtradas por etiquetas.

---

## Funcionalidades Especiales

1. **Subtareas y Tareas Colectivas**
   - Las tareas pueden desglosarse en subtareas para una mejor organización.
   - En tareas colectivas:
      - Los ejecutores crean subtareas para sí mismos o para otros.
      - El estado de la tarea principal se actualiza automáticamente basado en el progreso de las subtareas.
      - Los ejecutores pueden ocultar la tarea principal de su lista si sus subtareas están completadas.

2. **Notificaciones**:
   - Los participantes son notificados de la creación, actualizaciones y finalización de tareas por correo electrónico y alertas de CRM.

3. **Recordatorios**:
   - Se pueden establecer recordatorios personales para fechas límite y reuniones utilizando la vista de calendario o los detalles de la tarea.

4. **Campo de Próximo Paso**:
   - Introduce acciones planificadas y sus fechas límite para mayor claridad y mejor seguimiento del flujo de trabajo.
   - Actualiza automáticamente el flujo de trabajo de la tarea e impacta en la ordenación en la lista de tareas.

---

## **Cómo Usan los Equipos la Aplicación de Tareas**

1. **Tareas Colectivas**:
   - Los ejecutores crean subtareas para sí mismos y otros.
   - Las actualizaciones automáticas aseguran la visibilidad del progreso de la tarea, con notificaciones que reducen el seguimiento manual.

2. **Seguimiento del Progreso**:
   - Visibilidad clara en tareas *Pendientes*, *En Progreso* y *Completadas*.
   - Los gerentes pueden usar filtros para monitorear la carga de trabajo individual o del equipo.

3. **Colaboración Interdepartamental**:
   - Las subtareas pueden ser asignadas a través de departamentos, rompiendo los silos organizacionales.

---

## **Mejores Prácticas**

- **Autoasignación de Tareas**: Al recibir asignaciones verbales, crea tareas en el CRM para asegurar un seguimiento adecuado y transparencia.
- **Etiquetado**: Usa etiquetas significativas para una rápida ordenación y recuperación.
- **Actualización de Etapas**: Mantén las etapas de las tareas actualizadas para un seguimiento en tiempo real por otros participantes.
- **Verificación de Finalización**: Siempre marca las tareas como "Hechas" para notificar a los interesados y eliminarlas de las listas activas.

La aplicación de Tareas en **Django-CRM** combina simplicidad y potentes funcionalidades para optimizar la gestión de tareas y la colaboración, asegurando que los proyectos progresen eficientemente.