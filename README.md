# Cirujano de Sintetizadores

Repositorio principal del sistema web de Cirujano de Sintetizadores.

Este proyecto concentra el frontend público y administrativo, el backend principal y las utilidades internas que sostienen la operación del sitio, el taller y los flujos asociados.

## Qué es este repo

El repositorio está siendo trabajado como un monolito modular:

- un frontend principal en Vue 3
- un backend principal en FastAPI
- utilidades y scripts de soporte
- piezas temporales o satélite, mantenidas separadas del núcleo canónico

La dirección de trabajo no es reescribir desde cero, sino deconstruir piezas grandes, extraer contratos compartidos y reducir duplicación sin romper compatibilidad donde todavía se necesita.

## Estructura general

```text
cirujano-front_CLEAN/
├── CDS_VUE3_ZERO/    frontend Vue 3 principal
├── backend/          API FastAPI y lógica principal
├── scripts/          utilidades de soporte y sincronización
├── coming-soon-vue/  landing temporal separada del frontend principal
└── .github/          automatizaciones del repositorio
```

## Arquitectura actual

### Frontend principal

`CDS_VUE3_ZERO/` es la aplicación principal del proyecto.

Incluye, entre otros:

- home pública
- cotizador público
- panel administrativo
- portal de cliente
- inventario y tienda
- agenda
- media
- calculadoras electrónicas

La dirección actual del frontend es seguir partiendo lógica grande en composables, servicios y componentes más finos, manteniendo contratos existentes mientras todavía haya consumo legacy.

### Backend principal

`backend/` contiene la API principal y la mayor parte de la lógica operativa.

Incluye, entre otros:

- autenticación
- clientes, equipos y reparaciones
- cotizaciones
- inventario
- agenda
- media
- pagos
- portal cliente
- utilidades de reporting y soporte

La dirección actual del backend es reducir routers con demasiadas responsabilidades, consolidar contratos canónicos y empujar reglas compartidas hacia capas reutilizables.

## Hegemonías actuales del sistema

Estas son las fuentes de verdad que hoy se están consolidando:

- cotizador público: contrato canónico bajo `quotation`
- media runtime: contrato canónico orientado a Cloudinary
- inventario: contrato canónico bajo `/inventory`
- compatibilidad legacy: se conserva sólo donde todavía hace falta, pero ya no debe gobernar el runtime

En particular:

- `image-mapping.json` ya no debe ser fuente de verdad de runtime
- `/items` existe por compatibilidad, pero la dirección canónica es `/inventory`
- wrappers legacy deben comportarse como compatibilidad, no como sistemas paralelos

## Estado técnico resumido

El repositorio ya avanzó bastante en modularización visual y de contratos. La deuda principal ya no está tanto en páginas enteras renderizando todo, sino en lógica concentrada en algunos composables, routers y servicios grandes.

Frentes que ya han sido fuertemente deconstruidos:

- home pública
- shell público
- cotizador público
- intake wizard
- repair detail admin
- dashboard y varias vistas admin
- integración media/Cloudinary
- compatibilidad `/items` vs `/inventory`

Frentes todavía pesados:

- `MediaPage.vue`
- `AdminShellLayout.vue`
- `quote_management_router.py`
- `repair.py`
- `client_portal.py`
- algunos servicios de reporting y reparación

## Cómo se ha trabajado

La disciplina aplicada al repo sigue estas reglas:

- cambios aditivos, no destructivos por defecto
- deconstrucción antes que reescritura total
- reutilizar piezas existentes antes de crear otras nuevas
- no duplicar contratos ni lógica si ya existe una capa válida
- mantener compatibilidad legacy sólo donde todavía sea necesaria
- validar con build y/o tests antes de dar por cerrado un corte
- no documentar secretos ni detalles sensibles en archivos públicos

## Desarrollo local

### Frontend principal

```bash
cd CDS_VUE3_ZERO
npm install
npm run dev
```

Build:

```bash
cd CDS_VUE3_ZERO
npm run build
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Validación

### Frontend

La validación mínima del frontend hoy es:

```bash
cd CDS_VUE3_ZERO
npm run build
```

### Backend

La validación del backend depende del frente que se esté tocando. La base general es:

```bash
cd backend
pytest tests/ --verbose
```

Cuando un corte es temático, se prefieren corridas focalizadas sobre los tests realmente afectados.

## Documentación

Este `README.md` está pensado como resumen técnico y seguro de alto nivel.

No debe contener:

- credenciales
- tokens
- passwords
- correos privados
- rutas locales sensibles
- configuraciones de producción
- datos de clientes

La planificación operativa detallada y el seguimiento fino del avance se mantienen en documentos de trabajo separados, sin tratarlos como documentación pública canónica del proyecto.

## Seguridad

- No se versionan secretos reales en este archivo.
- La configuración sensible debe resolverse vía variables de entorno o canales internos controlados.
- Ningún README del proyecto debe exponer claves, tokens, secretos de servicios externos ni datos operativos sensibles.
