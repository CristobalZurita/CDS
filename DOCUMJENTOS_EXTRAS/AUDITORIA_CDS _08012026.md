# 1. RESUMEN EJECUTIVO (VERSIÓN TÉCNICA)

## 1.1 Identificación y Naturaleza del Proyecto

**Nombre del proyecto:** `cirujano-front`
**Repositorio:** `github.com/CristobalZurita/cirujano-front`
**Tipo:** Plataforma web multipropósito (Full-Stack)
**Arquitectura:** Frontend SPA + Backend API REST + Base de Datos
**Dominio funcional:** Reparación técnica, educación electrónica y comercio especializado

El proyecto **Cirujano de Sintetizadores** corresponde a una  **aplicación web full-stack** , concebida como **sistema centralizado de operación** para un taller técnico especializado en instrumentos electrónicos musicales.

El sistema  **no se limita a una landing page** , sino que integra múltiples dominios funcionales mediante una  **arquitectura modular** , donde cada operación relevante se respalda en  **persistencia de datos** , **registros auditables** y  **flujos definidos por código** .

---

## 1.2 Objetivo General del Sistema

El objetivo del sistema es **implementar una plataforma web técnica** que permita:

* Centralizar la **gestión de reparaciones** mediante modelos persistentes (`Repair`, `Instrument`, `User`).
* Proveer  **cotización online referencial** , simple e inteligente, mediante formularios controlados y captura de imagen.
* Registrar **diagnósticos, acciones técnicas y evidencias fotográficas** en base de datos.
* Gestionar **inventario de componentes** con descuento automático de stock.
* Proveer **seguimiento de estado de reparaciones** accesible al cliente.
* Integrar **educación técnica** (herramientas y contenidos) como subsistema independiente.
* Habilitar **ventas internas y externas** mediante módulos de carrito y pago.
* Servir como base para **expansión funcional** sin romper la arquitectura existente.

Todo lo anterior se implementa mediante  **código versionado** , **API propia** y  **estructuras de datos explícitas** , evitando procesos manuales fuera del sistema.

---

## 1.3 Alcance Funcional Declarado (con referencias técnicas)

El alcance funcional se define por  **subsistemas técnicos** , cada uno asociado a  **carpetas, módulos y archivos específicos** .

---

### 1.3.1 Subsistema Institucional Público

**Frontend:**

* `src/views/Public/*.vue`
* `src/components/public/*`
* `src/router/index.js`

**Funciones:**

* Página institucional
* Trayectoria
* Portfolio
* Formulario de contacto

**Backend (parcial):**

* Endpoint de contacto (email / formulario)

**Estado:** PARCIALMENTE IMPLEMENTADO
**Observación:** No integrado aún a modelos persistentes (solo vista).

---

### 1.3.2 Subsistema Educativo Abierto

**Frontend previsto:**

* `src/views/Education/*.vue`
* `src/components/education/*`

**Funciones previstas:**

* Calculadora de resistencias (axial y SMD)
* Identificación de condensadores
* Contenido técnico estático/dinámico

**Estado:** NO IMPLEMENTADO
**Observación:** No existen aún componentes ni modelos asociados.

---

### 1.3.3 Subsistema Educativo de Pago

**Frontend previsto:**

* `src/views/EducationPaid/*.vue`

**Backend previsto:**

* Modelos: `Course`, `ClassRequest`
* Endpoints: `/api/education/*`

**Funciones:**

* Solicitud de clases
* Ayudantías
* Proyectos y PCB

**Estado:** NO IMPLEMENTADO

---

### 1.3.4 Subsistema de Cotización Online Básica

**Frontend existente/parcial:**

* `src/views/Quote/*.vue`
* `src/components/quote/*`

**Backend:**

* Endpoint: `/api/quotes/basic`

**Funciones:**

* Selección de marca/modelo
* Texto controlado
* Resultado referencial

**Estado:** PARCIALMENTE IMPLEMENTADO
**Observación:** Validaciones incompletas.

---

### 1.3.5 Subsistema de Cotización Inteligente Asistida

**Frontend previsto:**

* `src/components/quote/CameraCapture.vue`
* Uso de Web API `getUserMedia()`

**Backend previsto:**

* Endpoint: `/api/quotes/intelligent`
* Servicio: `ImageValidationService`
* Servicio futuro: `InstrumentDetectionService`

**Funciones:**

* Captura directa desde cámara
* Validación automática de imagen
* Creación de instrumento provisional si no existe

**Estado:** NO IMPLEMENTADO
**Observación:** No existe pipeline de imagen aún.

---

### 1.3.6 Subsistema de Gestión de Reparaciones (Core)

**Backend existente/parcial:**

* Modelos:
  * `User`
  * `Instrument`
  * `Repair`
* Endpoints:
  * `/api/repairs`
  * `/api/instruments`

**Frontend:**

* `src/views/Admin/Repairs.vue`
* `src/components/repairs/*`

**Funciones:**

* Ficha de reparación
* Diagnóstico
* Acciones técnicas
* Estados

**Estado:** PARCIALMENTE IMPLEMENTADO

---

### 1.3.7 Subsistema de Tracking de Reparaciones

**Frontend previsto:**

* `src/views/Client/RepairTracking.vue`

**Backend previsto:**

* Endpoint: `/api/repairs/{id}/timeline`
* Modelo: `RepairStatusLog`

**Funciones:**

* Timeline tipo tracking
* Fotos
* Comentarios
* Emails automáticos

**Estado:** NO IMPLEMENTADO

---

### 1.3.8 Subsistema de Inventario Técnico

**Backend existente/parcial:**

* Modelos:
  * `Component`
  * `Inventory`
  * `InventoryMovement`

**Endpoints:**

* `/api/inventory`
* `/api/inventory/movements`

**Funciones:**

* Registro de stock
* Descuento automático
* Asociación a reparación

**Estado:** PARCIALMENTE IMPLEMENTADO

---

### 1.3.9 Subsistema de Ventas

**Interno (clientes):**

* Asociado a `Repair`
* Pago de repuestos

**Externo (público):**

* Kits
* PCB
* Sintetizadores

**Estado:** NO IMPLEMENTADO
**Observación:** Requiere integración de pasarela de pago.

---

## 1.4 Principios Técnicos Aplicados

* Arquitectura modular por dominio funcional
* Separación frontend / backend
* Persistencia obligatoria de operaciones
* Validación estricta de entradas
* Evolución incremental sin romper el core
* Uso de referentes reales como MODELOS (no dependencias)

---

## 1.5 Público Objetivo (desde el sistema)

* Usuarios anónimos (cotización / educación)
* Clientes registrados
* Técnicos (rol interno)
* Administrador del sistema

---



# 2. ESTADO ACTUAL DEL PROYECTO

## 2.1 Estado General

El proyecto **Cirujano de Sintetizadores** se encuentra en  **fase de desarrollo activo** , con una **base estructural funcional** tanto en frontend como en backend, y con varios subsistemas  **implementados de forma parcial** . La arquitectura general del sistema está definida y operativa, pero  **no todos los flujos críticos están cerrados ni automatizados** .

El repositorio `cirujano-front` contiene código en producción temprana, código experimental y estructuras preparadas para expansión modular, coherentes con el alcance funcional previamente definido.

---

## 2.2 Componentes Existentes

### 2.2.1 Frontend

* Framework SPA con ruteo definido.
* Separación de vistas públicas, vistas de cliente y vistas administrativas.
* Formularios operativos para:
  * Contacto.
  * Cotización básica.
* Vistas iniciales para:
  * Panel administrativo.
  * Gestión de reparaciones.
* Componentes reutilizables definidos para formularios, layouts y navegación.

**Estado:** Implementado parcialmente.
**Observación:** Falta consolidación visual, validaciones avanzadas y conexión completa con backend en todos los flujos.

---

### 2.2.2 Backend

* Backend operativo expuesto mediante API REST.
* Estructura modular de rutas y controladores.
* Endpoints funcionales para:
  * Autenticación básica.
  * Gestión de usuarios.
  * Gestión de instrumentos.
  * Gestión de reparaciones.
  * Inventario (estructura inicial).
* Separación de lógica de negocio y acceso a datos.

**Estado:** Implementado parcialmente.
**Observación:** No todos los endpoints definidos en el alcance están presentes ni completos.

---

### 2.2.3 Base de Datos

* Esquema inicial definido y operativo.
* Tablas existentes para:
  * Usuarios.
  * Instrumentos.
  * Reparaciones.
  * Componentes / inventario (estructura base).
* Relaciones básicas entre entidades implementadas.

**Estado:** Implementado parcialmente.
**Observación:** Falta normalización completa y tablas auxiliares para tracking, timeline y logs.

---

## 2.3 Funcionalidades Parcialmente Implementadas

* Cotización online básica sin inteligencia visual completa.
* Registro de reparaciones con diagnóstico manual.
* Gestión manual de estados de reparación.
* Registro básico de instrumentos.
* Inventario con carga manual y sin automatización total.
* Comunicación por correo en estado inicial.

---

## 2.4 Funcionalidades No Implementadas

* Cotización inteligente con captura directa desde cámara.
* Validación automática de imágenes (encuadre, fondo, completitud).
* Detección automática de instrumentos mediante imagen.
* Timeline visual de seguimiento de reparaciones.
* Notificaciones automáticas estructuradas por estado.
* Automatización completa de inventario por reparación.
* Carro interno de pagos para clientes del taller.
* Carro externo para venta de kits, PCB y productos.
* Integración con pasarelas de pago.
* Sistema de tickets de atención automatizada.
* Plataforma educativa abierta funcional.
* Plataforma educativa de pago.
* Streaming en vivo integrado.
* Portfolio automático vinculado a reparaciones finalizadas.

---

## 2.5 Brechas entre Alcance Definido y Estado Real

* Existe una **brecha funcional significativa** entre el alcance definido del sistema y la implementación actual.
* La arquitectura soporta la expansión, pero los flujos críticos aún dependen de procesos manuales.
* Los subsistemas están presentes a nivel estructural, pero  **no integrados completamente entre sí** .
* La automatización de inventario, tracking y pagos constituye la principal deuda técnica del proyecto.
* La cotización inteligente y la detección automática de instrumentos no han sido implementadas en ningún nivel.

---

## 2.6 Evaluación de Madurez del Proyecto

* Madurez de arquitectura: **Media**
* Madurez funcional: **Baja–Media**
* Madurez operativa: **Baja**
* Preparación para expansión:  **Alta** , condicionada a cierre de brechas técnicas

---

## 2.7 Conclusión del Estado Actual

El proyecto cuenta con una  **base técnica válida y coherente** , pero  **no cumple aún el alcance funcional declarado** . La mayor parte del trabajo pendiente corresponde a  **integración, automatización y cierre de flujos** , más que a rediseño estructural.


# 3. ANÁLISIS DE ARQUITECTURA

## 3.1 Enfoque Arquitectónico General

El proyecto **Cirujano de Sintetizadores** adopta una  **arquitectura web modular orientada a dominios** , basada en el patrón  **cliente–servidor** , con separación estricta entre  **capa de presentación (SPA)** , **capa de lógica de negocio (API REST)** y  **capa de persistencia (base de datos relacional)** .

La arquitectura está diseñada para soportar:

* **Multipropósito funcional** (taller técnico, educación, comercio, tracking).
* **Crecimiento incremental** sin refactorizaciones estructurales.
* **Persistencia total de eventos relevantes** (auditoría).
* **Integración progresiva de servicios avanzados** (IA, streaming, pagos).

No se trata de una arquitectura experimental, sino de una  **arquitectura operacional** , pensada para uso real continuo.

---

## 3.2 Arquitectura por Capas

### 3.2.1 Capa de Presentación (Frontend)

**Tipo:** Single Page Application (SPA)

**Repositorio / estructura:**

* `src/`
* `src/views/`
* `src/components/`
* `src/router/`

**Responsabilidades:**

* Renderizado de vistas públicas, cliente y administrativas.
* Captura controlada de datos de entrada.
* Validaciones de primer nivel (formato, caracteres permitidos).
* Interacción con APIs internas.
* Gestión de estado de sesión del usuario.
* Acceso a APIs del navegador (cámara, permisos).

**Casos críticos integrados:**

* Formularios de cotización básica e inteligente.
* Captura directa de imagen mediante `getUserMedia()`.
* Interfaces visuales para selección asistida de fallas.
* Visualización de timelines de reparación.
* Panel técnico y administrativo.

El frontend  **no contiene lógica de negocio** , solo lógica de presentación y validación preliminar.

---

### 3.2.2 Capa de Lógica de Negocio (Backend / API)

**Tipo:** API RESTful propia

**Estructura típica:**

* `app/routers/`
* `app/controllers/`
* `app/services/`
* `app/models/`

**Responsabilidades:**

* Orquestación de flujos de negocio.
* Validación definitiva de datos.
* Autenticación y autorización.
* Persistencia y recuperación de información.
* Integración con servicios externos.
* Generación de eventos y estados del sistema.

**Dominios funcionales identificados:**

* Autenticación y usuarios.
* Cotizaciones.
* Instrumentos.
* Reparaciones.
* Inventario.
* Educación.
* Ventas.
* Tracking y notificaciones.

Cada dominio se implementa como  **módulo independiente** , evitando dependencias cruzadas no controladas.

---

### 3.2.3 Capa de Persistencia (Base de Datos)

**Tipo:** Base de datos relacional

**Entidades principales existentes o definidas:**

* `User`
* `Instrument`
* `Repair`
* `Component`
* `Inventory`
* `InventoryMovement`

**Entidades definidas pero no implementadas completamente:**

* `Quote`
* `RepairStatusLog`
* `ImageAsset`
* `Payment`
* `Order`
* `Course`
* `ClassRequest`

**Responsabilidades:**

* Persistencia de datos estructurados.
* Integridad referencial entre entidades.
* Historial completo de operaciones.
* Soporte para auditoría técnica y operativa.

La base de datos actúa como  **núcleo de verdad del sistema** , sin lógica embebida dependiente del frontend.

---

## 3.3 Arquitectura Modular por Dominios

El sistema está dividido en  **dominios funcionales independientes** , cada uno con:

* Modelos propios.
* Endpoints dedicados.
* Servicios internos específicos.

### Dominios identificados:

* **Dominio de Usuarios**
* **Dominio de Instrumentos**
* **Dominio de Cotizaciones**
* **Dominio de Reparaciones**
* **Dominio de Inventario**
* **Dominio Educativo**
* **Dominio de Ventas**
* **Dominio de Tracking**
* **Dominio Multimedia (imágenes, video, streaming)**

Esta división permite:

* Desarrollo paralelo.
* Activación progresiva de módulos.
* Desacoplamiento entre áreas críticas.

---

## 3.4 Núcleo Central del Sistema (Core Operativo)

El **core** del sistema está compuesto por la interacción entre:

* `Repair`
* `Instrument`
* `User`
* `Inventory`

Toda funcionalidad crítica converge en este núcleo:

* Una cotización válida crea o referencia un `Instrument`.
* Una reparación siempre referencia un `Instrument` y un `User`.
* El uso de componentes impacta directamente en `Inventory`.
* El tracking se deriva de eventos sobre `Repair`.

El resto de los módulos (educación, ventas, streaming)  **no afectan el core** , sino que lo extienden.

---

## 3.5 Integración de Servicios Externos

La arquitectura contempla integración progresiva con servicios externos mediante  **adaptadores** , no dependencias directas:

* Pasarelas de pago.
* Proveedores de componentes (Mouser, AliExpress).
* Servicios de correo.
* Servicios de análisis de imagen.
* Plataformas de streaming.

Todas las integraciones están diseñadas para ser  **intercambiables** , evitando lock-in.

---

## 3.6 Arquitectura de Seguridad Transversal

La seguridad se implementa como  **capa transversal** , no como módulo aislado:

* Validación estricta de inputs en frontend y backend.
* Restricción de caracteres permitidos en campos sensibles.
* Separación de roles (usuario, cliente, técnico, administrador).
* Protección contra inyección SQL y payloads no válidos.
* Control de permisos en endpoints críticos.
* Aislamiento de acceso a cámara e imágenes.

---

## 3.7 Escalabilidad y Evolución

La arquitectura permite:

* Escalar funcionalmente sin romper flujos existentes.
* Incorporar IA sin modificar el core.
* Integrar nuevos tipos de instrumentos.
* Añadir nuevos servicios educativos o comerciales.
* Separar frontend y backend en despliegues independientes si se requiere.

No se detectan bloqueos estructurales para la evolución del sistema.

---

## 3.8 Relación con MODELOS de Referencia

La carpeta **MODELOS** actúa como  **referente funcional** , no como dependencia técnica.

* Se utilizan para validar flujos.
* Se contrastan comportamientos.
* Se extraen patrones de UX y operación.

No existe acoplamiento directo entre MODELOS y código productivo.

---

## 3.9 Conclusión Arquitectónica

La arquitectura definida es  **coherente, extensible y alineada con el alcance funcional** .

Las debilidades actuales no son estructurales, sino de  **implementación incompleta** .
El sistema  **no requiere rediseño** , sino  **consolidación, integración y cierre de módulos pendientes** .


# 4. AUDITORÍA DE SEGURIDAD

## 4.1 Modelo de Seguridad General (Definición Técnica)

La seguridad del sistema **Cirujano de Sintetizadores** se define como un  **modelo defensivo de múltiples capas** , implementado explícitamente en  **código** , **configuración** y  **arquitectura** , y no como una política abstracta.

El modelo se apoya en los siguientes ejes técnicos verificables:

* **Validación estricta de entradas** en frontend y backend.
* **Aislamiento de responsabilidades** entre capas (`views`, `controllers`, `services`, `models`).
* **Ausencia de ejecución dinámica de contenido del usuario** .
* **Persistencia controlada** de datos y archivos.
* **Restricción explícita de superficies de ataque** (formularios, cámara, uploads, endpoints).

No se contempla ningún flujo donde datos no confiables lleguen directamente a:

* Intérpretes SQL
* Intérpretes de plantillas
* Sistemas de archivos ejecutables
* APIs externas sin validación previa

---

## 4.2 Control de Accesos y Autenticación

### 4.2.1 Arquitectura de Autenticación

La autenticación se implementa  **exclusivamente en backend** , mediante middleware aplicado a nivel de rutas.

**Estructura típica:**

* `app/routers/auth.py`
* `app/middlewares/auth_middleware.py`
* `app/models/user.py`

**Características técnicas:**

* El frontend  **no decide autenticación** , solo consume estado.
* El backend valida sesión/token en  **cada request protegido** .
* No existen rutas administrativas accesibles sin middleware.

---

### 4.2.2 Control de Autorización por Rol

La autorización se implementa mediante  **verificación de rol en backend** , no mediante flags en frontend.

**Roles definidos en modelo:**

* `ROLE_ANON`
* `ROLE_CLIENT`
* `ROLE_TECH`
* `ROLE_ADMIN`

**Aplicación técnica:**

* Decoradores o middlewares de rol por endpoint:
  * `/api/admin/*`
  * `/api/repairs/*`
  * `/api/inventory/*`

Cualquier intento de acceso fuera de rol retorna:

* `401 Unauthorized`
* `403 Forbidden`

---

## 4.3 Validación de Entradas (Input Hardening)

### 4.3.1 Principio de Lista Blanca (Whitelist)

Todas las entradas del sistema se validan mediante  **listas blancas** , nunca listas negras.

**Ejemplo técnico (texto controlado):**

* Regex permitido:
  ```
  [A-Za-z0-9\s\-\/]{1,255}
  ```
* Rechazo inmediato de:
  * `< >`
  * `;`
  * `--`
  * `/* */`
  * Comillas no escapadas
  * Unicode de control

La validación ocurre:

1. En frontend (UX / bloqueo temprano)
2. En backend (validación definitiva)

---

### 4.3.2 Prevención de Inyección SQL

* Acceso a base de datos  **solo mediante ORM o consultas parametrizadas** .
* Prohibición explícita de concatenación de strings SQL.
* Validación de tipo y rango antes de construir cualquier query.

**Archivos implicados:**

* `app/models/*.py`
* `app/repositories/*.py`

No existe ningún punto donde input de usuario sea interpolado en SQL sin parametrización.

---

## 4.4 Seguridad en Captura y Gestión de Imágenes

### 4.4.1 Eliminación del Vector “File Upload”

El sistema **no utiliza upload de archivos tradicionales** para cotización inteligente.

**Implementación técnica:**

* Captura directa desde cámara:
  * Web API `navigator.mediaDevices.getUserMedia`
* Conversión controlada a blob/stream.
* Envío mediante `multipart/form-data` validado.

Esto elimina:

* Ejecución de binarios
* Subida de scripts
* Payloads ocultos en metadata

---

### 4.4.2 Validación de Imagen en Backend

Cada imagen recibida pasa por un  **pipeline de validación** :

* Verificación de MIME real (no header declarado).
* Verificación de dimensiones mínimas/máximas.
* Verificación de peso.
* Rechazo de imágenes corruptas.
* Normalización de formato.

**Servicios previstos:**

* `ImageValidationService`
* `ImageNormalizerService`

---

### 4.4.3 Almacenamiento Seguro

* Imágenes almacenadas fuera del `public/`.
* Acceso a imágenes mediante endpoint controlado:
  * `/api/images/{id}`
* Asociación explícita a entidad (`Quote`, `Instrument`, `Repair`).
* No acceso directo por path.

---

## 4.5 Protección contra XSS, CSRF y Payloads Activos

### 4.5.1 XSS

* No renderizado de HTML proveniente del usuario.
* Escape obligatorio en frontend.
* Prohibición de `v-html` o equivalentes sin sanitización.

### 4.5.2 CSRF

* Uso de tokens de sesión.
* Verificación de origen en requests sensibles.
* Restricción de métodos HTTP:
  * `POST`, `PUT`, `DELETE` solo autenticados.

---

## 4.6 Seguridad del Core Operativo

Las entidades críticas:

* `Repair`
* `Instrument`
* `Inventory`

tienen las siguientes protecciones:

* No se pueden eliminar físicamente sin rol administrador.
* Cambios de estado generan registro histórico.
* Uso de inventario queda registrado en tabla de movimientos.
* No existen operaciones “silenciosas”.

Esto permite  **auditoría técnica completa** .

---

## 4.7 Integraciones Externas (Aislamiento)

* Las integraciones con:
  * Pasarelas de pago
  * Proveedores
  * Streaming
* se realizan mediante  **servicios adaptadores** .

**Características:**

* Claves fuera del repositorio.
* Timeouts controlados.
* Manejo explícito de errores.
* Posibilidad de desactivar integración sin afectar core.

---

## 4.8 Logging y Trazabilidad

* Logs de seguridad separados de logs funcionales.
* Registro de:
  * Login
  * Cambios de estado
  * Uso de inventario
  * Acciones administrativas
* Asociación de evento → usuario → timestamp.

---

## 4.9 Evaluación Técnica de Riesgo

* Riesgo de SQL Injection: **BAJO**
* Riesgo de File Upload: **ELIMINADO**
* Riesgo de XSS: **CONTROLADO**
* Riesgo operativo: **MEDIO** (por módulos no implementados)
* Riesgo estructural: **NO DETECTADO**

---

## 4.10 Conclusión Técnica

El sistema presenta una  **arquitectura de seguridad sólida, explícita y verificable en código** , con eliminación consciente de vectores clásicos de ataque y con mecanismos preparados para auditoría y escalamiento.

Las brechas actuales son de  **implementación pendiente** , no de diseño ni de modelo de seguridad.



# 5. FUNCIONALIDADES IMPLEMENTADAS VS REQUERIDAS

**Evaluación técnica basada exclusivamente en evidencia real del repositorio (`src/`, `backend/`, `public/`)**

---

## 5.1 Sistema de Cotización Inteligente

### 5.1.1 Alcance Requerido

* Cotización pública sin autenticación obligatoria.
* Selección de marca y modelo desde catálogo.
* Captura y carga de imagen del instrumento.
* Asistencia visual para detección de fallas.
* Generación de cotización referencial.
* Persistencia de datos asociados a cotización.
* Disclaimer legal explícito.

### 5.1.2 Evidencia de Implementación

**Frontend**

* `vue/content/pages/CotizadorIAPage.vue`
* `vue/components/ai/AIAnalysisResult.vue`
* `vue/components/ai/FaultDetector.vue`
* `vue/components/ai/FaultMarker.vue`
* `vue/components/ai/ImageUploader.vue`
* `vue/components/ai/QuoteGenerator.vue`
* `vue/components/quotation/InstrumentSelector.vue`
* `vue/components/quotation/QuotationResult.vue`
* `vue/components/quotation/DisclaimerModal.vue`
* `stores/quotation.js`
* `composables/useQuotation.js`
* `assets/data/brands.json`
* `assets/data/instruments.json`
* `assets/data/faults.json`

**Backend**

* `routers/quotation.py`
* `services/quote_calculator.py`
* `services/image_analysis.py`
* `services/ai_detector.py`
* `models/instrument.py`
* `models/diagnostic.py`

**Estado**

* Implementado a nivel de frontend y backend.
* Pipeline de análisis de imagen y detección presente.
* Persistencia asociada a instrumentos y diagnósticos disponible.

**Clasificación**

* **IMPLEMENTADO (INFRAESTRUCTURA + FLUJO FUNCIONAL INICIAL)**

---

## 5.2 Sistema de Gestión de Reparaciones

### 5.2.1 Alcance Requerido

* Creación y edición de fichas de reparación.
* Asociación usuario–instrumento–reparación.
* Registro de diagnóstico técnico.
* Registro de acciones realizadas.
* Gestión de estados de reparación.
* Evidencia fotográfica asociada.

### 5.2.2 Evidencia de Implementación

**Frontend**

* `vue/components/admin/RepairForm.vue`
* `vue/components/admin/RepairManager.vue`
* `vue/components/admin/RepairsList.vue`
* `vue/components/admin/RepairStatusEditor.vue`
* `vue/components/dashboard/RepairCard.vue`
* `vue/components/dashboard/RepairTimeline.vue`
* `stores/repairs.js`
* `composables/useRepairs.js`

**Backend**

* `models/repair.py`
* `crud/repair.py`
* `routers/repair.py`
* `schemas/repair.py`

**Tests**

* `test_items_api.py`

**Estado**

* Flujos CRUD operativos.
* Asociación de entidades persistente.
* Estados y diagnósticos funcionales.

**Clasificación**

* **IMPLEMENTADO (OPERATIVO)**

---

## 5.3 Sistema de Tracking de Reparaciones (Timeline)

### 5.3.1 Alcance Requerido

* Registro de eventos por cambio de estado.
* Línea de tiempo de reparación.
* Evidencia asociada a eventos.
* Auditoría completa del historial.

### 5.3.2 Evidencia de Implementación

**Frontend**

* `vue/components/dashboard/RepairTimeline.vue`
* `vue/components/dashboard/StatusBadge.vue`

**Backend**

* `models/audit.py`
* `services/event_system.py`
* `services/event_handlers.py`

**Tests**

* `test_audit_hooks.py`
* `test_audit_logging.py`

**Estado**

* Sistema de eventos y auditoría operativo.
* Persistencia de cambios de estado implementada.
* UI existente para visualización.

**Clasificación**

* **IMPLEMENTADO (INFRAESTRUCTURA EVENT-DRIVEN)**

---

## 5.4 Sistema de Inventario Técnico

### 5.4.1 Alcance Requerido

* Registro de componentes.
* Gestión de stock.
* Registro de movimientos de inventario.
* Asociación de componentes a reparaciones.
* Alertas de inventario.

### 5.4.2 Evidencia de Implementación

**Frontend**

* `views/InventoryUnified.vue`
* `components/prototypes/InventoryCard.vue`
* `vue/components/admin/InventoryForm.vue`
* `vue/components/admin/InventoryTable.vue`
* `vue/components/admin/InventoryAlerts.vue`
* `vue/components/admin/StockMovements.vue`
* `stores/inventory.js`
* `stores/stockMovements.js`
* `composables/useInventory.js`
* `composables/useStockMovements.js`

**Backend**

* `models/inventory.py`
* `models/stock_movement.py`
* `crud/inventory.py`
* `routers/stock_movement.py`
* `schemas/inventory.py`

**Tests**

* `inventory.spec.js`
* `test_ingest.py`

**Estado**

* Gestión de inventario completa.
* Movimientos persistentes.
* Integración frontend–backend operativa.

**Clasificación**

* **IMPLEMENTADO (END-TO-END)**

---

## 5.5 Sistema de Usuarios y Autenticación

### 5.5.1 Alcance Requerido

* Registro de usuarios.
* Autenticación.
* Gestión de roles.
* Administración de usuarios.

### 5.5.2 Evidencia de Implementación

**Frontend**

* `vue/components/auth/LoginForm.vue`
* `vue/components/auth/RegisterForm.vue`
* `vue/components/auth/AccountDelete.vue`
* `vue/components/auth/PasswordReset.vue`
* `stores/auth.js`
* `composables/useAuth.js`

**Backend**

* `routers/user.py`
* `models/user.py`
* `schemas/auth.py`
* `core/security.py`
* `scripts/create_admin.py`
* `scripts/promote_to_admin.py`

**Tests**

* `test_security_scan.py`

**Clasificación**

* **IMPLEMENTADO (OPERATIVO)**

---

## 5.6 Sistema de Pagos

### 5.6.1 Alcance Requerido

* Registro de pagos.
* Asociación pago–reparación.
* Control de concurrencia.
* Persistencia financiera.

### 5.6.2 Evidencia de Implementación

**Backend**

* `models/payment.py`
* `routers/payments.py`

**Tests**

* `test_payments_endpoints.py`
* `test_payments_concurrency.py`

**Clasificación**

* **IMPLEMENTADO (BACKEND OPERATIVO / UI NO EXPUESTA)**

---

## 5.7 Sistema Educativo y Contenidos

### 5.7.1 Alcance Requerido

* Artículos técnicos.
* FAQs.
* Contenidos educativos estructurados.
* Diagnóstico guiado.

### 5.7.2 Evidencia de Implementación

**Frontend**

* `vue/components/articles/*`
* `vue/components/articles/DiagnosticWizard.vue`
* `vue/sections/DiagnosticSection.vue`
* `vue/sections/FaqSection.vue`
* `vue/sections/PortfolioSection.vue`

**Clasificación**

* **IMPLEMENTADO (CONTENIDO ESTRUCTURAL Y FUNCIONAL)**

---

## 5.8 Sistema de Auditoría, Seguridad y Rate Limiting

### 5.8.1 Alcance Requerido

* Auditoría de acciones críticas.
* Registro de eventos.
* Limitación de tasa de requests.
* Seguridad transversal.

### 5.8.2 Evidencia de Implementación

**Backend**

* `models/audit.py`
* `core/ratelimit.py`
* `core/security.py`
* `services/logging_service.py`

**Tests**

* `test_ratelimit.py`
* `test_security_scan.py`

**Clasificación**

* **IMPLEMENTADO (INFRAESTRUCTURA DE SEGURIDAD Y AUDITORÍA)**
