const MasterLayout = () => import('@/layouts/MasterLayout.vue')
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

export const adminRoutes = [
  {
    path: '/admin',
    component: MasterLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', name: 'admin-dashboard', component: AdminDashboard },
      { path: 'inventory', name: 'admin-inventory', component: InventoryPage },
      { path: 'inventory/unified', name: 'admin-inventory-unified', component: InventoryUnified },
      { path: 'clients', name: 'admin-clients', component: ClientsPage },
      { path: 'repairs', name: 'admin-repairs', component: RepairsAdminPage },
      { path: 'quotes', name: 'admin-quotes', component: QuotesAdminPage },
      { path: 'repairs/:id', name: 'admin-repair-detail', component: RepairDetailAdminPage },
      { path: 'categories', name: 'admin-categories', component: CategoriesPage },
      { path: 'contact', name: 'admin-contact', component: ContactMessagesPage },
      { path: 'newsletter', name: 'admin-newsletter', component: NewsletterSubscriptionsPage },
      { path: 'appointments', name: 'admin-appointments', component: AppointmentsPage },
      { path: 'tickets', name: 'admin-tickets', component: TicketsPage },
      { path: 'purchase-requests', name: 'admin-purchase-requests', component: PurchaseRequestsPage },
      { path: 'manuals', name: 'admin-manuals', component: ManualsPage },
      { path: 'stats', name: 'admin-stats', component: StatsPage },
      { path: 'wizards', name: 'admin-wizards', component: WizardsPage },
      { path: 'intake', name: 'admin-intake', component: IntakeWizardPage },
      { path: 'archive', name: 'admin-archive', component: ArchivePage }
    ]
  }
]
