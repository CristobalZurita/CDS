#!/bin/bash

# =============================================================================
# VOLCADO COMPLETO DE CÓDIGO FUNCIONAL - CDS
# =============================================================================
# Extrae TODO el código relevante del proyecto
# Target: ~7MB de texto puro con implementación completa
# Frontend (Vue) + Backend (Python) + Configs
# =============================================================================

OUTPUT_FILE="AUDITORIA_CDS_COMPLETA_$(date +%Y%m%d_%H%M%S).txt"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}       GENERANDO VOLCADO COMPLETO DE CÓDIGO - CDS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"

# Contador de archivos
COUNTER=0

# =============================================================================
# FUNCIÓN PARA AGREGAR ARCHIVO
# =============================================================================
add_file() {
    local file=$1
    local label=$2
    
    if [ -f "$file" ]; then
        echo "" >> "$OUTPUT_FILE"
        echo "╔═══════════════════════════════════════════════════════════════════════════╗" >> "$OUTPUT_FILE"
        echo "║ FILE: $label" >> "$OUTPUT_FILE"
        echo "║ PATH: $file" >> "$OUTPUT_FILE"
        echo "╚═══════════════════════════════════════════════════════════════════════════╝" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        cat "$file" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "───────────────────────────────────────────────────────────────────────────" >> "$OUTPUT_FILE"
        ((COUNTER++))
        echo -e "${GREEN}✓${NC} [$COUNTER] $file"
    else
        echo -e "${YELLOW}⚠${NC} No encontrado: $file"
    fi
}

# =============================================================================
# HEADER DEL DOCUMENTO
# =============================================================================
cat > "$OUTPUT_FILE" << 'HEADER'
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                   AUDITORÍA COMPLETA DE CÓDIGO                           ║
║                   CIRUJANO DE SINTETIZADORES (CDS)                       ║
║                                                                           ║
║  Volcado completo de código fuente para análisis de:                     ║
║  • Funcionalidades implementadas                                         ║
║  • Arquitectura y estructura                                             ║
║  • Gaps y pendientes                                                     ║
║  • Calidad y mantenibilidad                                              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

GENERADO: $(date '+%Y-%m-%d %H:%M:%S')
PROYECTO: CDS - Cirujano de Sintetizadores
REPOSITORY: https://github.com/CristobalZurita/CDS

═══════════════════════════════════════════════════════════════════════════

HEADER

# =============================================================================
# SECCIÓN 1: CONFIGURACIONES Y MANIFIESTOS
# =============================================================================
echo -e "\n${BLUE}[SECCIÓN 1/10]${NC} Configuraciones del Proyecto"

cat >> "$OUTPUT_FILE" << 'S1'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SECCIÓN 1: CONFIGURACIONES Y MANIFIESTOS                                ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

S1

add_file "package.json" "Package.json - Dependencias y Scripts Frontend"
add_file "backend/requirements.txt" "Requirements.txt - Dependencias Python"
add_file "vite.config.js" "Vite - Configuración de Build"
add_file "tsconfig.json" "TypeScript - Configuración"
add_file "vitest.config.js" "Vitest - Configuración de Testing"
add_file "eslint.config.cjs" "ESLint - Configuración de Linting"

# =============================================================================
# SECCIÓN 2: FRONTEND - BOOTSTRAP Y ROUTER
# =============================================================================
echo -e "\n${BLUE}[SECCIÓN 2/10]${NC} Frontend - Bootstrap y Routing"

cat >> "$OUTPUT_FILE" << 'S2'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SECCIÓN 2: FRONTEND - BOOTSTRAP, ROUTER Y APP PRINCIPAL                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

S2

add_file "src/main.js" "Main.js - Punto de Entrada Vue"
add_file "src/router/index.js" "Router - Configuración de Rutas (JS)"
add_file "src/router/index.ts" "Router - Configuración de Rutas (TS)"
add_file "src/vue/stack/App.vue" "App.vue - Componente Raíz"
add_file "src/vue/stack/StateProviderLayer.vue" "StateProviderLayer - Proveedor de Estado"
add_file "src/vue/stack/FeedbacksLayer.vue" "FeedbacksLayer - Sistema de Notificaciones"
add_file "src/vue/content/Master.vue" "Master.vue - Layout Principal"

# =============================================================================
# SECCIÓN 3: STORES - GESTIÓN DE ESTADO
# =============================================================================
echo -e "\n${BLUE}[SECCIÓN 3/10]${NC} Stores - Gestión de Estado (Pinia)"

cat >> "$OUTPUT_FILE" << 'S3'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SECCIÓN 3: STORES (PINIA) - GESTIÓN DE ESTADO GLOBAL                    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

S3

add_file "src/stores/auth.js" "Store: Autenticación"
add_file "src/stores/categories.js" "Store: Categorías"
add_file "src/stores/diagnostics.js" "Store: Diagnósticos"
add_file "src/stores/instruments.js" "Store: Instrumentos"
add_file "src/stores/inventory.js" "Store: Inventario"
add_file "src/stores/quotation.js" "Store: Cotizaciones"
add_file "src/stores/repairs.js" "Store: Reparaciones"
add_file "src/stores/stockMovements.js" "Store: Movimientos de Stock"
add_file "src/stores/users.js" "Store: Usuarios"

# =============================================================================
# SECCIÓN 4: COMPOSABLES - LÓGICA REUTILIZABLE
# =============================================================================
echo -e "\n${BLUE}[SECCIÓN 4/10]${NC} Composables - Lógica de Negocio"

cat >> "$OUTPUT_FILE" << 'S4'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SECCIÓN 4: COMPOSABLES - HOOKS Y LÓGICA REUTILIZABLE                    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

S4

add_file "src/composables/useApi.js" "Composable: API Client"
add_file "src/composables/useAuth.js" "Composable: Autenticación"
add_file "src/composables/useCalculator.ts" "Composable: Calculadoras"
add_file "src/composables/useCategories.js" "Composable: Categorías"
add_file "src/composables/useDiagnostic.js" "Composable: Diagnóstico Individual"
add_file "src/composables/useDiagnostics.js" "Composable: Diagnósticos"
add_file "src/composables/useInstruments.js" "Composable: Instrumentos"
add_file "src/composables/useInstrumentsCatalog.js" "Composable: Catálogo de Instrumentos"
add_file "src/composables/useInventory.js" "Composable: Inventario"
add_file "src/composables/useQuotation.js" "Composable: Cotizaciones"
add_file "src/composables/useRepairs.js" "Composable: Reparaciones"
add_file "src/composables/useStockMovements.js" "Composable: Movimientos de Stock"
add_file "src/composables/useUsers.js" "Composable: Usuarios"
add_file "src/composables/useValidation.ts" "Composable: Validaciones"
add_file "src/composables/strings.js" "Composable: Utilidades de Strings"

# =============================================================================
# SECCIÓN 5: PÁGINAS PRINCIPALES
# =============================================================================
echo -e "\n${BLUE}[SECCIÓN 5/10]${NC} Páginas - Vistas Principales"

cat >> "$OUTPUT_FILE" << 'S5'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SECCIÓN 5: PÁGINAS - VISTAS PRINCIPALES DE LA APLICACIÓN                ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

═══ PÁGINAS PÚBLICAS ═══

S5

add_file "src/vue/content/pages/HomePage.vue" "Página: Home"
add_file "src/vue/content/pages/LoginPage.vue" "Página: Login"
add_file "src/vue/content/pages/RegisterPage.vue" "Página: Registro"
add_file "src/vue/content/pages/CotizadorIAPage.vue" "Página: Cotizador con IA"
add_file "src/vue/content/pages/RepairsPage.vue" "Página: Reparaciones (Cliente)"
add_file "src/vue/content/pages/SchedulePage.vue" "Página: Agenda/Citas"
add_file "src/vue/content/pages/DashboardPage.vue" "Página: Dashboard Cliente"
add_file "src/vue/content/pages/ProfilePage.vue" "Página: Perfil de Usuario"
add_file "src/vue/content/pages/PrivacyPage.vue" "Página: Privacidad"
add_file "src/vue/content/pages/TermsPage.vue" "Página: Términos"

cat >> "$OUTPUT_FILE" << 'ADMIN'

═══ PÁGINAS ADMINISTRACIÓN ═══

ADMIN

add_file "src/vue/content/pages/admin/AdminDashboard.vue" "Admin: Dashboard Principal"
add_file "src/vue/content/pages/admin/CategoriesPage.vue" "Admin: Gestión de Categorías"
add_file "src/vue/content/pages/admin/ClientsPage.vue" "Admin: Gestión de Clientes"
add_file "src/vue/content/pages/admin/InventoryPage.vue" "Admin: Gestión de Inventario"
add_file "src/vue/content/pages/admin/RepairsAdminPage.vue" "Admin: Gestión de Reparaciones"
add_file "src/vue/content/pages/admin/StatsPage.vue" "Admin: Estadísticas"

# =============================================================================
# SECCIÓN 6: COMPONENTES - ADMIN
# =============================================================================
echo -e "\n${BLUE}[SECCIÓN 6/10]${NC} Componentes - Administración"

cat >> "$OUTPUT_FILE" << 'S6'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SECCIÓN 6: COMPONENTES - ADMINISTRACIÓN                                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

S6

add_file "src/vue/components/admin/CategoryForm.vue" "Admin: Formulario de Categorías"
add_file "src/vue/components/admin/CategoryList.vue" "Admin: Lista de Categorías"
add_file "src/vue/components/admin/CategoryManager.vue" "Admin: Gestor de Categorías"
add_file "src/vue/components/admin/ClientDetail.vue" "Admin: Detalle de Cliente"
add_file "src/vue/components/admin/ClientList.vue" "Admin: Lista de Clientes"
add_file "src/vue/components/admin/DiagnosticsList.vue" "Admin: Lista de Diagnósticos"
add_file "src/vue/components/admin/InstrumentForm.vue" "Admin: Formulario de Instrumentos"
add_file "src/vue/components/admin/InstrumentList.vue" "Admin: Lista de Instrumentos"
add_file "src/vue/components/admin/InventoryAlerts.vue" "Admin: Alertas de Inventario"
add_file "src/vue/components/admin/InventoryForm.vue" "Admin: Formulario de Inventario"
add_file "src/vue/components/admin/InventoryTable.vue" "Admin: Tabla de Inventario"
add_file "src/vue/components/admin/RepairForm.vue" "Admin: Formulario de Reparaciones"
add_file "src/vue/components/admin/RepairManager.vue" "Admin: Gestor de Reparaciones"
add_file "src/vue/components/admin/RepairStatusEditor.vue" "Admin: Editor de Estados"
add_file "src/vue/components/admin/RepairsList.vue" "Admin: Lista de Reparaciones"
add_file "src/vue/components/admin/StatsCards.vue" "Admin: Tarjetas de Estadísticas"
add_file "src/vue/components/admin/StockMovements.vue" "Admin: Movimientos de Stock"
add_file "src/vue/components/admin/StockMovementsList.vue" "Admin: Lista de Movimientos"
add_file "src/vue/components/admin/UserForm.vue" "Admin: Formulario de Usuarios"
add_file "src/vue/components/admin/UserList.vue" "Admin: Lista de Usuarios"

# =============================================================================
# SECCIÓN 7: COMPONENTES - AI Y FEATURES
# =============================================================================
echo -e "\n${BLUE}[SECCIÓN 7/10]${NC} Componentes - IA y Features Principales"

cat >> "$OUTPUT_FILE" << 'S7'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SECCIÓN 7: COMPONENTES - INTELIGENCIA ARTIFICIAL Y FEATURES             ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

═══ COMPONENTES IA ═══

S7

add_file "src/vue/components/ai/AIAnalysisResult.vue" "AI: Resultado de Análisis"
add_file "src/vue/components/ai/FaultDetector.vue" "AI: Detector de Fallas"
add_file "src/vue/components/ai/FaultMarker.vue" "AI: Marcador de Fallas"
add_file "src/vue/components/ai/ImageUploader.vue" "AI: Subida de Imágenes"
add_file "src/vue/components/ai/QuoteGenerator.vue" "AI: Generador de Cotizaciones"

cat >> "$OUTPUT_FILE" << 'AUTH'

═══ COMPONENTES AUTENTICACIÓN ═══

AUTH

add_file "src/vue/components/auth/AccountDelete.vue" "Auth: Eliminación de Cuenta"
add_file "src/vue/components/auth/LoginForm.vue" "Auth: Formulario de Login"
add_file "src/vue/components/auth/PasswordReset.vue" "Auth: Reseteo de Contraseña"
add_file "src/vue/components/auth/RegisterForm.vue" "Auth: Formulario de Registro"

cat >> "$OUTPUT_FILE" << 'DASH'

═══ COMPONENTES DASHBOARD ═══

DASH

add_file "src/vue/components/dashboard/DashboardPanel.vue" "Dashboard: Panel Principal"
add_file "src/vue/components/dashboard/QuickStats.vue" "Dashboard: Estadísticas Rápidas"
add_file "src/vue/components/dashboard/RepairCard.vue" "Dashboard: Tarjeta de Reparación"
add_file "src/vue/components/dashboard/RepairTimeline.vue" "Dashboard: Timeline de Reparación"
add_file "src/vue/components/dashboard/RepairsList.vue" "Dashboard: Lista de Reparaciones"
add_file "src/vue/components/dashboard/StatusBadge.vue" "Dashboard: Badge de Estado"
add_file "src/vue/components/dashboard/UserProfile.vue" "Dashboard: Perfil de Usuario"

cat >> "$OUTPUT_FILE" << 'QUOT'

═══ COMPONENTES COTIZACIÓN ═══

QUOT

add_file "src/vue/components/quotation/DisclaimerModal.vue" "Cotización: Modal de Disclaimer"
add_file "src/vue/components/quotation/InstrumentSelector.vue" "Cotización: Selector de Instrumentos"
add_file "src/vue/components/quotation/QuotationResult.vue" "Cotización: Resultado"

# =============================================================================
# SECCIÓN 8: BACKEND - CORE Y CONFIGURACIÓN
# =============================================================================
echo -e "\n${BLUE}[SECCIÓN 8/10]${NC} Backend - Core y Configuración"

cat >> "$OUTPUT_FILE" << 'S8'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SECCIÓN 8: BACKEND - FASTAPI CORE                                        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

═══ APLICACIÓN PRINCIPAL ═══

S8

add_file "backend/app/main.py" "Main - Aplicación FastAPI"
add_file "backend/app/core/config.py" "Core: Configuración"
add_file "backend/app/core/database.py" "Core: Base de Datos"
add_file "backend/app/core/dependencies.py" "Core: Dependencias"
add_file "backend/app/core/security.py" "Core: Seguridad y Auth"
add_file "backend/app/core/logging_config.py" "Core: Configuración de Logging"
add_file "backend/app/core/ratelimit.py" "Core: Rate Limiting"

# =============================================================================
# SECCIÓN 9: BACKEND - MODELOS Y SCHEMAS
# =============================================================================
echo -e "\n${BLUE}[SECCIÓN 9/10]${NC} Backend - Modelos y Schemas"

cat >> "$OUTPUT_FILE" << 'S9'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SECCIÓN 9: BACKEND - MODELOS SQLAlchemy Y SCHEMAS PYDANTIC              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

═══ MODELOS SQLAlchemy ═══

S9

add_file "backend/app/models/user.py" "Modelo: Usuario"
add_file "backend/app/models/appointment.py" "Modelo: Cita/Appointment"
add_file "backend/app/models/audit.py" "Modelo: Auditoría"
add_file "backend/app/models/brand.py" "Modelo: Marca"
add_file "backend/app/models/category.py" "Modelo: Categoría"
add_file "backend/app/models/diagnostic.py" "Modelo: Diagnóstico"
add_file "backend/app/models/instrument.py" "Modelo: Instrumento"
add_file "backend/app/models/inventory.py" "Modelo: Inventario"
add_file "backend/app/models/payment.py" "Modelo: Pago"
add_file "backend/app/models/repair.py" "Modelo: Reparación"
add_file "backend/app/models/stock_movement.py" "Modelo: Movimiento de Stock"

cat >> "$OUTPUT_FILE" << 'SCHEMAS'

═══ SCHEMAS Pydantic ═══

SCHEMAS

add_file "backend/app/schemas/appointment.py" "Schema: Appointment"
add_file "backend/app/schemas/auth.py" "Schema: Autenticación"
add_file "backend/app/schemas/category.py" "Schema: Categoría"
add_file "backend/app/schemas/diagnostic.py" "Schema: Diagnóstico"
add_file "backend/app/schemas/inventory.py" "Schema: Inventario"
add_file "backend/app/schemas/repair.py" "Schema: Reparación"
add_file "backend/app/schemas/user.py" "Schema: Usuario"

# =============================================================================
# SECCIÓN 10: BACKEND - ROUTERS, CRUD Y SERVICIOS
# =============================================================================
echo -e "\n${BLUE}[SECCIÓN 10/10]${NC} Backend - Routers, CRUD y Servicios"

cat >> "$OUTPUT_FILE" << 'S10'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SECCIÓN 10: BACKEND - ENDPOINTS, CRUD Y SERVICIOS                       ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

═══ ROUTERS ═══

S10

add_file "backend/app/routers/user.py" "Router: Usuarios"
add_file "backend/app/routers/appointment.py" "Router: Citas"
add_file "backend/app/routers/category.py" "Router: Categorías"
add_file "backend/app/routers/contact.py" "Router: Contacto"
add_file "backend/app/routers/diagnostic.py" "Router: Diagnósticos"
add_file "backend/app/routers/instrument.py" "Router: Instrumentos"
add_file "backend/app/routers/payments.py" "Router: Pagos"
add_file "backend/app/routers/quotation.py" "Router: Cotizaciones"
add_file "backend/app/routers/repair.py" "Router: Reparaciones"
add_file "backend/app/routers/stock_movement.py" "Router: Movimientos de Stock"
add_file "backend/app/routers/uploads.py" "Router: Subida de Archivos"

cat >> "$OUTPUT_FILE" << 'API'

═══ API V1 ENDPOINTS ═══

API

add_file "backend/app/api/v1/router.py" "API V1: Router Principal"
add_file "backend/app/api/v1/endpoints/ai.py" "API V1: Endpoints de IA"
add_file "backend/app/api/v1/endpoints/auth.py" "API V1: Endpoints de Auth"
add_file "backend/app/api/v1/endpoints/brands.py" "API V1: Endpoints de Marcas"
add_file "backend/app/api/v1/endpoints/categories.py" "API V1: Endpoints de Categorías"
add_file "backend/app/api/v1/endpoints/diagnostics.py" "API V1: Endpoints de Diagnósticos"
add_file "backend/app/api/v1/endpoints/imports.py" "API V1: Endpoints de Importación"
add_file "backend/app/api/v1/endpoints/instruments.py" "API V1: Endpoints de Instrumentos"
add_file "backend/app/api/v1/endpoints/inventory.py" "API V1: Endpoints de Inventario"
add_file "backend/app/api/v1/endpoints/repairs.py" "API V1: Endpoints de Reparaciones"
add_file "backend/app/api/v1/endpoints/stats.py" "API V1: Endpoints de Estadísticas"
add_file "backend/app/api/v1/endpoints/users.py" "API V1: Endpoints de Usuarios"

cat >> "$OUTPUT_FILE" << 'CRUD'

═══ CRUD OPERATIONS ═══

CRUD

add_file "backend/app/crud/base.py" "CRUD: Base"
add_file "backend/app/crud/user.py" "CRUD: Usuario"
add_file "backend/app/crud/appointment.py" "CRUD: Citas"
add_file "backend/app/crud/category.py" "CRUD: Categorías"
add_file "backend/app/crud/inventory.py" "CRUD: Inventario"
add_file "backend/app/crud/repair.py" "CRUD: Reparaciones"

cat >> "$OUTPUT_FILE" << 'SERVICES'

═══ SERVICIOS ═══

SERVICES

add_file "backend/app/services/ai_detector.py" "Servicio: Detector de IA"
add_file "backend/app/services/email_service.py" "Servicio: Email"
add_file "backend/app/services/event_handlers.py" "Servicio: Event Handlers"
add_file "backend/app/services/event_system.py" "Servicio: Sistema de Eventos"
add_file "backend/app/services/google_calendar_service.py" "Servicio: Google Calendar"
add_file "backend/app/services/image_analysis.py" "Servicio: Análisis de Imágenes"
add_file "backend/app/services/logging_service.py" "Servicio: Logging"
add_file "backend/app/services/pdf_generator.py" "Servicio: Generador de PDF"
add_file "backend/app/services/quote_calculator.py" "Servicio: Calculador de Cotizaciones"

# =============================================================================
# MÓDULOS DE CALCULADORAS
# =============================================================================
echo -e "\n${BLUE}[EXTRA]${NC} Módulos de Calculadoras Electrónicas"

cat >> "$OUTPUT_FILE" << 'CALC'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  MÓDULOS DE CALCULADORAS ELECTRÓNICAS - DOMAIN LOGIC                     ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

CALC

for module in awg length numberSystem ohmsLaw resistorColor smdCapacitor smdResistor temperature timer555; do
    add_file "src/domain/${module}/contract.ts" "Domain ${module}: Contrato"
    add_file "src/domain/${module}/model.ts" "Domain ${module}: Modelo"
    
    # Vista correspondiente
    MODULE_CAP="$(tr '[:lower:]' '[:upper:]' <<< ${module:0:1})${module:1}"
    add_file "src/modules/${module}/${MODULE_CAP}View.vue" "Vista: ${MODULE_CAP}"
done

# =============================================================================
# VALIDACIONES
# =============================================================================
echo -e "\n${BLUE}[EXTRA]${NC} Sistema de Validaciones"

cat >> "$OUTPUT_FILE" << 'VAL'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SISTEMA DE VALIDACIONES                                                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

VAL

add_file "src/validation/index.ts" "Validación: Index"
add_file "src/validation/numeric.ts" "Validación: Numérica"
add_file "src/validation/physical.ts" "Validación: Física"
add_file "src/validation/rules.ts" "Validación: Reglas"

# =============================================================================
# SERVICIOS FRONTEND
# =============================================================================
add_file "src/services/toastService.js" "Servicio Frontend: Toast Notifications"

# =============================================================================
# ESTILOS SCSS
# =============================================================================
echo -e "\n${BLUE}[EXTRA]${NC} Sistema de Estilos"

cat >> "$OUTPUT_FILE" << 'STYLES'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  SISTEMA DE ESTILOS SCSS                                                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

STYLES

add_file "src/scss/style.scss" "SCSS: Archivo Principal"
add_file "src/scss/_variables.scss" "SCSS: Variables"
add_file "src/scss/_brand.scss" "SCSS: Branding"
add_file "src/scss/_mixins.scss" "SCSS: Mixins"
add_file "src/scss/_theming.scss" "SCSS: Theming"

# =============================================================================
# FINALIZACIÓN Y ESTADÍSTICAS
# =============================================================================

cat >> "$OUTPUT_FILE" << 'FOOTER'

╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                    FIN DEL VOLCADO DE CÓDIGO                              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

FOOTER

# Estadísticas
FILE_
