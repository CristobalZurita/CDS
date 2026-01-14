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
        const response = await fetch('/api/v1/appointments/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(appointmentData)
        })
        
        if (response.ok) {
            showSuccess.value = true
            emit('submit', appointmentData)
            
            // Limpiar formulario
            formData.nombre = ''
            formData.email = ''
            formData.telefono = ''
            formData.fecha = ''
            formData.mensaje = ''
        } else {
            alert('Error al agendar la cita. Intenta nuevamente.')
        }
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

<style scoped lang="scss">
@import '/src/scss/_variables.scss';
@import '/src/scss/_theming.scss';

.appointment-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center; /* modal centrado (formato apaisado) */
    z-index: 1000;
    padding: 1rem;
    animation: fadeIn 0.3s ease-in-out;

    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
}

.appointment-modal {
    background: white;
    border-radius: 12px; /* modal centrado con bordes redondeados uniformes */
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    width: 100%;
    max-width: 900px; /* formato apaisado */
    overflow-y: auto;
    max-height: 90vh;
    height: auto;
    animation: slideUp 0.3s ease-in-out;

    @keyframes slideUp {
        from {
            transform: translateY(30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem;
    border-bottom: 2px solid $light-2;
    background: linear-gradient(135deg, $primary 0%, rgba($primary, 0.8) 100%);
    color: white;

    h2 {
        margin: 0;
        font-size: 1.5rem;
        font-family: 'Cervo Neue', serif;
        font-weight: 600;
    }

    .close-btn {
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.2s;

        &:hover {
            background: rgba(255, 255, 255, 0.2);
        }
    }
}

.appointment-form {
    padding: 2rem;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem 1.5rem;
    align-items: start;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;

    label {
        font-weight: 600;
        color: $text-normal;
        font-size: 0.95rem;
        font-family: 'Steelfish', sans-serif;
    }

    .form-control {
        padding: 0.75rem;
        border: 2px solid $light-2;
        border-radius: 8px;
        font-family: inherit;
        font-size: 1rem;
        transition: border-color 0.2s, box-shadow 0.2s;

        &:focus {
            outline: none;
            border-color: $primary;
            box-shadow: 0 0 0 3px rgba($primary, 0.1);
        }

        &.is-invalid {
            border-color: #dc3545;

            &:focus {
                box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
            }
        }

        &::placeholder {
            color: $text-muted;
        }
    }

    textarea.form-control {
        resize: vertical;
        min-height: 100px;
    }

    .error-message {
        color: #dc3545;
        font-size: 0.85rem;
        font-weight: 500;
    }
}

.form-group.full-width { grid-column: 1 / -1 }
.form-actions { grid-column: 1 / -1; display:flex; justify-content:flex-end }
.form-actions .btn-submit { min-width: 220px }

.btn-submit {
    padding: 0.75rem 1.5rem;
    background: $primary;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    font-family: 'Steelfish', sans-serif;

    &:hover:not(:disabled) {
        background: darken($primary, 10%);
        transform: translateY(-2px);
    }

    &:active:not(:disabled) {
        transform: translateY(0);
    }

    &:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    i {
        margin-right: 0.5rem;
    }
}

.success-message {
    padding: 2rem;
    text-align: center;
}

.success-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;

    i {
        font-size: 3rem;
        color: #28a745;
    }

    h3 {
        margin: 0;
        color: $text-normal;
        font-family: 'Cervo Neue', serif;
        font-size: 1.5rem;
    }

    p {
        margin: 0;
        color: $text-muted;
        font-size: 0.95rem;
    }

    .btn-close-success {
        margin-top: 1rem;
        padding: 0.75rem 2rem;
        background: $primary;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
        font-family: 'Steelfish', sans-serif;

        &:hover {
            background: darken($primary, 10%);
        }
    }
}

// Responsive
@media (max-width: 576px) {
    .appointment-modal-overlay {
        justify-content: center; /* en móviles volvemos al centro */
    }

    .appointment-modal {
        max-width: 95vw;
        border-radius: 8px;
        height: auto;
        max-height: 90vh;
    }

    .modal-header {
        padding: 1.5rem;

        h2 {
            font-size: 1.25rem;
        }
    }

    .appointment-form {
        padding: 1.5rem;
        gap: 1rem;
        display: flex;
        flex-direction: column;
    }

    .form-group {
        gap: 0.35rem;

        label {
            font-size: 0.9rem;
        }
    }
}
</style>
