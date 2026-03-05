import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const instrumentsComposableMock = vi.hoisted(() => ({
  createInstrument: vi.fn(),
}))

const diagnosticsComposableMock = vi.hoisted(() => ({
  diagnostics: [] as Array<{ id: number; repair_id: number; quote_total: number }>,
  fetchDiagnostics: vi.fn(),
  deleteDiagnostic: vi.fn(),
}))

const apiMock = vi.hoisted(() => ({
  post: vi.fn(),
}))

vi.mock('@/composables/useInstruments', () => ({
  useInstruments: () => instrumentsComposableMock,
}))

vi.mock('@/composables/useDiagnostics', () => ({
  useDiagnostics: () => diagnosticsComposableMock,
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import InstrumentForm from '@/vue/components/admin/InstrumentForm.vue'
import IntakeForm from '@/vue/components/admin/IntakeForm.vue'
import DiagnosticsList from '@/vue/components/admin/DiagnosticsList.vue'
import RepairManager from '@/vue/components/admin/RepairManager.vue'
import RepairStatusEditor from '@/vue/components/admin/RepairStatusEditor.vue'

describe('admin repair base components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    diagnosticsComposableMock.diagnostics = [
      { id: 1, repair_id: 101, quote_total: 120000 },
      { id: 2, repair_id: 102, quote_total: 98000 },
    ]
    diagnosticsComposableMock.fetchDiagnostics.mockResolvedValue(diagnosticsComposableMock.diagnostics)
    diagnosticsComposableMock.deleteDiagnostic.mockResolvedValue(true)
    vi.spyOn(window, 'alert').mockImplementation(() => {})
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('submits InstrumentForm with current form payload', async () => {
    const wrapper = mount(InstrumentForm)

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('MS-20')
    await inputs[1].setValue('12')
    await inputs[2].setValue('Korg')
    await inputs[3].setValue('Sintetizador')
    await wrapper.find('form').trigger('submit')

    expect(instrumentsComposableMock.createInstrument).toHaveBeenCalledWith({
      name: 'MS-20',
      brand_id: '12',
      model: 'Korg',
      type: 'Sintetizador',
    })
  })

  it('loads diagnostics list and triggers fetch/delete actions', async () => {
    const wrapper = mount(DiagnosticsList)

    expect(wrapper.text()).toContain('Diagnósticos')
    expect(wrapper.text()).toContain('101')
    expect(wrapper.text()).toContain('102')

    const actionButtons = wrapper.findAll('button')
    await actionButtons[0].trigger('click')
    expect(diagnosticsComposableMock.fetchDiagnostics).toHaveBeenCalled()

    const deleteButtons = wrapper.findAll('tbody button')
    await deleteButtons[1].trigger('click')
    expect(diagnosticsComposableMock.deleteDiagnostic).toHaveBeenCalledWith(1)
  })

  it('emits status changes from RepairStatusEditor and bubbles update through RepairManager', async () => {
    const statusEditor = mount(RepairStatusEditor, {
      props: {
        modelValue: 'open',
        options: [
          { value: 'open', label: 'Abierta' },
          { value: 'closed', label: 'Cerrada' },
        ],
      },
    })

    await statusEditor.find('select').setValue('closed')
    expect(statusEditor.emitted('update:modelValue')?.[0]?.[0]).toBe('closed')

    const repairs = [
      { id: 10, title: 'OT 10', status: 'open' },
      { id: 11, problem_reported: 'No enciende', status: 'pending' },
    ]
    const manager = mount(RepairManager, {
      props: {
        repairs,
        statusOptions: [
          { value: 'open', label: 'Abierta' },
          { value: 'pending', label: 'Pendiente' },
          { value: 'closed', label: 'Cerrada' },
        ],
      },
    })

    const selects = manager.findAll('select')
    expect(selects).toHaveLength(2)
    await selects[0].setValue('closed')
    expect(manager.emitted('update-status')?.[0]?.[0]).toEqual({
      repair: repairs[0],
      status: 'closed',
    })
  })

  it('runs IntakeForm full success flow including optional photo upload', async () => {
    apiMock.post.mockImplementation(async (url: string) => {
      if (url === '/clients') return { data: { id: 7 } }
      if (url === '/devices/') return { data: { id: 11 } }
      if (url === '/repairs') return { data: { id: 19 } }
      if (url === '/uploads/images') return { data: { path: '/uploads/intake-photo.jpg' } }
      return { data: { ok: true } }
    })

    const wrapper = mount(IntakeForm)

    const formInputs = wrapper.findAll('input.form-control')
    await formInputs[0].setValue('Ana Test')
    await wrapper.find('input[type="email"]').setValue('ana@test.cl')
    await wrapper.find('input[placeholder="Ej: Korg"]').setValue('Korg')
    await wrapper.find('input[placeholder="Ej: MS-20"]').setValue('MS-20')
    await wrapper.find('textarea[rows="3"]').setValue('No entrega audio')
    await wrapper.find('input[placeholder="Descripción de la foto"]').setValue('Foto inicial')

    const fileInput = wrapper.find('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [new File(['image-bytes'], 'init.png', { type: 'image/png' })],
      configurable: true,
    })
    await fileInput.trigger('change')

    const saveButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Guardar ingreso'))
    expect(saveButton).toBeTruthy()
    await saveButton!.trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenNthCalledWith(1, '/clients', {
      name: 'Ana Test',
      email: 'ana@test.cl',
      phone: '',
      address: '',
      notes: '',
    })
    expect(apiMock.post).toHaveBeenNthCalledWith(2, '/devices/', {
      client_id: 7,
      model: 'MS-20',
      brand_other: 'Korg',
      serial_number: null,
      description: null,
      condition_notes: null,
    })
    expect(apiMock.post).toHaveBeenNthCalledWith(3, '/repairs', {
      device_id: 11,
      problem_reported: 'No entrega audio',
      priority: 2,
    })
    expect(apiMock.post).toHaveBeenNthCalledWith(
      4,
      '/uploads/images',
      expect.any(FormData),
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    expect(apiMock.post).toHaveBeenNthCalledWith(5, '/repairs/19/photos', {
      photo_url: '/uploads/intake-photo.jpg',
      caption: 'Foto inicial',
      photo_type: 'general',
    })
    expect(wrapper.emitted('completed')?.[0]?.[0]).toEqual({
      client_id: 7,
      device_id: 11,
      repair_id: 19,
    })

    expect((wrapper.findAll('input.form-control')[0].element as HTMLInputElement).value).toBe('')
    expect((wrapper.find('input[placeholder="Ej: MS-20"]').element as HTMLInputElement).value).toBe('')
    expect((wrapper.find('textarea[rows="3"]').element as HTMLTextAreaElement).value).toBe('')
  })

  it('validates required fields and handles submit errors in IntakeForm', async () => {
    const wrapper = mount(IntakeForm)

    const saveButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Guardar ingreso'))
    expect(saveButton).toBeTruthy()
    await saveButton!.trigger('click')
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith(
      'Completa los campos obligatorios (cliente, email, modelo, problema).'
    )
    expect(apiMock.post).not.toHaveBeenCalled()

    apiMock.post.mockResolvedValueOnce({ data: {} })
    await wrapper.findAll('input.form-control')[0].setValue('Client Error')
    await wrapper.find('input[type="email"]').setValue('error@test.cl')
    await wrapper.find('input[placeholder="Ej: MS-20"]').setValue('Model Error')
    await wrapper.find('textarea[rows="3"]').setValue('Problema error')
    await saveButton!.trigger('click')
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('Error en ingreso completo')
  })
})
