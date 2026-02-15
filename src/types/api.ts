/**
 * API Response Types - Tipos de respuestas de endpoints
 */

import type { ApiResponse, User, AuthToken } from './common';

export interface AuthApiResponse {
  login: ApiResponse<{
    user: User;
    token: AuthToken;
  }>;
  register: ApiResponse<{
    user: User;
    message: string;
  }>;
  logout: ApiResponse<{ message: string }>;
  refreshToken: ApiResponse<AuthToken>;
}

export interface DiagnosticApiResponse {
  brands: ApiResponse<Array<{ id: string; name: string }>>;
  models: ApiResponse<Array<{ id: string; name: string; brandId: string }>>;
  faults: ApiResponse<Array<{ id: string; name: string; description: string }>>;
  calculate: ApiResponse<{
    diagnosticId: string;
    recommendation: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    estimatedCost: number;
  }>;
}

export interface RepairApiResponse {
  list: ApiResponse<Repair[]>;
  create: ApiResponse<Repair>;
  update: ApiResponse<Repair>;
  delete: ApiResponse<{ message: string }>;
  changeStatus: ApiResponse<Repair>;
}

export interface Repair {
  id: string;
  clientId: string;
  diagnosticId: string;
  status: 'pending' | 'in-progress' | 'completed' | 'on-hold' | 'cancelled';
  description: string;
  estimatedCost: number;
  actualCost?: number;
  createdAt: string;
  updatedAt: string;
}

export interface Invoice {
  id: string;
  invoiceNumber: string;
  repairId: string;
  clientId: string;
  amount: number;
  tax: number;
  total: number;
  status: 'draft' | 'sent' | 'viewed' | 'paid' | 'overdue' | 'void';
  dueDate: string;
  createdAt: string;
  paidAt?: string;
}

export interface Appointment {
  id: string;
  clientId: string;
  date: string;
  time: string;
  type: 'diagnostic' | 'repair-followup' | 'consultation';
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
  createdAt: string;
}

export interface Quotation {
  id: string;
  diagnosticId: string;
  clientId: string;
  items: QuotationItem[];
  subtotal: number;
  tax: number;
  total: number;
  validUntil: string;
  status: 'pending' | 'accepted' | 'rejected' | 'expired';
  createdAt: string;
}

export interface QuotationItem {
  id: string;
  description: string;
  quantity: number;
  unitPrice: number;
  total: number;
}
