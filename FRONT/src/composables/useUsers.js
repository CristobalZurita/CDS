import { useUsersStore } from '@/stores/users'
export function useUsers() {
  const store = useUsersStore()
  return {
    users: store.users,
    loading: store.loading,
    error: store.error,
    fetchUsers: store.fetchUsers,
    createUser: store.createUser,
    updateUser: store.updateUser,
    deleteUser: store.deleteUser
  }
}
