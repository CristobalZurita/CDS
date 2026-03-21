<template>
  <main v-if="isAdmin" class="redirect-notice">
    <p>Redirigiendo al panel de administración...</p>
  </main>

  <main v-else class="neo-dash-page">
    <p v-if="loadingError" class="neo-dash-error">{{ loadingError }}</p>

    <NeoDashShell>
      <template #top>
        <NeoDashTopShell
          :user-first-name="userFirstName"
          :active-section-meta="activeSectionMeta"
          :pending-repairs="pendingRepairs"
          :active-repairs="activeRepairs"
          :pending-ot-payments="pendingOtPayments"
          :notifications-count="notifications.length"
          :cart-items-count="cartItemsCount"
          :is-refreshing="isRefreshing"
          @open-sections="openSectionSheet"
          @refresh="refreshDashboard"
          @logout="handleLogout"
        />
      </template>

      <template #nav>
        <NeoDashSectionNav
          :sections="sections"
          :active-section="activeSection"
          @select="setActiveSection"
        />
      </template>

      <NeoDashOverviewSection
        v-if="activeSection === 'overview'"
        :pending-repairs="pendingRepairs"
        :active-repairs="activeRepairs"
        :completed-repairs="completedRepairs"
        :total-spent="totalSpent"
        :pending-ot-payments="pendingOtPayments"
        :cart-items-count="cartItemsCount"
        :pending-store-requests="pendingStoreRequests"
        :active-repairs-list="activeRepairsList"
        :notifications="notifications"
        :get-status-label="getStatusLabel"
        :get-status-class="getStatusClass"
        :format-date="formatDate"
        :format-time="formatTime"
        :get-notification-icon="getNotificationIcon"
        @select-section="setActiveSection"
      />

      <NeoDashRepairsSection
        v-else-if="activeSection === 'repairs'"
        :selected-status="selectedRepairStatus"
        :repairs="repairsRows"
        :is-loading="repairsLoading"
        :loading-error="repairsLoadingError"
        :get-status-label="getRepairsStatusLabel"
        :format-date="formatRepairsDate"
        :format-price="formatRepairsPrice"
        :should-show-progress="shouldShowProgress"
        :view-repair="viewRepair"
        @update:selected-status="updateRepairFilter"
      />

      <NeoDashPaymentsSection
        v-else-if="activeSection === 'payments'"
        :requests="paymentRequests"
        :loading="paymentsLoading"
        :error="paymentsError"
        :active-filter="activePaymentsFilter"
        :format-currency="formatPaymentsCurrency"
        :format-date="formatPaymentsDate"
        :to-api-path="toApiPath"
        :normalize-status="normalizePaymentStatus"
        @update:active-filter="setActivePaymentsFilter"
      />

      <NeoDashPurchasesSection
        v-else-if="activeSection === 'purchases'"
        :active-filter="activePurchaseFilter"
        :cart-items="cartItems"
        :totals="cartTotals"
        :current-shipping="currentShipping"
        :store-requests="storeRequests"
        :format-currency="formatPaymentsCurrency"
        :format-date="formatPaymentsDate"
        :normalize-status="normalizePaymentStatus"
        @update:active-filter="setActivePurchaseFilter"
      />

      <NeoDashNotificationsSection
        v-else-if="activeSection === 'notifications'"
        :notifications="notifications"
        :get-notification-icon="getNotificationIcon"
        :format-time="formatTime"
        :dismiss-notification="dismissNotification"
        @select-section="setActiveSection"
      />

      <NeoDashProfileSection
        v-else-if="activeSection === 'profile'"
        :user="profileUser"
        :preferences="profilePreferences"
        :user-initials="userInitials"
        :member-since="memberSince"
        :total-repairs="profileTotalRepairs"
        :total-spent="profileTotalSpent"
        :avg-repair-days="avgRepairDays"
      />

      <NeoDashScheduleBridge
        v-else-if="activeSection === 'schedule'"
      />
    </NeoDashShell>

    <NeoDashSectionSheet
      :open="sectionSheetOpen"
      :sections="sections"
      :active-section="activeSection"
      @close="closeSectionSheet"
      @select="setActiveSection"
    />
  </main>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDashboardPage } from '@/composables/useDashboardPage'
import { useOtPaymentsPage } from '@/composables/useOtPaymentsPage'
import { useRepairsPage } from '@/composables/useRepairsPage'
import { useProfilePage } from '@/composables/useProfilePage'
import { useNeoDashboardState } from '@/composables/useNeoDashboardState'
import { useShopCartStore } from '@/stores/shopCart'
import NeoDashShell from '@/components/client/dashboard/NeoDashShell.vue'
import NeoDashTopShell from '@/components/client/dashboard/NeoDashTopShell.vue'
import NeoDashSectionNav from '@/components/client/dashboard/NeoDashSectionNav.vue'
import NeoDashOverviewSection from '@/components/client/dashboard/NeoDashOverviewSection.vue'
import NeoDashRepairsSection from '@/components/client/dashboard/NeoDashRepairsSection.vue'
import NeoDashPaymentsSection from '@/components/client/dashboard/NeoDashPaymentsSection.vue'
import NeoDashPurchasesSection from '@/components/client/dashboard/NeoDashPurchasesSection.vue'
import NeoDashNotificationsSection from '@/components/client/dashboard/NeoDashNotificationsSection.vue'
import NeoDashProfileSection from '@/components/client/dashboard/NeoDashProfileSection.vue'
import NeoDashScheduleBridge from '@/components/client/dashboard/NeoDashScheduleBridge.vue'
import NeoDashSectionSheet from '@/components/client/dashboard/NeoDashSectionSheet.vue'

const authStore = useAuthStore()
const router = useRouter()
const shopCart = useShopCartStore()
const isAdmin = computed(() => authStore.isAdmin)

const {
  sections,
  activeSection,
  activeSectionMeta,
  activeRepairFilter,
  activePaymentsFilter,
  activePurchaseFilter,
  sectionSheetOpen,
  setActiveSection,
  setActiveRepairFilter,
  setActivePaymentsFilter,
  setActivePurchaseFilter,
  openSectionSheet,
  closeSectionSheet,
} = useNeoDashboardState()

const {
  isLoading,
  loadingError,
  userFirstName,
  pendingRepairs,
  activeRepairs,
  completedRepairs,
  totalSpent,
  pendingOtPayments,
  activeRepairsList,
  notifications,
  getStatusLabel,
  getStatusClass,
  formatDate,
  formatTime,
  getNotificationIcon,
  dismissNotification,
  viewRepair,
  handleLogout,
  loadDashboard,
} = useDashboardPage()

const {
  requests,
  loading: paymentsLoading,
  error: paymentsError,
  formatCurrency: formatPaymentsCurrency,
  formatDate: formatPaymentsDate,
  toApiPath,
  loadRequests,
} = useOtPaymentsPage()

const {
  selectedStatus,
  filteredRepairs,
  isLoading: repairsLoading,
  loadingError: repairsLoadingError,
  getStatusLabel: getRepairsStatusLabel,
  formatDate: formatRepairsDate,
  formatPrice: formatRepairsPrice,
  shouldShowProgress,
  loadRepairs,
} = useRepairsPage()

const {
  user: profileUser,
  preferences: profilePreferences,
  userInitials,
  memberSince,
  totalRepairs: profileTotalRepairs,
  totalSpent: profileTotalSpent,
  avgRepairDays,
} = useProfilePage()

const cartItems = computed(() => shopCart.items)
const cartItemsCount = computed(() => shopCart.itemsCount)
const cartTotals = computed(() => shopCart.totals)
const currentShipping = computed(() => shopCart.currentShipping)
const isRefreshing = computed(() => isLoading.value || paymentsLoading.value || repairsLoading.value)

const selectedRepairStatus = computed(() => selectedStatus.value)

function normalizePaymentStatus(value) {
  return String(value || '').trim().toLowerCase()
}

const paymentRequests = computed(() => {
  const rows = Array.isArray(requests.value) ? requests.value : []
  if (activePaymentsFilter.value === 'all') return rows

  if (activePaymentsFilter.value === 'history') {
    return rows.filter((entry) => !['requested', 'pending_payment', 'proof_submitted'].includes(normalizePaymentStatus(entry.status)))
  }

  return rows.filter((entry) => ['requested', 'pending_payment', 'proof_submitted'].includes(normalizePaymentStatus(entry.status)))
})

const storeRequests = computed(() => {
  const rows = Array.isArray(requests.value) ? requests.value : []
  const next = rows.filter((entry) => !(entry?.repair_code || entry?.repair_number))
  if (activePurchaseFilter.value === 'requests') return next
  return next
})

const pendingStoreRequests = computed(() => {
  return storeRequests.value.filter((entry) => ['requested', 'pending_payment', 'proof_submitted'].includes(normalizePaymentStatus(entry.status))).length
})

const repairsRows = computed(() => filteredRepairs.value)

async function refreshDashboard() {
  shopCart.hydrate()
  await Promise.all([
    loadDashboard(),
    loadRequests(),
    loadRepairs(),
  ])
}

function updateRepairFilter(nextFilter) {
  setActiveRepairFilter(nextFilter)
  selectedStatus.value = String(nextFilter || '')
}

watch(activeRepairFilter, (nextFilter) => {
  if (selectedStatus.value !== nextFilter) {
    selectedStatus.value = String(nextFilter || '')
  }
}, { immediate: true })

onMounted(() => {
  if (isAdmin.value) {
    router.replace('/admin')
    return
  }
  shopCart.hydrate()
})
</script>

<style scoped>
.redirect-notice {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--cds-background-color);
  color: var(--cds-text-normal);
}

.redirect-notice p {
  margin: 0;
  font-size: var(--cds-text-xl);
}
</style>
