import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCategoriesStore } from '@stores/categories'

describe('Categories Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should have initial empty state', () => {
    const store = useCategoriesStore()
    expect(store.categories).toEqual([])
  })

  it('should add category', () => {
    const store = useCategoriesStore()
    const cat = { id: 1, name: 'Electronics', description: 'Electronic components' }
    store.categories.push(cat)
    expect(store.categories).toContainEqual(cat)
  })

  it('should find category by ID', () => {
    const store = useCategoriesStore()
    const cat = { id: 1, name: 'Electronics', description: 'Electronic components' }
    store.categories = [cat]
    expect(store.categories.find(c => c.id === 1)).toEqual(cat)
  })

  it('should update category', () => {
    const store = useCategoriesStore()
    store.categories = [{ id: 1, name: 'Electronics', description: 'Old' }]
    store.categories[0].name = 'Updated'
    expect(store.categories[0].name).toBe('Updated')
  })

  it('should delete category', () => {
    const store = useCategoriesStore()
    store.categories = [
      { id: 1, name: 'Cat1', description: 'Desc1' },
      { id: 2, name: 'Cat2', description: 'Desc2' }
    ]
    store.categories = store.categories.filter(c => c.id !== 1)
    expect(store.categories).toHaveLength(1)
  })

  it('should count categories', () => {
    const store = useCategoriesStore()
    store.categories = [
      { id: 1, name: 'Cat1', description: 'Desc1' },
      { id: 2, name: 'Cat2', description: 'Desc2' },
      { id: 3, name: 'Cat3', description: 'Desc3' }
    ]
    expect(store.categories.length).toBe(3)
  })

  it('should search categories by name', () => {
    const store = useCategoriesStore()
    store.categories = [
      { id: 1, name: 'Electronics', description: 'Desc' },
      { id: 2, name: 'Mechanical', description: 'Desc' }
    ]
    const results = store.categories.filter(c => c.name.includes('Elec'))
    expect(results).toHaveLength(1)
  })
})
