/**
 * Stores Types - Tipos para todos los Pinia stores
 */

import type { User } from './common';
import type {
  Repair,
  Invoice,
  Appointment,
  Quotation,
  QuotationItem,
} from './api';

/**
 * Auth Store State
 */
export interface AuthStoreState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  requires2FA: boolean;
  twoFAChallengeId: string | null;
}

export interface AuthStoreActions {
  login(email: string, password: string, turnstileToken?: string): Promise<{ requires_2fa?: boolean; challenge_id?: string | null }>;
  register(data: Record<string, any>): Promise<void>;
  logout(): Promise<void>;
  fetchUserInfo(): Promise<void>;
  checkAuth(): Promise<void>;
  verify2FA(code: string): Promise<void>;
  verifyTwoFactor(challengeId: string | null, code: string): Promise<void>;
  setError(error: string): void;
}

export interface RegisterFormData {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  phone?: string;
}

/**
 * Repairs Store State
 */
export interface RepairsStoreState {
  repairs: Repair[];
  currentRepair: Repair | null;
  currentRepairTimeline?: Record<string, any>[];
  currentRepairPhotos?: Record<string, any>[];
  currentRepairNotes?: Record<string, any>[];
  isLoading: boolean;
  error: string | null;
  filters: RepairFilters;
}

export interface RepairFilters {
  status?: Repair['status'];
  clientId?: string;
  dateFrom?: string;
  dateTo?: string;
}

export interface RepairsStoreActions {
  fetchRepairs(filters?: RepairFilters): Promise<void>;
  fetchClientRepairs?(): Promise<Repair[]>;
  getRepair(id: string): Promise<void>;
  fetchClientRepairDetail?(id: string): Promise<Record<string, any> | null>;
  downloadClientClosurePdf?(id: string): Promise<BlobPart>;
  clearCurrentRepairDetail?(): void;
  createRepair(data: CreateRepairData): Promise<void>;
  updateRepair(id: string, data: UpdateRepairData): Promise<void>;
  deleteRepair(id: string): Promise<void>;
  changeStatus(id: string, status: Repair['status']): Promise<void>;
  setError(error: string): void;
  clearRepairs(): void;
}

export type CreateRepairData = Omit<Repair, 'id' | 'createdAt' | 'updatedAt'>;
export type UpdateRepairData = Partial<CreateRepairData>;

/**
 * Invoices Store State
 */
export interface InvoicesStoreState {
  invoices: Invoice[];
  currentInvoice: Invoice | null;
  isLoading: boolean;
  error: string | null;
  filters: InvoiceFilters;
}

export interface InvoiceFilters {
  status?: Invoice['status'];
  clientId?: string;
  dueDateFrom?: string;
  dueDateTo?: string;
}

export interface InvoicesStoreActions {
  fetchInvoices(filters?: InvoiceFilters): Promise<void>;
  getInvoice(id: string): Promise<void>;
  createInvoice(data: CreateInvoiceData): Promise<void>;
  sendInvoice(id: string): Promise<void>;
  markViewed(id: string): Promise<void>;
  voidInvoice(id: string, reason: string): Promise<void>;
  recordPayment(id: string, amount: number): Promise<void>;
  getOverdueInvoices(): Promise<Invoice[]>;
  setError(error: string): void;
}

export type CreateInvoiceData = Omit<Invoice, 'id' | 'createdAt' | 'paidAt'>;

/**
 * Appointments Store State
 */
export interface AppointmentsStoreState {
  appointments: Appointment[];
  currentAppointment: Appointment | null;
  isLoading: boolean;
  error: string | null;
  availableSlots: string[];
}

export interface AppointmentsStoreActions {
  fetchAppointments(): Promise<void>;
  getAppointment(id: string): Promise<void>;
  createAppointment(data: CreateAppointmentData): Promise<void>;
  confirmAppointment(id: string): Promise<void>;
  cancelAppointment(id: string): Promise<void>;
  getAvailableSlots(date: string): Promise<void>;
  setError(error: string): void;
}

export type CreateAppointmentData = Omit<Appointment, 'id' | 'createdAt'>;

/**
 * Quotations Store State
 */
export interface QuotationsStoreState {
  quotations: Quotation[];
  currentQuotation: Quotation | null;
  isLoading: boolean;
  error: string | null;
  items: QuotationItem[];
}

export interface QuotationsStoreActions {
  fetchQuotations(): Promise<void>;
  getQuotation(id: string): Promise<void>;
  createQuotation(diagnosticId: string): Promise<void>;
  addItem(item: QuotationItem): void;
  removeItem(itemId: string): void;
  updateItem(itemId: string, updates: Partial<QuotationItem>): void;
  acceptQuotation(id: string): Promise<void>;
  rejectQuotation(id: string): Promise<void>;
  calculateTotal(): number;
  setError(error: string): void;
}

/**
 * Inventory Store State
 */
export interface InventoryStoreState {
  items: InventoryItem[];
  isLoading: boolean;
  error: string | null;
  searchQuery: string;
  page?: number;
  limit?: number;
  catalogStatus?: Record<string, any> | null;
  syncingCatalog?: boolean;
  importing?: boolean;
  lastRunId?: string | null;
  runStatus?: string | null;
}

export interface InventoryItem {
  id: string;
  name: string;
  sku: string;
  quantity: number;
  minQuantity: number;
  unitPrice: number;
  category: string;
  supplier?: string;
  lastUpdated: string;
}

export interface InventoryStoreActions {
  fetchInventory(): Promise<void>;
  fetchItems?(page?: number, limit?: number, search?: string | null, categoryId?: string | null): Promise<InventoryItem[]>;
  searchItems(query: string): Promise<void>;
  updateStock(id: string, quantity: number): Promise<void>;
  getLowStockItems(): Promise<InventoryItem[]>;
  addItem(data: CreateInventoryItemData): Promise<void>;
  updateItem(id: string, data: UpdateInventoryItemData): Promise<void>;
  deleteItem(id: string): Promise<void>;
  fetchCatalogStatus?(): Promise<Record<string, any> | null>;
  fetchItemById?(id: string): Promise<Record<string, any> | null>;
  syncCatalog?(): Promise<Record<string, any> | null>;
  triggerImport?(): Promise<Record<string, any>>;
  setError(error: string): void;
}

export type CreateInventoryItemData = Omit<InventoryItem, 'id' | 'lastUpdated'>;
export type UpdateInventoryItemData = Partial<CreateInventoryItemData>;

/**
 * Categories Store State
 */
export interface CategoriesStoreState {
  categories: Category[];
  isLoading: boolean;
  error: string | null;
}

export interface Category {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
}

export interface CategoriesStoreActions {
  fetchCategories(): Promise<void>;
  getCategory(id: string): Promise<Category>;
  createCategory(data: CreateCategoryData): Promise<void>;
  updateCategory(id: string, data: UpdateCategoryData): Promise<void>;
  deleteCategory(id: string): Promise<void>;
}

export type CreateCategoryData = Omit<Category, 'id'>;
export type UpdateCategoryData = Partial<CreateCategoryData>;

/**
 * Users Store State - Para admin
 */
export interface UsersStoreState {
  users: User[];
  currentUser: User | null;
  isLoading: boolean;
  error: string | null;
}

export interface UsersStoreActions {
  fetchUsers(): Promise<void>;
  getUser(id: string): Promise<void>;
  createUser(data: CreateUserData): Promise<void>;
  updateUser(id: string, data: UpdateUserData): Promise<void>;
  deleteUser(id: string): Promise<void>;
  setUserRole(id: string, role: User['role']): Promise<void>;
}

export type CreateUserData = Omit<User, 'id' | 'createdAt' | 'updatedAt'>;
export type UpdateUserData = Partial<CreateUserData>;
