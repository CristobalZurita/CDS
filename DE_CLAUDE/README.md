# 🎹 Sistema de Cotización Interactiva con Diagnóstico Visual

Sistema completo de diagnóstico visual para instrumentos musicales con marcado interactivo de fallas, cotización automática, y dashboard para técnicos.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Vue](https://img.shields.io/badge/vue-3.0+-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.109+-teal.svg)

---

## ✨ Características Principales

### Para Clientes
- 📸 **Upload de Fotos**: Sube múltiples vistas de tu instrumento
- 🎯 **Marcado Interactivo**: Marca fallas directamente sobre las fotos con doble clic
- 📝 **Planilla de Componentes**: Completa checklist detallado de partes
- 💰 **Cotización Instantánea**: Recibe estimación preliminar al instante
- 📧 **Código de Referencia**: Sistema de tracking con código único
- ⚠️ **Disclaimer Claro**: Información transparente sobre el proceso

### Para Técnicos
- 📊 **Dashboard Completo**: Vista general de todos los diagnósticos
- 🔧 **Gestión de Templates**: Crea y administra plantillas de instrumentos
- 🤖 **Detección OpenCV**: Identificación automática de controles en fotos
- ✏️ **Ajuste de Cotizaciones**: Modifica precios manualmente
- 📈 **Seguimiento de Estado**: Workflow completo (pendiente → completado)
- 📷 **Evidencia Fotográfica**: Todas las fotos guardadas con marcadores

---

## 🚀 Quick Start

### Opción 1: Setup Rápido con Docker

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/diagnostic-system.git
cd diagnostic-system

# Construir y ejecutar
docker-compose up -d

# Acceder
# Frontend: http://localhost
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Opción 2: Instalación Manual

#### 1. Backend (Python/FastAPI)

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python -c "from backend_api import Base, engine; Base.metadata.create_all(engine)"

# Seed data (opcional)
curl -X POST http://localhost:8000/api/admin/seed-database

# Ejecutar servidor
uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend (Vue 3)

```bash
# Instalar dependencias
npm install

# Copiar componentes
cp InteractiveInstrumentDiagnostic.vue src/components/
cp TechnicianDashboard.vue src/components/

# Configurar rutas (ver DOCUMENTATION.md)

# Ejecutar desarrollo
npm run dev

# Build producción
npm run build
```

---

## 📁 Estructura del Proyecto

```
diagnostic-system/
├── backend/
│   ├── backend_api.py          # FastAPI app principal
│   ├── requirements.txt         # Dependencias Python
│   └── uploads/                 # Directorio de fotos
│
├── frontend/
│   ├── components/
│   │   ├── InteractiveInstrumentDiagnostic.vue
│   │   └── TechnicianDashboard.vue
│   ├── router/
│   │   └── index.js            # Configuración de rutas
│   └── package.json
│
├── docker-compose.yml           # Orquestación Docker
├── DOCUMENTATION.md             # Documentación completa
└── README.md                    # Este archivo
```

---

## 🎯 Flujo de Uso

### Cliente: Enviar Diagnóstico

1. **Seleccionar Instrumento**
   - Buscar en catálogo o subir fotos propias
   - Mínimo 2 fotos (frontal y trasera)

2. **Completar Planilla**
   - Marcar componentes presentes (teclas, knobs, etc.)
   - Indicar cantidades

3. **Marcar Fallas**
   - Seleccionar tipo de falla
   - Doble clic sobre componente afectado
   - Repetir para todas las fallas

4. **Confirmar y Enviar**
   - Revisar resumen
   - Aceptar disclaimer
   - Recibir código de referencia

### Técnico: Revisar Diagnóstico

1. **Dashboard**
   - Ver diagnósticos pendientes
   - Filtrar por estado

2. **Revisar Detalles**
   - Información del cliente
   - Fotos con marcadores
   - Cotización preliminar

3. **Ajustar Cotización**
   - Modificar precios si es necesario
   - Agregar notas internas

4. **Enviar al Cliente**
   - Aprobar cotización
   - Enviar por email

---

## 🔧 Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para manejo de base de datos
- **OpenCV** - Procesamiento y análisis de imágenes
- **Pydantic** - Validación de datos

### Frontend
- **Vue 3** - Framework JavaScript progresivo
- **Composition API** - Lógica reutilizable
- **Canvas API** - Marcado interactivo de fotos
- **SCSS** - Estilos avanzados

### Base de Datos
- **SQLite** (desarrollo)
- **PostgreSQL** (producción)

---

## 📊 API Endpoints

### Instrumentos
```
GET    /api/instruments              # Lista de instrumentos
GET    /api/instruments/{id}         # Detalle de instrumento
POST   /api/instruments/{id}/detect  # Detectar controles (OpenCV)
```

### Diagnósticos
```
POST   /api/diagnostics/submit       # Enviar diagnóstico
GET    /api/diagnostics/{code}       # Obtener por código
```

### Cotizaciones
```
POST   /api/quotes/{id}/approve      # Aprobar cotización
```

Ver documentación completa en `/docs` (Swagger UI)

---

## 💡 Ejemplos de Uso

### Cliente: Enviar Diagnóstico (JavaScript)

```javascript
const formData = {
  instrument_id: 1,
  selected_components: ['keys', 'knobs', 'sliders'],
  component_quantities: {
    keys: 61,
    knobs: 12,
    sliders: 8
  },
  photos: [
    {
      view: 'front',
      base64_image: 'data:image/jpeg;base64,...',
      markers: [
        {
          x: 150.5,
          y: 200.3,
          type: 'broken',
          timestamp: Date.now()
        }
      ]
    }
  ],
  customer_name: 'Juan Pérez',
  customer_email: 'juan@email.com'
}

const response = await fetch('/api/diagnostics/submit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(formData)
})

const result = await response.json()
console.log('Código de referencia:', result.reference_code)
```

### Técnico: Obtener Diagnósticos (Python)

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(
        'http://localhost:8000/api/diagnostics/DIAG-ABC12345'
    )
    diagnostic = response.json()
    
    print(f"Cliente: {diagnostic['customer_name']}")
    print(f"Estado: {diagnostic['status']}")
    print(f"Total: ${diagnostic['quote']['total']}")
```

---

## 🎨 Capturas de Pantalla

### Vista Cliente: Marcado de Fallas
![Marcado Interactivo](docs/images/screenshot-marking.png)

### Vista Técnico: Dashboard
![Dashboard Técnico](docs/images/screenshot-dashboard.png)

*(Notas: Agregar capturas reales)*

---

## 🧪 Testing

### Backend
```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=backend_api --cov-report=html

# Test específico
pytest tests/test_quotation.py::test_calculate_quote_basic
```

### Frontend
```bash
# Ejecutar tests
npm run test

# Con watch
npm run test:watch

# E2E tests
npm run test:e2e
```

---

## 🔐 Seguridad

### Validaciones Implementadas
- ✅ Validación de formato de email
- ✅ Sanitización de imágenes
- ✅ Límite de tamaño de archivo (10MB)
- ✅ Rate limiting (5 requests/hora)
- ✅ SQL injection protection (ORM)
- ✅ XSS protection

### Recomendaciones Adicionales
- Implementar autenticación JWT para técnicos
- Usar HTTPS en producción
- Configurar CORS apropiadamente
- Encriptar datos sensibles
- Realizar auditorías de seguridad

---

## 📈 Performance

### Optimizaciones Implementadas
- Índices en base de datos
- Compresión de imágenes
- Lazy loading de fotos
- Paginación de resultados
- Cache de catálogo

### Métricas Objetivo
- Tiempo de carga inicial: < 2s
- Tiempo de respuesta API: < 500ms
- Procesamiento de imagen: < 3s
- Tamaño de bundle: < 500KB

---

## 🐛 Troubleshooting

### Problema: OpenCV no detecta controles
**Solución:**
```python
# Ajustar parámetros de detección
circles = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=20,      # Reducir distancia mínima
    param1=40,       # Bajar umbral
    param2=25,       # Bajar umbral acumulador
    minRadius=8,     # Radio más pequeño
    maxRadius=60     # Radio más grande
)
```

### Problema: Cálculo de cotización incorrecto
**Solución:**
1. Verificar `FAULT_BASE_PRICES` actualizados
2. Revisar `complexity_tier` del instrumento
3. Validar `component_quantities` en request

### Problema: Fotos no se guardan
**Solución:**
```bash
# Verificar permisos
chmod 755 uploads/

# Verificar espacio en disco
df -h

# Verificar logs
tail -f diagnostic_system.log
```

---

## 🚢 Deployment

### Producción con Docker

```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose logs -f backend

# Backup database
docker-compose exec db pg_dump -U user diagnostic > backup.sql
```

### Variables de Entorno

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/diagnostic
SECRET_KEY=your-secret-key-here
UPLOAD_DIR=/var/www/uploads
MAX_FILE_SIZE=10485760
ALLOWED_ORIGINS=https://tudominio.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@tudominio.com
SMTP_PASSWORD=your-password
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guidelines
- Seguir PEP 8 para Python
- Usar Vue style guide
- Escribir tests para nuevas features
- Actualizar documentación

---

## 📝 Roadmap

### v1.1 (Q2 2026)
- [ ] Email notifications automáticas
- [ ] Generación de PDF reportes
- [ ] Integración de pagos online
- [ ] Sistema de anticipos

### v1.2 (Q3 2026)
- [ ] App móvil (iOS/Android)
- [ ] Machine learning para clasificación de fallas
- [ ] Sistema de inventario de partes
- [ ] Dashboard de analytics

### v2.0 (Q4 2026)
- [ ] Multi-tenant (múltiples talleres)
- [ ] API pública
- [ ] Marketplace de partes
- [ ] Sistema de garantías

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

## 📞 Contacto

**Tu Empresa**
- Website: https://tudominio.com
- Email: soporte@tudominio.com
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Twitter: [@tu-handle](https://twitter.com/tu-handle)

---

## 🙏 Agradecimientos

- FastAPI por el excelente framework
- Vue.js por la reactivity system
- OpenCV por las herramientas de visión computacional
- Comunidad open source

---

## 📚 Recursos Adicionales

- [Documentación Completa](DOCUMENTATION.md)
- [API Reference](http://localhost:8000/docs)
- [Video Tutorial](https://youtube.com/...)
- [Blog Post](https://blog.tudominio.com/...)

---

**Versión:** 1.0.0  
**Última actualización:** Enero 2026  
**Mantenido por:** Tu Empresa

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!
