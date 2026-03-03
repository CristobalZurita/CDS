import { storeToRefs } from 'pinia'
import { useUsersStore } from '@/stores/users'
export function useUsers() {
  const store = useUsersStore()
  const refs = storeToRefs(store)
  const users = refs.users
  const loading = refs.loading || refs.isLoading
  const error = refs.error
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
