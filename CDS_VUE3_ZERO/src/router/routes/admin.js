const AdminShellLayout = () => import('@/layouts/AdminShellLayout.vue')
const AdminDashboard = () => import('@/pages/admin/AdminDashboard.vue')
const InventoryPage = () => import('@/pages/admin/InventoryPage.vue')
const InventoryUnified = () => import('@/pages/admin/InventoryUnifiedPage.vue')
const ClientsPage = () => import('@/pages/admin/ClientsPage.vue')
const RepairsAdminPage = () => import('@/pages/admin/RepairsAdminPage.vue')
const QuotesAdminPage = () => import('@/pages/admin/QuotesAdminPage.vue')
const CategoriesPage = () => import('@/pages/admin/CategoriesPage.vue')
const ContactMessagesPage = () => import('@/pages/admin/ContactMessagesPage.vue')
const NewsletterSubscriptionsPage = () => import('@/pages/admin/NewsletterSubscriptionsPage.vue')
const AppointmentsPage = () => import('@/pages/admin/AppointmentsPage.vue')
const RepairDetailAdminPage = () => import('@/pages/admin/RepairDetailAdminPage.vue')
const TicketsPage = () => import('@/pages/admin/TicketsPage.vue')
const PurchaseRequestsPage = () => import('@/pages/admin/PurchaseRequestsPage.vue')
const ManualsPage = () => import('@/pages/admin/ManualsPage.vue')
const StatsPage = () => import('@/pages/admin/StatsPage.vue')
const WizardsPage = () => import('@/pages/admin/WizardsPage.vue')
const IntakeWizardPage = () => import('@/pages/admin/IntakeWizardPage.vue')
const ArchivePage = () => import('@/pages/admin/ArchivePage.vue')
const MediaPage = () => import('@/pages/admin/MediaPage.vue')
const LeadsAdminPage = () => import('@/pages/admin/LeadsAdminPage.vue')
const MobileFotoFirmaPage = () => import('@/pages/admin/MobileFotoFirmaPage.vue')

export const adminRoutes = [
  {
    path: '/admin',
    component: AdminShellLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', name: 'admin-dashboard', component: AdminDashboard,
        meta: { title: 'Dashboard', subtitle: 'Panel de control administrativo' } },
      { path: 'inventory', name: 'admin-inventory', component: InventoryPage,
        meta: { title: 'Inventario', subtitle: 'Control de stock y materiales' } },
      { path: 'inventory/unified', name: 'admin-inventory-unified', component: InventoryUnified,
        meta: { title: 'Inventario Unificado' } },
      { path: 'clients', name: 'admin-clients', component: ClientsPage,
        meta: { title: 'Clientes', subtitle: 'Base de datos de clientes' } },
      { path: 'repairs', name: 'admin-repairs', component: RepairsAdminPage,
        meta: { title: 'Reparaciones', subtitle: 'Gestión de órdenes de trabajo' } },
      { path: 'quotes', name: 'admin-quotes', component: QuotesAdminPage,
        meta: { title: 'Cotizaciones', subtitle: 'Cotizaciones y presupuestos' } },
      { path: 'repairs/:id', name: 'admin-repair-detail', component: RepairDetailAdminPage,
        meta: { title: 'Detalle de Reparación' } },
      { path: 'categories', name: 'admin-categories', component: CategoriesPage,
        meta: { title: 'Categorías' } },
      { path: 'contact', name: 'admin-contact', component: ContactMessagesPage,
        meta: { title: 'Mensajes' } },
      { path: 'newsletter', name: 'admin-newsletter', component: NewsletterSubscriptionsPage,
        meta: { title: 'Newsletter' } },
      { path: 'appointments', name: 'admin-appointments', component: AppointmentsPage,
        meta: { title: 'Citas' } },
      { path: 'tickets', name: 'admin-tickets', component: TicketsPage,
        meta: { title: 'Tickets' } },
      { path: 'purchase-requests', name: 'admin-purchase-requests', component: PurchaseRequestsPage,
        meta: { title: 'Solicitudes de Compra' } },
      { path: 'manuals', name: 'admin-manuals', component: ManualsPage,
        meta: { title: 'Manuales' } },
      { path: 'stats', name: 'admin-stats', component: StatsPage,
        meta: { title: 'Estadísticas' } },
      { path: 'wizards', name: 'admin-wizards', component: WizardsPage,
        meta: { title: 'Magos' } },
      { path: 'intake', name: 'admin-intake', component: IntakeWizardPage,
        meta: { title: 'Nuevo Ingreso', subtitle: 'Ingreso unificado de equipos' } },
      { path: 'archive', name: 'admin-archive', component: ArchivePage,
        meta: { title: 'Archivo' } },
      { path: 'media', name: 'admin-media', component: MediaPage,
        meta: { title: 'Gestión de Medios' } },
      { path: 'leads', name: 'admin-leads', component: LeadsAdminPage,
        meta: { title: 'Prospectos', subtitle: 'Leads del cotizador público' } },
      { path: 'foto-firma', name: 'admin-foto-firma', component: MobileFotoFirmaPage,
        meta: { title: 'Foto / Firma', subtitle: 'Agregar fotos y firma a OT activa' } },
    ]
  }
]
