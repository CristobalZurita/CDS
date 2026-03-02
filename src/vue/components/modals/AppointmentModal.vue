<template>
    <div class="appointment-modal-overlay" @click="closeModal">
        <div class="appointment-modal" @click.stop>
            <!-- Header -->
            <div class="modal-header">
                <h2>Agenda tu hora</h2>
                <button class="close-btn" type="button" aria-label="Cerrar" @click.stop="closeModal">
                    <i class="fa-solid fa-times"></i>
                </button>
            </div>

            <!-- Form -->
            <form @submit.prevent="submitForm" class="appointment-form">
                <!-- Nombre -->
                <div class="form-group">
                    <label for="nombre">Nombre *</label>
                    <input 
                        id="nombre"
                        v-model="formData.nombre"
                        type="text"
                        placeholder="Tu nombre completo"
                        @blur="validateNombre"
                        class="form-control"
                        :class="{ 'is-invalid': errors.nombre }"
                    />
                    <small v-if="errors.nombre" class="error-message">
                        {{ errors.nombre }}
                    </small>
                </div>

                <!-- Email -->
                <div class="form-group">
                    <label for="email">Email *</label>
                    <input 
                        id="email"
                        v-model="formData.email"
                        type="email"
                        placeholder="tu@ejemplo.com"
                        @blur="validateEmail"
                        class="form-control"
                        :class="{ 'is-invalid': errors.email }"
                    />
                    <small v-if="errors.email" class="error-message">
                        {{ errors.email }}
                    </small>
                </div>

                <!-- Teléfono -->
                <div class="form-group">
                    <label for="telefono">Teléfono *</label>
                    <input 
                        id="telefono"
                        v-model="formData.telefono"
                        type="tel"
                        placeholder="+56912345678"
                        @blur="validateTelefono"
                        class="form-control"
                        :class="{ 'is-invalid': errors.telefono }"
                    />
                    <small v-if="errors.telefono" class="error-message">
                        {{ errors.telefono }}
                    </small>
                </div>

                <!-- Fecha -->
                <div class="form-group">
                    <label for="fecha">Fecha *</label>
                    <input 
                        id="fecha"
                        v-model="formData.fecha"
                        type="date"
                        @blur="validateFecha"
                        class="form-control"
                        :class="{ 'is-invalid': errors.fecha }"
                    />
                    <small v-if="errors.fecha" class="error-message">
                        {{ errors.fecha }}
                    </small>
                </div>

                <!-- Mensaje -->
                <div class="form-group full-width">
                    <label for="mensaje">Mensaje (opcional)</label>
                    <textarea 
                        id="mensaje"
                        v-model="formData.mensaje"
                        placeholder="Cuéntanos sobre tu instrumento o consulta..."
                        rows="4"
                        class="form-control"
                    ></textarea>
                </div>

                <!-- Submit -->
                <div class="form-actions full-width">
                    <button type="submit" class="btn-submit" :disabled="isSubmitting">
                        <span v-if="!isSubmitting">Agendar cita</span>
                        <span v-else>
                            <i class="fa-solid fa-spinner fa-spin"></i> Enviando...
                        </span>
                    </button>
                </div>
            </form>

            <!-- Success Message -->
            <div v-if="showSuccess" class="success-message">
                <div class="success-content">
                    <i class="fa-solid fa-check-circle"></i>
                    <h3>¡Mensaje Enviado!</h3>
                    <p>Tu cita ha sido agendada exitosamente.</p>
                    <button class="btn-close-success" @click="closeModal">
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { api } from '@/services/api'

const emit = defineEmits(['close', 'submit'])

const showSuccess = ref(false)
const isSubmitting = ref(false)
const formData = reactive({
    nombre: '',
    email: '',
    telefono: '',
    fecha: '',
    mensaje: ''
})
const errors = reactive({
    nombre: '',
    email: '',
    telefono: '',
    fecha: ''
})

// Validación: Nombre (solo letras, acentos y Ñ)
const validateNombre = () => {
    const nombreRegex = /^[a-záéíóúñA-ZÁÉÍÓÚÑ\s]+$/
    
    if (!formData.nombre.trim()) {
        errors.nombre = 'El nombre es requerido'
    } else if (!nombreRegex.test(formData.nombre)) {
        errors.nombre = 'El nombre solo puede contener letras, acentos y espacios'
    } else {
        errors.nombre = ''
    }
}

// Validación: Email (formato A@B.CD mínimo 5 elementos)
const validateEmail = () => {
    // Formato: nombre@dominio.extensión
    // Mínimo 5 caracteres: a@b.cd
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    
    if (!formData.email.trim()) {
        errors.email = 'El email es requerido'
    } else if (formData.email.length < 5) {
        errors.email = 'El email debe tener al menos 5 caracteres'
    } else if (!emailRegex.test(formData.email)) {
        errors.email = 'Por favor ingresa un email válido (ejemplo@dominio.com)'
    } else {
        errors.email = ''
    }
}

// Validación: Teléfono (solo + y números)
const validateTelefono = () => {
    const telefonoRegex = /^\+\d+$/
    
    if (!formData.telefono.trim()) {
        errors.telefono = 'El teléfono es requerido'
    } else if (!telefonoRegex.test(formData.telefono)) {
        errors.telefono = 'El teléfono debe comenzar con + y solo contener números'
    } else {
        errors.telefono = ''
    }
}

// Validación: Fecha
const validateFecha = () => {
    if (!formData.fecha) {
        errors.fecha = 'La fecha es requerida'
    } else {
        const selectedDate = new Date(formData.fecha)
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        
        if (selectedDate < today) {
            errors.fecha = 'La fecha debe ser en el futuro'
        } else {
            errors.fecha = ''
        }
    }
}

// Validar todos los campos
const validateAll = () => {
    validateNombre()
    validateEmail()
    validateTelefono()
    validateFecha()
    
    return !errors.nombre && !errors.email && !errors.telefono && !errors.fecha
}

// Enviar formulario
const submitForm = async () => {
    if (!validateAll()) {
        return
    }
    
    isSubmitting.value = true
    
    try {
        const appointmentData = {
            nombre: formData.nombre.trim(),
            email: formData.email.trim(),
            telefono: formData.telefono.trim(),
            fecha: formData.fecha,
            mensaje: formData.mensaje.trim(),
            createdAt: new Date().toISOString()
        }
        
        // Enviar al backend
        await api.post('/appointments/', appointmentData)
        showSuccess.value = true
        emit('submit', appointmentData)
        
        // Limpiar formulario
        formData.nombre = ''
        formData.email = ''
        formData.telefono = ''
        formData.fecha = ''
        formData.mensaje = ''
    } catch (error) {
        console.error('Error:', error)
        alert('Error de conexión. Intenta nuevamente.')
    } finally {
        isSubmitting.value = false
    }
}

// Cerrar modal
const closeModal = () => {
    // emitimos siempre para que el padre pueda ocultar el modal
    emit('close')
    // Reset success visual state
    showSuccess.value = false
}

// Cerrar con ESC
const handleKeydown = (e) => {
    if (e.key === 'Escape' || e.key === 'Esc') {
        closeModal()
    }
}

onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
})
</script>
