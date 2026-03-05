import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routeState = vi.hoisted(() => ({
  params: { id: '55' },
}))

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

const secureMediaMock = vi.hoisted(() => ({
  hydrateRepairPhotos: vi.fn(),
  revokeHydratedRepairPhotos: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/services/secureMedia', () => secureMediaMock)

import RepairDetailAdminPage from '@/vue/content/pages/admin/RepairDetailAdminPage.vue'

const baseRepair = {
  id: 55,
  repair_number: 'R-55',
  repair_code: 'OT-55',
  status_id: 2,
  priority: 1,
  client: {
    name: 'Cliente Test',
    client_code: 'CLI-055',
  },
  device: {
    model: 'Juno 106',
    serial_number: 'SN-55',
  },
  problem_reported: 'Ruido en salida',
  diagnosis: 'Capacitores en fuga',
  work_performed: 'Reemplazo completo',
  signature_ingreso_path: null,
  signature_retiro_path: null,
  archived_at: null,
}

const stubs = {
  AdminLayout: {
    props: ['title', 'subtitle', 'context'],
    template: `
      <section>
        <h1 data-testid="layout-title">{{ title }}</h1>
        <p data-testid="layout-subtitle">{{ subtitle }}</p>
        <div data-testid="layout-context">{{ context?.clientName || '' }}</div>
        <slot />
      </section>
    `,
  },
  RepairStatusChanger: {
    props: ['repairId', 'currentStatusId'],
    template: `
      <div data-testid="status-changer-stub">
        <span data-testid="status-current">{{ currentStatusId }}</span>
        <button data-testid="status-refresh" @click="$emit('status-changed', { newStatusId: 6 })">refresh</button>
        <button
          data-testid="status-inline"
          @click="$emit('status-changed', {
            newStatusId: 6,
            repair: {
              id: Number(repairId),
              repair_number: 'R-55',
              repair_code: 'OT-55-UPD',
              status_id: 6,
              priority: 2,
              client: { name: 'Cliente Test' },
              device: { model: 'Juno 106', serial_number: 'SN-55' },
              problem_reported: 'Ruido',
              diagnosis: 'Diagnóstico actualizado',
              work_performed: 'Trabajo actualizado'
            }
          })"
        >
          inline
        </button>
      </div>
    `,
  },
  RepairComponentsManager: {
    props: ['repairId', 'isReadOnly'],
    template: `
      <div data-testid="components-manager-stub">
        <span data-testid="components-read-only">{{ isReadOnly ? 'yes' : 'no' }}</span>
        <button data-testid="components-cost-event" @click="$emit('update:total-cost', 2300)">cost</button>
        <button data-testid="components-changed-event" @click="$emit('components-changed', [{ id: 1 }, { id: 2 }])">components</button>
      </div>
    `,
  },
  RepairCostSummary: {
    props: ['repairId', 'materialsCost', 'componentsCount', 'isReadOnly'],
    template: `
      <div data-testid="cost-summary-stub">
        <span data-testid="materials-cost">{{ materialsCost }}</span>
        <span data-testid="components-count">{{ componentsCount }}</span>
        <span data-testid="cost-read-only">{{ isReadOnly ? 'yes' : 'no' }}</span>
        <button data-testid="cost-summary-updated" @click="$emit('updated')">updated</button>
      </div>
    `,
  },
  RouterLink: {
    template: '<a><slot /></a>',
  },
}

describe('RepairDetailAdminPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    routeState.params = { id: '55' }

    let currentRepair = { ...baseRepair }
    let currentPhotos = [
      {
        id: 1,
        photo_url: '/uploads/initial.jpg',
        photo_type: 'before',
        caption: 'Inicial',
      },
    ]
    let currentNotes = [
      {
        id: 1,
        note: 'Nota inicial',
        note_type: 'internal',
        created_at: '2026-03-05T10:00:00Z',
      },
    ]

    secureMediaMock.hydrateRepairPhotos.mockImplementation(async (photos: any[]) =>
      photos.map((photo) => ({
        ...photo,
        resolved_photo_url: photo.photo_url || '/uploads/fallback.jpg',
      }))
    )

    apiMock.get.mockImplementation(async (url: string) => {
      if (url === '/repairs/55') return { data: currentRepair }
      if (url === '/repairs/55/photos') return { data: currentPhotos }
      if (url === '/repairs/55/notes') return { data: currentNotes }
      if (url === '/repairs/55/closure-pdf') return { data: new Uint8Array([1, 2, 3]) }
      if (url === '/repairs/') return { data: [currentRepair] }
      return { data: {} }
    })

    apiMock.post.mockImplementation(async (url: string, payload: any) => {
      if (url === '/signatures/requests') {
        return { data: { token: `sig-${payload.request_type}` } }
      }
      if (url === '/photo-requests/') {
        return { data: { token: 'photo-request-token' } }
      }
      if (url === '/uploads/images') {
        return { data: { path: '/uploads/new-photo.jpg' } }
      }
      if (url === '/repairs/55/photos') {
        currentPhotos = [
          ...currentPhotos,
          {
            id: 2,
            photo_url: payload.photo_url,
            photo_type: payload.photo_type,
            caption: payload.caption,
          },
        ]
        return { data: { ok: true } }
      }
      if (url === '/repairs/55/notes') {
        currentNotes = [
          ...currentNotes,
          {
            id: 2,
            note: payload.note,
            note_type: payload.note_type,
            created_at: '2026-03-05T10:05:00Z',
          },
        ]
        return { data: { ok: true } }
      }
      if (url === '/repairs/55/notify') {
        return { data: { ok: true } }
      }
      if (url === '/repairs/55/archive') {
        currentRepair = {
          ...currentRepair,
          archived_at: '2026-03-05T11:00:00Z',
        }
        return { data: { archived_at: '2026-03-05T11:00:00Z' } }
      }
      return { data: {} }
    })

    vi.spyOn(window, 'confirm').mockReturnValue(true)
    vi.spyOn(window, 'alert').mockImplementation(() => {})
  })

  it('loads repair detail and updates child-driven state', async () => {
    const wrapper = mount(RepairDetailAdminPage, {
      global: { stubs },
    })
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/repairs/55')
    expect(wrapper.text()).toContain('OT-55')
    expect(wrapper.get('[data-testid="layout-context"]').text()).toContain('Cliente Test')
    expect(wrapper.get('[data-testid="materials-cost"]').text()).toBe('0')
    expect(wrapper.get('[data-testid="components-count"]').text()).toBe('0')

    await wrapper.get('[data-testid="components-cost-event"]').trigger('click')
    await wrapper.get('[data-testid="components-changed-event"]').trigger('click')
    expect(wrapper.get('[data-testid="materials-cost"]').text()).toBe('2300')
    expect(wrapper.get('[data-testid="components-count"]').text()).toBe('2')

    const callCountBeforeRefresh = apiMock.get.mock.calls.length
    await wrapper.get('[data-testid="status-refresh"]').trigger('click')
    await flushPromises()
    expect(apiMock.get.mock.calls.length).toBeGreaterThan(callCountBeforeRefresh)

    await wrapper.get('[data-testid="status-inline"]').trigger('click')
    expect(wrapper.text()).toContain('OT-55-UPD')
  })

  it('requests signature and photo tokens with generated public links', async () => {
    const wrapper = mount(RepairDetailAdminPage, {
      global: { stubs },
    })
    await flushPromises()

    await wrapper.get('[data-testid="signature-request-ingreso"]').trigger('click')
    await flushPromises()
    expect(apiMock.post).toHaveBeenCalledWith('/signatures/requests', {
      repair_id: 55,
      request_type: 'ingreso',
      expires_minutes: 5,
    })
    expect((wrapper.get('[data-testid="signature-link"]').element as HTMLInputElement).value).toContain('/signature/sig-ingreso')

    await wrapper.get('[data-testid="signature-request-retiro"]').trigger('click')
    await flushPromises()
    expect(apiMock.post).toHaveBeenCalledWith('/signatures/requests', {
      repair_id: 55,
      request_type: 'retiro',
      expires_minutes: 5,
    })
    expect((wrapper.get('[data-testid="signature-link"]').element as HTMLInputElement).value).toContain('/signature/sig-retiro')

    await wrapper.get('[data-testid="photo-request"]').trigger('click')
    await flushPromises()
    expect(apiMock.post).toHaveBeenCalledWith('/photo-requests/', null, {
      params: { repair_id: 55, photo_type: 'client', expires_minutes: 10 },
    })
    expect((wrapper.get('[data-testid="photo-upload-link"]').element as HTMLInputElement).value).toContain('/photo-upload/photo-request-token')
  })

  it('adds notes and uploads photos from admin forms', async () => {
    const wrapper = mount(RepairDetailAdminPage, {
      global: { stubs },
    })
    await flushPromises()

    const addNoteButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Agregar Nota'))
    expect(addNoteButton).toBeTruthy()
    await addNoteButton!.trigger('click')

    await wrapper.find('.note-form textarea').setValue('  Nueva nota técnica  ')
    await wrapper.find('.note-form select').setValue('technical')
    await wrapper.find('.note-form .btn-success').trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith('/repairs/55/notes', {
      note: 'Nueva nota técnica',
      note_type: 'technical',
    })
    expect(wrapper.text()).toContain('Nueva nota técnica')

    const addPhotoButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Agregar Foto'))
    expect(addPhotoButton).toBeTruthy()
    await addPhotoButton!.trigger('click')

    const imageFile = new File(['file-binary'], 'damage.png', { type: 'image/png' })
    const fileInput = wrapper.find('.upload-form input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [imageFile],
      configurable: true,
    })
    await fileInput.trigger('change')
    await wrapper.find('.upload-form input[placeholder="Ej: Daño en circuito"]').setValue('Daño en IC')
    await wrapper.find('.upload-form select').setValue('damage')
    await wrapper.find('.upload-form .btn-success').trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith(
      '/uploads/images',
      expect.any(FormData),
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    expect(apiMock.post).toHaveBeenCalledWith('/repairs/55/photos', {
      photo_url: '/uploads/new-photo.jpg',
      photo_type: 'damage',
      caption: 'Daño en IC',
    })
    expect(wrapper.text()).toContain('Daño en IC')
  })

  it('notifies, archives, downloads closure PDF and revokes hydrated media on unmount', async () => {
    const createObjectURLSpy = vi.fn(() => 'blob:closure-pdf')
    const revokeObjectURLSpy = vi.fn()
    Object.defineProperty(window.URL, 'createObjectURL', {
      value: createObjectURLSpy,
      configurable: true,
    })
    Object.defineProperty(window.URL, 'revokeObjectURL', {
      value: revokeObjectURLSpy,
      configurable: true,
    })
    const originalCreateElement = document.createElement.bind(document)
    const linkClickSpy = vi.fn()
    vi.spyOn(document, 'createElement').mockImplementation(((tagName: any) => {
      const element = originalCreateElement(tagName) as any
      if (String(tagName).toLowerCase() === 'a') {
        element.click = linkClickSpy
      }
      return element
    }) as any)

    const wrapper = mount(RepairDetailAdminPage, {
      global: { stubs },
    })
    await flushPromises()

    const notifyButton = wrapper.findAll('button').find((button) => button.text().includes('Enviar al cliente'))
    expect(notifyButton).toBeTruthy()
    await notifyButton!.trigger('click')
    await flushPromises()
    expect(apiMock.post).toHaveBeenCalledWith('/repairs/55/notify')
    expect(window.alert).toHaveBeenCalledWith('Enviado al cliente.')

    const archiveButton = wrapper.findAll('button').find((button) => button.text().includes('Archivar OT'))
    expect(archiveButton).toBeTruthy()
    await archiveButton!.trigger('click')
    await flushPromises()
    expect(apiMock.post).toHaveBeenCalledWith('/repairs/55/archive')
    expect(wrapper.text()).toContain('Archivado')

    const downloadButton = wrapper.findAll('button').find((button) => button.text().includes('Descargar Cierre OT'))
    expect(downloadButton).toBeTruthy()
    await downloadButton!.trigger('click')
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/repairs/55/closure-pdf', {
      responseType: 'blob',
    })
    expect(createObjectURLSpy).toHaveBeenCalled()
    expect(linkClickSpy).toHaveBeenCalled()
    expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:closure-pdf')

    wrapper.unmount()
    expect(secureMediaMock.revokeHydratedRepairPhotos).toHaveBeenCalled()
  })

  it('falls back to /repairs/ list when direct endpoint fails', async () => {
    apiMock.get.mockImplementation(async (url: string) => {
      if (url === '/repairs/55') throw new Error('not found')
      if (url === '/repairs/55/photos') return { data: [] }
      if (url === '/repairs/55/notes') return { data: [] }
      if (url === '/repairs/') {
        return {
          data: [
            {
              ...baseRepair,
              repair_code: 'OT-LIST-55',
            },
          ],
        }
      }
      return { data: {} }
    })

    const wrapper = mount(RepairDetailAdminPage, {
      global: { stubs },
    })
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/repairs/')
    expect(wrapper.text()).toContain('OT-LIST-55')
  })
})
