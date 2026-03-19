import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

const optionalPhone = z.preprocess((value) => {
  const normalized = String(value || '').trim()
  return normalized ? normalized : undefined
}, z.string()
  .regex(/^(\+?56)?9\d{8}$/, 'Ingresa un teléfono válido, por ejemplo +56912345678')
  .optional())

export const quotationLeadSchema = z.object({
  nombre: z
    .string()
    .trim()
    .min(3, 'Ingresa tu nombre completo')
    .regex(/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/, 'El nombre solo puede incluir letras y espacios'),
  email: z
    .string()
    .trim()
    .email('Ingresa un email válido'),
  telefono: optionalPhone,
  acceptedDisclaimer: z
    .boolean()
    .refine((value) => value === true, 'Debes aceptar las condiciones del servicio'),
})

export const quotationLeadTypedSchema = toTypedSchema(quotationLeadSchema)
