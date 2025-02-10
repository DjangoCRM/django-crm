<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_app_features.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_app_features-spanish.md">Español</a>
</p>

# Descripción General Integral de la Aplicación CRM en el conjunto de software Django-CRM

La **aplicación CRM** en Django-CRM es el centro neurálgico para gestionar interacciones con clientes, solicitudes comerciales y procesos de ventas. Sus características están diseñadas para optimizar las operaciones y proporcionar información accionable para gerentes de ventas, operadores y administradores. Cuenta con control de acceso basado en roles, asegurando que los usuarios solo vean los datos relevantes para sus funciones. Los datos de la aplicación CRM se integran perfectamente en la aplicación de Análisis para generar informes como embudos de ventas, resúmenes de ingresos y tasas de conversión. Estos informes permiten a las empresas refinar estrategias y lograr mejores resultados.

## Gestión de Solicitudes Comerciales

- **Creación y Procesamiento**: Los objetos de solicitud pueden crearse automáticamente a partir de formularios web, correos electrónicos o manualmente dentro del CRM. Las solicitudes contienen detalles esenciales y reciben un estado de "pendiente" hasta ser verificadas. El sistema CRM busca automáticamente en la base de datos entidades relacionadas como Empresa, Persona de Contacto o Prospecto cuando se guarda una solicitud y la vincula a ellas.
  - **Manejo de Solicitudes**: Las solicitudes se procesan y verifican, lo que puede llevar a la creación de Oportunidades.
  - **Manejo de Solicitudes Inválidas**: Las solicitudes que no coinciden con las ofertas de la empresa y no pueden ser cumplidas se marcan como irrelevantes y deben eliminarse.
  - **Filtrado de Solicitudes Comerciales**: Se filtran los dominios de correo electrónico públicos para evitar la identificación errónea de contactos de proveedores de servicios de correo comunes como Gmail.
  - **Contador de Solicitudes**: El CRM muestra el número de solicitudes pendientes en la lista, con una distinción entre las recibidas hoy y las anteriores.
- **Geolocalización del Contraparte**: El CRM puede determinar el país y la ciudad de la contraparte según su dirección IP, lo que ayuda a los equipos de ventas a personalizar la comunicación y gestionar solicitudes específicas de territorios.
- **Nombres de Empresas Prohibidos y Frases de Parada**: Para evitar solicitudes basadas en spam, los usuarios pueden agregar nombres de empresas repetitivos de spam a una lista prohibida y definir frases de parada para filtrar correos electrónicos no deseados y datos de formularios de contacto.

## Gestión de Empresas, Personas de Contacto y Prospectos

- **Gestión de Empresas y Personas de Contacto**: Cuando se recibe una nueva solicitud, el sistema verifica la base de datos en busca de empresas y personas de contacto existentes. Si no se encuentra coincidencia, se crea un nuevo Prospecto.
- **Conversión de Prospectos**: Los prospectos pueden convertirse en empresas y personas de contacto después de la validación. También previene duplicados al verificar las nuevas entradas contra los datos existentes.

## Gestión de Oportunidades

- **Creación y Gestión de Objetos de Oportunidad** (como Oportunidad):
  Un objeto de Oportunidad se crea a partir de una Solicitud y sirve como el área de trabajo principal donde los gerentes de ventas trabajan para concluir una venta exitosa. Pueden ordenarse por configuraciones predeterminadas o personalizadas según la preferencia del usuario. Los detalles del trabajo realizado se almacenan dentro del objeto de Oportunidad. Los íconos proporcionan pistas visuales sobre el estado de la oportunidad y las acciones requeridas.
  - **Ciclo de Vida de la Oportunidad**: [Las Oportunidades](https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png) se gestionan a través de varias etapas personalizables (por ejemplo, propuesta, negociación, cierre), con cada etapa rastreada visualmente en el CRM hasta su cierre. Los gerentes pueden monitorear el progreso y asegurar acciones oportunas.
  - **Cierre de una Oportunidad**: Una vez que se ha terminado el trabajo en una oportunidad, debe cerrarse con una razón seleccionada de un menú desplegable (por ejemplo, ganada, perdida). Las oportunidades cerradas se ocultarán de la lista de oportunidades activas pero permanecerán en la base de datos y se pueden acceder ajustando los filtros de actividad.
- **Orden Predeterminado de las Oportunidades**: Las nuevas oportunidades se ordenan por defecto en la parte superior de la lista, pero se recomienda ordenar por la fecha del próximo paso.

## Manejo de Moneda y Pagos

- **Configuración de Moneda**: El CRM admite múltiples monedas necesarias para los pagos, incluidas las utilizadas para informes de marketing, lo que permite a los usuarios gestionar clientes internacionales sin problemas. Las monedas y sus tasas de cambio se pueden actualizar manualmente o mediante integración con servicios externos.
- **La Moneda Nacional y la Moneda para Informes de Marketing**: Estas pueden ser diferentes o la misma. El CRM utiliza valores de tasas de cambio para generar informes analíticos y convertir pagos, asegurando una representación precisa de los datos financieros.
- **Seguimiento de Pagos**: Los pagos se pueden crear directamente en la página de Oportunidades o desde la lista de Pagos. Todos los datos de pago se utilizan para generar informes analíticos del CRM.

## Integración y Extensibilidad

- **Integración de Formularios Web**: Automatiza la entrada de datos con reCAPTCHA y geolocalización integrados.
  - Los formularios web se pueden personalizar para coincidir con la marca y los requisitos de datos de la empresa.
  - Asegura la integridad y precisión de los datos validando las entradas del formulario antes de crear solicitudes.
- **Integración de Correo Electrónico**: Permite a los usuarios enviar y recibir correos electrónicos directamente desde el CRM.
- **Sincronización de Correo Electrónico**: Gestiona correos electrónicos utilizando los protocolos SMTP e IMAP.
  - Genera automáticamente tickets únicos para rastrear hilos de correo electrónico.
  - Importa manualmente correos electrónicos relacionados con Oportunidades utilizando el botón "Importar carta".
- **Soporte de Excel**: Optimiza la importación/exportación de datos para Empresas, Contactos y Prospectos.

## Envíos

- **Gestión de Envíos**: El CRM permite a los usuarios rastrear envíos especificando las fechas de envío del contrato. Los estados de los envíos están vinculados a las oportunidades y se muestran en tiempo real a los gerentes de ventas relevantes.