import { storeToRefs } from 'pinia'
import { useUsersStore } from '@/stores/users'
export function useUsers() {
  const store = useUsersStore()
  const { users, loading, error } = storeToRefs(store)
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
