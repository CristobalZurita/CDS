import { storeToRefs } from 'pinia'
import { useUsersStore } from '@/stores/users'
import type { Ref } from 'vue'

interface User {
  id: string
  email: string
  firstName?: string
  lastName?: string
  role?: string
  createdAt?: string
  updatedAt?: string
}

export interface UseUsersComposable {
  users: Ref<User[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchUsers: () => Promise<User[]>
  createUser: (data: any) => Promise<User>
  updateUser: (id: string, data: any) => Promise<User>
  deleteUser: (id: string) => Promise<boolean>
}

export function useUsers(): UseUsersComposable {
  const store = useUsersStore()
  const { users, error } = storeToRefs(store)
  const loading = 'loading' in store ? storeToRefs(store).loading : storeToRefs(store).isLoading

  return {
    users,
    loading,
    error,
    fetchUsers: store.fetchUsers,
    createUser: store.createUser,
    updateUser: store.updateUser,
    deleteUser: store.deleteUser
  }
}
