# DE PROFUNDIS

## Proposito

Este documento profundiza el analisis de duplicacion en el "Zero" actual:

- Front: `CDS_VUE3_ZERO/src`
- Back: `backend/app`

El objetivo no es solo detectar similitud textual, sino distinguir entre:

- duplicacion real con costo de mantenimiento,
- duplicacion residual de una migracion no destructiva,
- paralelismo intencional pero mal delimitado,
- y falsos positivos estructurales.

## Metodo y alcance

Base objetiva usada antes de interpretar:

- hash de archivos para detectar duplicados exactos,
- recuento de basenames repetidos,
- barrido de bloques repetidos,
- y, sobre todo, lectura completa de los archivos citados en este documento.

Exclusiones deliberadas:

- `node_modules`
- `dist`
- `.venv`
- `uploads`
- logs
- DBs y artefactos de runtime

Superficie revisada como referencia:

- front fuente: 197 archivos
- back fuente: 171 archivos

## Archivos leidos completos para este analisis

Front:

- `CDS_VUE3_ZERO/src/components/ui/BaseButton.vue`
- `CDS_VUE3_ZERO/src/components/base/BaseButton.vue`
- `CDS_VUE3_ZERO/src/components/ui/BaseInput.vue`
- `CDS_VUE3_ZERO/src/components/base/BaseInput.vue`
- `CDS_VUE3_ZERO/src/components/base/BaseCalculatorPage.vue`
- `CDS_VUE3_ZERO/src/components/composite/DataTable.vue`
- `CDS_VUE3_ZERO/src/components/composite/FormField.vue`
- `CDS_VUE3_ZERO/src/components/base/index.js`
- `CDS_VUE3_ZERO/src/components/ui/index.js`
- `CDS_VUE3_ZERO/src/pages/calculators/commonCalculatorPage.css`
- `CDS_VUE3_ZERO/src/pages/calculators/LowHighPassFilterPage.vue`
- `CDS_VUE3_ZERO/src/pages/calculators/ResistorColorPage.vue`
- `CDS_VUE3_ZERO/src/pages/calculators/SmdResistorCodePage.vue`
- `CDS_VUE3_ZERO/src/pages/calculators/SmdCapacitorPage.vue`
- `CDS_VUE3_ZERO/src/pages/admin/RepairsAdminPage.vue`
- `CDS_VUE3_ZERO/src/pages/admin/ManualsPage.vue`
- `CDS_VUE3_ZERO/src/pages/admin/ClientsPage.vue`
- `CDS_VUE3_ZERO/src/pages/admin/InventoryPage.vue`
- `CDS_VUE3_ZERO/src/pages/admin/QuotesAdminPage.vue`

Back:

- `backend/app/main.py`
- `backend/app/api/v1/router.py`
- `backend/app/routers/instrument.py`
- `backend/app/api/v1/endpoints/instruments.py`
- `backend/app/routers/clients.py`
- `backend/app/routers/repair.py`
- `backend/app/routers/client.py`
- `backend/app/routers/purchase_requests.py`

## 1. Archivos repetidos

### 1.1. Front

Hallazgo duro:

- no hay archivos fuente duplicados exactos por contenido en `CDS_VUE3_ZERO/src`

Hallazgos de nombre, no de contenido:

- `BaseButton.vue` existe en `components/ui` y `components/base`
- `BaseInput.vue` existe en `components/ui` y `components/base`
- `index.js` aparece varias veces, pero eso es esperable como punto de exportacion

Conclusion:

- el problema del front no es de archivo clonado literal
- el problema es de arquitectura paralela activa

### 1.2. Back

Hallazgo duro:

- solo aparecio 1 grupo de "duplicados exactos"
- ese grupo esta formado por 7 archivos vacios de 0 bytes

Eso significa que, en el back, el problema tampoco es "copias exactas de archivos enteros" sino duplicacion funcional entre modulos activos.

### 1.3. Falsos positivos que no conviene sobre-interpretar

Estos nombres repetidos no son automaticamente deuda:

- `inventory.py` en model/schema/router/crud/api
- `repair.py` en model/schema/router/crud
- `category.py`, `appointment.py`, `user.py`, etc.

Ese patron es normal en una arquitectura por capas. No hay que mezclar "mismo basename" con "mismo codigo".

## 2. Front: duplicacion tecnica real

## 2.1. El front tiene dos micro-design-systems vivos

El hallazgo mas importante del front no es un copy/paste puntual, sino una bifurcacion activa:

- `components/base`
- `components/ui`

No estan muertos ni archivados. Ambos estan siendo consumidos.

Prueba leida completa:

- `components/composite/DataTable.vue` importa `../base/BaseInput.vue` y `../base/BaseButton.vue`
- `components/composite/FormField.vue` usa `../base/BaseInput.vue` como default para campos dinamicos
- auth y varias calculadoras importan `BaseInput` y `BaseButton` desde `@/components/ui`

Esto tiene tres implicancias tecnicas:

1. `BaseButton` no es uno solo. Hay dos contratos distintos.
2. `BaseInput` no es uno solo. Hay dos contratos distintos.
3. Cualquier intento de estandarizar formularios o tablas choca con APIs divergentes.

### Diferencia real entre los dos BaseButton

`components/ui/BaseButton.vue` es un atomico simple:

- 3 variantes basicas
- API minima
- slots prefijo/sufijo
- loading muy simple

`components/base/BaseButton.vue` ya es otra cosa:

- variantes ampliadas
- tamanos
- spinner propio
- `block`
- `rounded`
- hover/active states

Esto no es "mismo componente repetido". Es peor a nivel de mantenimiento:

- mismo nombre,
- distinto contrato,
- distinta semantica,
- y ambos activos.

### Diferencia real entre los dos BaseInput

`components/ui/BaseInput.vue`:

- soporte `modelModifiers`
- slots `prefix/suffix`
- API mas chica
- foco en integracion tipo formulario Vue clasico

`components/base/BaseInput.vue`:

- validacion inline
- `hint`
- `rightIcon`
- `readonly`
- `pattern`
- `size`
- emision `validate`

De nuevo: no es un duplicado exacto, pero si una duplicacion de responsabilidad de alto riesgo.

Diagnostico:

- el repo no tiene un design system unico
- tiene dos ramas activas de primitives
- y ya hay componentes de segundo orden (`DataTable`, `FormField`) amarrados a la rama `base`, mientras auth/calculadoras dependen de `ui`

## 2.2. Las calculadoras se partieron en dos familias que no convergieron

### Familia A: shell parcialmente compartido

Hay una extraccion real:

- `BaseCalculatorPage.vue`
- `commonCalculatorPage.css`

Eso resuelve:

- cabecera
- contenedor general
- layout general
- backlink
- paneles y estilos utilitarios comunes

Pero la extraccion es incompleta.

Ejemplo leido completo:

- `LowHighPassFilterPage.vue`

Aunque ya usa `BaseCalculatorPage` y `commonCalculatorPage.css`, sigue repitiendo a mano:

- panel de configuracion
- panel de resultado
- estructura de `panel-header`
- estructura de `panel-body`
- bloque de reset
- patron `value-row`

O sea: se factorizaron los bordes exteriores, pero no el patron de contenido que mas se repite.

### Familia B: calculadoras especializadas que reescriben casi todo

Archivos leidos completos:

- `ResistorColorPage.vue`
- `SmdResistorCodePage.vue`
- `SmdCapacitorPage.vue`

Los tres re-declaran localmente una gran cantidad de estructura ya presente en la familia A:

- `calc-page`
- `calc-container`
- `calc-header`
- `panel-header`
- `panel-title`
- `form-actions`
- `value-row`
- `back-link`

No son clones 1:1 porque cada pagina tiene visuales propios. Pero si constituyen una familia paralela con duplicacion de layout, tipografia, spacing y controles.

Interpretacion correcta:

- no es "mala praxis aislada"
- parece mas bien una evolucion historica donde algunas calculadoras nacieron antes del shell comun y nunca migraron del todo

## 2.3. Las paginas admin repiten el mismo page-shell localmente

Lectura completa de:

- `RepairsAdminPage.vue`
- `ManualsPage.vue`
- `ClientsPage.vue`
- `InventoryPage.vue`
- `QuotesAdminPage.vue`

Patron observado:

- mismo `admin-page`
- mismo `admin-header`
- mismo bloque de botones primarios/secundarios/peligro
- mismo `admin-error`
- mismas bases de `panel-card`
- mismo tratamiento de formularios simples
- misma tabla base
- mismo `empty-state`

La variacion entre paginas existe, pero arranca demasiado tarde.

Ejemplo tecnico:

- `RepairsAdminPage.vue` y `ManualsPage.vue` comparten casi toda la capa base del page-shell
- `ClientsPage.vue` extiende esa base con split layout y paneles anidados
- `InventoryPage.vue` agrega summary cards y flags
- `QuotesAdminPage.vue` suma modal y una variante `btn-success`

Eso indica que no falta CSS. Falta un nivel de abstraccion intermedio:

- o un layout/composable visual compartido para admin pages,
- o una hoja de estilos comun por dominio admin,
- o componentes de seccion reutilizables

Hoy cada pagina recompone el mismo esqueleto scoped desde cero.

## 3. Back: duplicacion tecnica real

## 3.1. El back ya sabe que tiene deuda de dedupe

La lectura completa de `backend/app/main.py` y `backend/app/api/v1/router.py` muestra algo importante:

- la duplicacion no es accidental pura
- parte de ella esta explicitamente reconocida en comentarios `DEDUPE FASE`

Eso cambia la interpretacion:

- hay codigo duplicado conservado a proposito para no romper migraciones
- pero no toda la duplicacion esta encapsulada ni realmente desactivada

## 3.2. `instruments.py` es duplicacion residual de migracion

Lectura completa de:

- `backend/app/routers/instrument.py`
- `backend/app/api/v1/endpoints/instruments.py`

Hecho tecnico:

- las funciones `load_instruments_data`, `get_instrument` y `get_instrument_image` estan duplicadas

Pero la lectura completa del router central muestra que el endpoint v1 duplicado ya no se monta.

Interpretacion:

- esto es deuda residual, no deuda operativa inmediata
- sigue siendo molesto porque aumenta superficie de confusion
- pero el riesgo de drift runtime es menor que en otros casos porque la fuente activa canonica parece ser `app.routers.instrument`

## 3.3. `_resolved_repair_code` esta duplicado en varios routers vivos

Este es el punto mas serio del back.

Aparece en:

- `backend/app/routers/repair.py`
- `backend/app/routers/client.py`
- `backend/app/routers/clients.py`
- `backend/app/routers/purchase_requests.py`

No es la misma firma en todos los casos, pero la logica de negocio es esencialmente la misma:

- respetar `repair_number` legacy si no empieza con `R-`
- si hay parent/sequence, calcular OT agrupada
- si no, calcular OT base

Esto ya no es residuo de migracion. Es duplicacion viva en routers activos que exponen dominios distintos.

Riesgo:

- si la nomenclatura OT cambia, hay que tocar 4 lugares
- si uno diverge, se rompen listados, PDFs, cliente final y solicitudes de compra en formas diferentes

## 3.4. `_auto_archive_repairs` tambien esta duplicado y activo

Aparece en:

- `backend/app/routers/repair.py`
- `backend/app/routers/clients.py`

Es poca logica, pero es logica con efecto de estado:

- calcula cutoff
- archiva
- cambia `status_id`
- hace `commit`

No es helper inofensivo. Es comportamiento de dominio con side effects.

Duplicarlo en routers distintos hace que el archivado dependa del endpoint que toque al registro.

## 3.5. `_safe_pdf_filename` esta repetido

Aparece en:

- `backend/app/routers/repair.py`
- `backend/app/routers/client.py`

No es el peor caso por tamano, pero refuerza el patron:

- helpers de presentacion/documento se estan copiando entre routers en lugar de moverse a servicio/utilidad compartida

## 3.6. Parseo de metadata JSON repetido

Lectura completa confirma este patron:

- `client.py` tiene `_parse_payment_notes`
- `purchase_requests.py` tiene `_parse_notes_metadata`

La logica es esencialmente la misma:

- trim
- intentar `json.loads`
- si falla, devolver `{"text": text}`

Esto es pequeno, pero indica que el dominio de pagos/solicitudes se expandio por copia y no por consolidacion.

## 3.7. La duplicacion mas cara: payload de cierre de reparacion

Este es el hotspot de mayor costo semantico.

Lectura completa de:

- `repair.py`
- `client.py`

En ambos existe un payload grande para PDF/cierre de reparacion:

- datos base de OT
- costos
- diagnostico
- trabajo realizado
- componentes
- notas
- datos de cliente
- datos de dispositivo
- intake sheet

No son identicos. Y justamente por eso son peligrosos.

La relacion real es esta:

- comparten el mismo nucleo de informacion
- pero `client.py` recorta y adapta para cliente final
- `repair.py` conserva una version mas rica y mas tecnica

Problema:

- hoy la diferenciacion esta codificada por copia de payload, no por composicion
- eso invita a drift silencioso

Ejemplo claro:

- `repair.py` usa `_serialize_intake_sheet(...)`
- `client.py` recompone a mano un subconjunto del intake sheet

La intencion de negocio es defendible.
La implementacion no.

## 3.8. Fragmentacion de routers: `/client` y `/clients` son ambos activos

El router central monta simultaneamente:

- `client_router`
- `clients_router`

Y ambos tocan dominio de cliente/reparacion, pero para audiencias distintas:

- `client.py` es portal de cliente final autenticado
- `clients.py` es admin CRUD

Eso por si mismo no es un error. El problema es que helpers compartibles entre ambos quedaron embebidos dentro de routers HTTP y no en servicios de dominio.

Resultado:

- la frontera HTTP quedo actuando como frontera de negocio

Eso explica por que la duplicacion esta concentrada justo en routers y no tanto en `services/`.

## 4. Clasificacion tecnica de la duplicacion

## 4.1. Duplicacion que conviene atacar primero

Alta prioridad:

- `_resolved_repair_code` en routers activos
- `_auto_archive_repairs` en routers activos
- payload de cierre/PDF entre `repair.py` y `client.py`
- page-shell admin repetido en SFCs
- convivencia activa `components/base` vs `components/ui`

## 4.2. Duplicacion real pero de prioridad media

- shell de calculadoras simples que solo factoriza el contenedor y no el patron config/resultado
- familia de calculadoras especializadas que no converge al shell comun
- parseo JSON repetido de notas/payment metadata
- `_safe_pdf_filename`

## 4.3. Duplicacion que hoy es mas residuo que riesgo

- `backend/app/api/v1/endpoints/instruments.py`

Motivo:

- el propio `api/v1/router.py` documenta que esa capa no se monta como fuente activa

## 4.4. Falsos positivos o no-problemas

- `__init__.py` vacios
- nombres repetidos por capa (`models`, `schemas`, `routers`, `crud`)
- `index.js` en puntos de exportacion

## 5. Lo que el analisis tecnico sugiere sobre la historia del repo

La duplicacion observada no parece venir de una sola causa. Viene de tres:

1. Migracion aditiva/no destructiva en backend.
2. Extraccion parcial de primitives y shells en frontend.
3. Crecimiento por feature local con estilos scoped y helpers HTTP embebidos.

Por eso el mapa de duplicacion no es homogeneo:

- en back domina la duplicacion de logica de negocio embebida en routers
- en front domina la duplicacion de shell visual y primitives paralelos

## 6. Prioridad de consolidacion recomendada

Orden pragmatico:

1. Extraer a servicio/utilidad compartida:
   - `_resolved_repair_code`
   - `_auto_archive_repairs`
   - `_safe_pdf_filename`
   - parseo de notas metadata

2. Separar en el back:
   - builders de payload canonico
   - adaptadores de vista admin
   - adaptadores de vista cliente

3. En el front:
   - elegir un solo namespace canonico para primitives (`base` o `ui`)
   - dejar el otro como compat layer temporal, no como libreria paralela viva

4. Extraer page-shell admin comun:
   - header
   - error banner
   - action buttons
   - panel base
   - tabla base

5. Completar la convergencia de calculadoras:
   - o todas al shell comun
   - o declarar explicitamente una subfamilia visual especializada y dejar de fingir unificacion parcial

## 7. Conclusiones directas

- No hay una plaga de archivos clonados exactos.
- Si hay duplicacion funcional seria en back, concentrada en routers vivos.
- Si hay duplicacion estructural seria en front, concentrada en shells visuales y primitives paralelos.
- La deuda mas peligrosa no es textual; es semantica.
- El punto mas delicado del repo hoy es este: una misma regla de negocio se reimplementa desde varias fronteras HTTP.

Eso, mas que cualquier CSS repetido, es lo que puede producir divergencia real de comportamiento.
