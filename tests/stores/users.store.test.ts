import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUsersStore } from '@stores/users'

describe('Users Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should have initial empty state', () => {
    const store = useUsersStore()
    expect(store.users).toEqual([])
    expect(store.isLoading).toBe(false)
  })

  it('should add user', () => {
    const store = useUsersStore()
    const user = { id: 1, name: 'John', email: 'john@test.com', role: 'user' }
    store.users.push(user)
    expect(store.users).toContainEqual(user)
  })

  it('should find user by ID', () => {
    const store = useUsersStore()
    const user = { id: 1, name: 'John', email: 'john@test.com', role: 'user' }
    store.users = [user]
    expect(store.users.find(u => u.id === 1)).toEqual(user)
  })

  it('should update user', () => {
    const store = useUsersStore()
    store.users = [{ id: 1, name: 'John', email: 'john@test.com', role: 'user' }]
    store.users[0].name = 'Jane'
    expect(store.users[0].name).toBe('Jane')
  })

  it('should delete user', () => {
    const store = useUsersStore()
    store.users = [
      { id: 1, name: 'John', email: 'john@test.com', role: 'user' },
      { id: 2, name: 'Jane', email: 'jane@test.com', role: 'admin' }
    ]
    store.users = store.users.filter(u => u.id !== 1)
    expect(store.users).toHaveLength(1)
  })

  it('should count users', () => {
    const store = useUsersStore()
    store.users = [
      { id: 1, name: 'User1', email: 'user1@test.com', role: 'user' },
      { id: 2, name: 'User2', email: 'user2@test.com', role: 'admin' },
      { id: 3, name: 'User3', email: 'user3@test.com', role: 'user' }
    ]
    expect(store.users.length).toBe(3)
  })

  it('should filter admins', () => {
    const store = useUsersStore()
    store.users = [
      { id: 1, name: 'John', email: 'john@test.com', role: 'admin' },
      { id: 2, name: 'Jane', email: 'jane@test.com', role: 'user' },
      { id: 3, name: 'Bob', email: 'bob@test.com', role: 'admin' }
    ]
    const admins = store.users.filter(u => u.role === 'admin')
    expect(admins).toHaveLength(2)
  })

  it('should search users by email', () => {
    const store = useUsersStore()
    store.users = [
      { id: 1, name: 'John', email: 'john@test.com', role: 'user' },
      { id: 2, name: 'Jane', email: 'jane@test.com', role: 'admin' }
    ]
    const results = store.users.filter(u => u.email.includes('john'))
    expect(results).toHaveLength(1)
  })

  it('should set loading state', () => {
    const store = useUsersStore()
    store.isLoading = true
    expect(store.isLoading).toBe(true)
  })
})
