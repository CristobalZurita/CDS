const MasterLayout = () => import('@new/layouts/MasterLayout.vue')
const AdminDashboard = () => import('@new/pages/admin/AdminDashboard.vue')
const InventoryPage = () => import('@new/pages/admin/InventoryPage.vue')
const InventoryUnified = () => import('@new/pages/admin/InventoryUnifiedPage.vue')
const ClientsPage = () => import('@new/pages/admin/ClientsPage.vue')
const RepairsAdminPage = () => import('@new/pages/admin/RepairsAdminPage.vue')
const QuotesAdminPage = () => import('@new/pages/admin/QuotesAdminPage.vue')
const CategoriesPage = () => import('@new/pages/admin/CategoriesPage.vue')
const ContactMessagesPage = () => import('@new/pages/admin/ContactMessagesPage.vue')
const NewsletterSubscriptionsPage = () => import('@new/pages/admin/NewsletterSubscriptionsPage.vue')
const AppointmentsPage = () => import('@new/pages/admin/AppointmentsPage.vue')
const RepairDetailAdminPage = () => import('@new/pages/admin/RepairDetailAdminPage.vue')
const TicketsPage = () => import('@new/pages/admin/TicketsPage.vue')
const PurchaseRequestsPage = () => import('@new/pages/admin/PurchaseRequestsPage.vue')
const ManualsPage = () => import('@new/pages/admin/ManualsPage.vue')
const StatsPage = () => import('@new/pages/admin/StatsPage.vue')
const WizardsPage = () => import('@new/pages/admin/WizardsPage.vue')
const ArchivePage = () => import('@new/pages/admin/ArchivePage.vue')

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
      { path: 'archive', name: 'admin-archive', component: ArchivePage }
    ]
  }
]
