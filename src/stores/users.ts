/**
 * Store Pinia - users.ts (TypeScript)
 * Gestiona el estado de usuarios con tipos completos (para administración)
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { UsersStoreState, User, CreateUserData, UpdateUserData } from '@/types/stores';
import { get, post, put, deleteRequest, handleApiError } from '@/services/api';

export const useUsersStore = defineStore('users', () => {
  // State
  const users = ref<User[]>([]);
  const currentUser = ref<User | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch all users
   */
  async function fetchUsers(): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get<User[]>('/users/');
      users.value = response.data.data || [];
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      users.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get single user by ID
   */
  async function getUser(id: string): Promise<void> {
    try {
      const response = await get<User>(`/users/${id}`);
      currentUser.value = response.data.data || null;
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      currentUser.value = null;
    }
  }

  /**
   * Create user
   */
  async function createUser(data: CreateUserData): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post<User>('/users/', data);
      if (response.data.data) {
        users.value.push(response.data.data);
      }
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update user
   */
  async function updateUser(id: string, data: UpdateUserData): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put<User>(`/users/${id}`, data);
      if (response.data.data) {
        const index = users.value.findIndex((u) => u.id === id);
        if (index !== -1) {
          users.value[index] = response.data.data;
        }
        if (currentUser.value?.id === id) {
          currentUser.value = response.data.data;
        }
      }
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Delete user
   */
  async function deleteUser(id: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      await deleteRequest(`/users/${id}`);
      users.value = users.value.filter((u) => u.id !== id);
      if (currentUser.value?.id === id) {
        currentUser.value = null;
      }
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Set user role
   */
  async function setUserRole(id: string, role: User['role']): Promise<void> {
    try {
      const response = await put<User>(`/users/${id}`, { role });
      if (response.data.data) {
        const index = users.value.findIndex((u) => u.id === id);
        if (index !== -1) {
          users.value[index] = response.data.data;
        }
        if (currentUser.value?.id === id) {
          currentUser.value = response.data.data;
        }
      }
    } catch (err: any) {
      const apiError = handleApiError(err);
      error.value = apiError.message;
      throw err;
    }
  }

  /**
   * Set error message
   */
  function setError(message: string): void {
    error.value = message;
  }

  return {
    // State
    users,
    currentUser,
    isLoading,
    error,
    // Actions
    fetchUsers,
    getUser,
    createUser,
    updateUser,
    deleteUser,
    setUserRole,
    setError,
  };
});
