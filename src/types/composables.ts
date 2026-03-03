/**
 * Composables Types - Tipos para todos los composables
 */

import type { User } from './common';
import type { Repair, Invoice, Appointment, Quotation } from './api';

/**
 * useAuth - Auth management
 */
export interface UseAuthComposable {
  user: import('vue').Ref<User | null>;
  isLoading: import('vue').Ref<boolean>;
  error: import('vue').Ref<string | null>;
  requires2FA: import('vue').Ref<boolean>;
  twoFAChallengeId: import('vue').Ref<string | null>;
  isAuthenticated: import('vue').ComputedRef<boolean>;
  isAdmin: import('vue').ComputedRef<boolean>;
  isTechnician: import('vue').ComputedRef<boolean>;

  register(data: RegisterData): Promise<User | null>;
  login(email: string, password: string, turnstileToken?: string): Promise<LoginResponse>;
  verifyTwoFactor(code: string): Promise<User | null>;
  fetchUserInfo(): Promise<User | null>;
  refreshAccessToken(): Promise<boolean>;
  logout(): Promise<void>;
  requestPasswordReset(email: string): Promise<boolean>;
  confirmPasswordReset(token: string, newPassword: string): Promise<boolean>;
  deleteAccount(password: string): Promise<boolean>;
  hasPermission(permission: string): boolean;
  initialize(): Promise<void>;
}

export interface RegisterData {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  phone?: string;
}

export interface LoginResponse {
  user?: User;
  requires2FA?: boolean;
  challengeId?: string;
}

/**
 * useCalculator - Generic calculator for domain logic
 */
export interface UseCalculatorComposable<I, O> {
  result: import('vue').Ref<CalculationResult<O> | null>;
  calculate(input: I): void;
}

export interface CalculationResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * useValidation - Input validation
 */
export interface UseValidationComposable {
  validateEmail(email: string): ValidationError[];
  validatePassword(password: string): ValidationError[];
  validatePhone(phone: string): ValidationError[];
  validateUrl(url: string): ValidationError[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

/**
 * useRepairs - Repairs management
 */
export interface UseRepairsComposable {
  repairs: import('vue').Ref<Repair[]>;
  currentRepair?: import('vue').Ref<Record<string, any> | null>;
  currentRepairTimeline?: import('vue').Ref<Record<string, any>[]>;
  currentRepairPhotos?: import('vue').Ref<Record<string, any>[]>;
  currentRepairNotes?: import('vue').Ref<Record<string, any>[]>;
  isLoading: import('vue').Ref<boolean>;
  error: import('vue').Ref<string | null>;

  fetchRepairs(): Promise<Repair[]>;
  fetchClientRepairs?(): Promise<Repair[]>;
  getRepair(id: string): Promise<Repair>;
  fetchClientRepairDetail?(id: string): Promise<Record<string, any> | null>;
  downloadClientClosurePdf?(id: string): Promise<BlobPart>;
  clearCurrentRepairDetail?(): void;
  createRepair(data: CreateRepairData): Promise<Repair>;
  updateRepair(id: string, data: UpdateRepairData): Promise<Repair>;
  deleteRepair(id: string): Promise<boolean>;
  changeStatus(id: string, status: RepairStatus): Promise<Repair>;
}

export type CreateRepairData = Omit<Repair, 'id' | 'createdAt' | 'updatedAt'>;
export type UpdateRepairData = Partial<CreateRepairData>;
export type RepairStatus = 'pending' | 'in-progress' | 'completed' | 'on-hold' | 'cancelled';

/**
 * useInvoices - Invoices management
 */
export interface UseInvoicesComposable {
  invoices: import('vue').Ref<Invoice[]>;
  isLoading: import('vue').Ref<boolean>;
  error: import('vue').Ref<string | null>;

  fetchInvoices(): Promise<Invoice[]>;
  getInvoice(id: string): Promise<Invoice>;
  createInvoice(data: CreateInvoiceData): Promise<Invoice>;
  sendInvoice(id: string): Promise<boolean>;
  markViewed(id: string): Promise<boolean>;
  voidInvoice(id: string): Promise<boolean>;
}

export type CreateInvoiceData = Omit<Invoice, 'id' | 'createdAt' | 'paidAt'>;

/**
 * useAppointments - Appointments management
 */
export interface UseAppointmentsComposable {
  appointments: import('vue').Ref<Appointment[]>;
  isLoading: import('vue').Ref<boolean>;
  error: import('vue').Ref<string | null>;

  fetchAppointments(): Promise<Appointment[]>;
  getAppointment(id: string): Promise<Appointment>;
  createAppointment(data: CreateAppointmentData): Promise<Appointment>;
  confirmAppointment(id: string): Promise<boolean>;
  cancelAppointment(id: string): Promise<boolean>;
  getAvailableSlots(date: string): Promise<string[]>;
}

export type CreateAppointmentData = Omit<Appointment, 'id' | 'createdAt'>;

/**
 * useQuotations - Quotations management
 */
export interface UseQuotationsComposable {
  quotations: import('vue').Ref<Quotation[]>;
  isLoading: import('vue').Ref<boolean>;
  error: import('vue').Ref<string | null>;

  fetchQuotations(): Promise<Quotation[]>;
  getQuotation(id: string): Promise<Quotation>;
  createQuotation(diagnosticId: string): Promise<Quotation>;
  acceptQuotation(id: string): Promise<boolean>;
  rejectQuotation(id: string): Promise<boolean>;
}

/**
 * useInventory - Inventory management
 */
export interface UseInventoryComposable {
  items: import('vue').Ref<InventoryItem[]>;
  isLoading: import('vue').Ref<boolean>;
  error: import('vue').Ref<string | null>;
  catalogStatus?: import('vue').Ref<Record<string, any> | null>;
  syncingCatalog?: import('vue').Ref<boolean>;
  importing?: import('vue').Ref<boolean>;
  lastRunId?: import('vue').Ref<string | null>;
  runStatus?: import('vue').Ref<string | null>;

  fetchInventory(): Promise<InventoryItem[]>;
  getItem(id: string): Promise<InventoryItem>;
  updateStock(id: string, quantity: number): Promise<InventoryItem>;
  getLowStockItems(): Promise<InventoryItem[]>;
  fetchCatalogStatus?(): Promise<Record<string, any> | null>;
  fetchItemById?(id: string): Promise<Record<string, any> | null>;
  syncCatalog?(): Promise<Record<string, any> | null>;
  triggerImport?(): Promise<Record<string, any>>;
}

export interface InventoryItem {
  id: string;
  name: string;
  sku: string;
  quantity: number;
  minQuantity: number;
  unitPrice: number;
  category: string;
}
