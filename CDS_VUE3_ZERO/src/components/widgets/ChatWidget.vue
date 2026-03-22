<template>
  <div class="chat-widget">
    <!-- Panel -->
    <transition name="chat-slide">
      <div v-if="open" class="chat-panel">
        <div class="chat-header">
          <span class="chat-title">
            <i class="fa-solid fa-robot"></i> Asistente CDS
          </span>
          <div class="chat-header-actions">
            <button
              v-if="messages.length"
              class="chat-icon-btn"
              title="Limpiar conversación"
              type="button"
              @click="clear"
            >
              <i class="fa-solid fa-trash-can"></i>
            </button>
            <button class="chat-icon-btn" title="Cerrar" type="button" @click="toggle">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>

        <div ref="messagesEl" class="chat-messages">
          <div v-if="!messages.length" class="chat-welcome">
            <p>Hola, soy el asistente de Cristobal. Puedo ayudarte con servicios, precios, agenda, horario y ubicación del taller.</p>
          </div>

          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="chat-bubble"
            :class="msg.role === 'user' ? 'chat-bubble--user' : 'chat-bubble--model'"
          >
            {{ msg.text }}
          </div>

          <div v-if="loading" class="chat-bubble chat-bubble--model chat-bubble--typing">
            <span></span><span></span><span></span>
          </div>
        </div>

        <!-- Handoff: WhatsApp → link externo -->
        <div v-if="handoff === 'whatsapp'" class="chat-handoff">
          <span class="chat-handoff-text">
            <i class="fa-solid fa-arrow-right"></i> Continuar por WhatsApp
          </span>
          <a
            :href="handoffUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="chat-handoff-btn"
            @click="onHandoffClick"
          >
            <i class="fa-brands fa-whatsapp"></i> WhatsApp
          </a>
        </div>

        <!-- Handoff: Email → formulario inline -->
        <form v-else-if="handoff === 'email'" class="chat-email-form" @submit.prevent="submitEmailForm">
          <p class="chat-email-form-title">Envíame un mensaje y te respondo a la brevedad:</p>
          <input
            v-model="emailForm.name"
            class="chat-email-input"
            type="text"
            placeholder="Tu nombre"
            maxlength="80"
            :disabled="sendingEmail"
          />
          <input
            v-model="emailForm.email"
            class="chat-email-input"
            type="email"
            placeholder="Tu correo"
            maxlength="120"
            :disabled="sendingEmail"
          />
          <textarea
            v-model="emailForm.message"
            class="chat-email-input chat-email-textarea"
            placeholder="Tu consulta..."
            rows="3"
            maxlength="1000"
            :disabled="sendingEmail"
          ></textarea>
          <p v-if="emailError" class="chat-email-error">{{ emailError }}</p>
          <button
            class="chat-email-submit"
            type="submit"
            :disabled="sendingEmail"
          >
            <i class="fa-solid fa-paper-plane"></i>
            {{ sendingEmail ? 'Enviando...' : 'Enviar mensaje' }}
          </button>
        </form>

        <p v-if="error" class="chat-error">{{ error }}</p>

        <form class="chat-input-row" @submit.prevent="handleSend">
          <input
            ref="inputEl"
            v-model="input"
            class="chat-input"
            type="text"
            placeholder="Escribe tu consulta..."
            :disabled="loading"
            autocomplete="off"
            maxlength="500"
          />
          <button class="chat-send-btn" type="submit" :disabled="loading || !input.trim()">
            <i class="fa-solid fa-paper-plane"></i>
          </button>
        </form>
      </div>
    </transition>

    <!-- Trigger button — ocupa el lugar del botón WhatsApp -->
    <button
      class="chat-trigger"
      type="button"
      :aria-label="open ? 'Cerrar chat' : 'Chatea con nosotros'"
      @click="toggle"
    >
      <i :class="open ? 'fa-solid fa-xmark' : 'fa-brands fa-whatsapp'"></i>
    </button>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useChatWidget } from '@/composables/useChatWidget'

const {
  open, loading, messages, handoff, handoffUrl,
  input, error,
  emailForm, sendingEmail, emailError,
  toggle, send, submitEmailForm, confirmHandoff, clear,
} = useChatWidget()

const messagesEl = ref(null)
const inputEl = ref(null)

async function handleSend() {
  await send()
  await nextTick()
  inputEl.value?.focus()
}

function onHandoffClick() {
  confirmHandoff()
}

watch(messages, async () => {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}, { deep: true })

watch(open, async (val) => {
  if (val) {
    await nextTick()
    inputEl.value?.focus()
  }
})
</script>

<style scoped>
.chat-widget {
  position: fixed;
  left: 1rem;
  bottom: 1.25rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.6rem;
}

/* ── Trigger — posición, tamaño y color heredados del botón WhatsApp ── */
.chat-trigger {
  width: 50px;
  height: 50px;
  border-radius: var(--cds-radius-pill, 999px);
  border: none;
  background: #25d366;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.55rem;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(37, 211, 102, 0.45);
  transition: transform 0.2s, box-shadow 0.2s;
  flex-shrink: 0;
}

.chat-trigger:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 20px rgba(37, 211, 102, 0.55);
}

/* ── Panel ── */
.chat-panel {
  width: min(360px, calc(100vw - 2rem));
  display: flex;
  flex-direction: column;
  border-radius: 1.1rem;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.32);
  background: #23201d;
  border: 1px solid rgba(216, 189, 160, 0.18);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.7rem 0.85rem;
  background: #1b1814;
  border-bottom: 1px solid rgba(216, 189, 160, 0.14);
  gap: 0.5rem;
}

.chat-title {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--cds-primary);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.chat-header-actions {
  display: flex;
  gap: 0.3rem;
}

.chat-icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: rgba(225, 202, 176, 0.6);
  font-size: 0.9rem;
  padding: 0.2rem 0.3rem;
  border-radius: 0.4rem;
  transition: color 0.15s;
}

.chat-icon-btn:hover {
  color: #e1cab0;
}

.chat-messages {
  flex: 1;
  min-height: 200px;
  max-height: 320px;
  overflow-y: auto;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  scroll-behavior: smooth;
}

.chat-welcome {
  color: rgba(225, 202, 176, 0.7);
  font-size: 0.88rem;
  line-height: 1.5;
  text-align: center;
  padding: 0.5rem;
}

.chat-welcome p {
  margin: 0;
}

.chat-bubble {
  max-width: 85%;
  padding: 0.5rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.88rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.chat-bubble--user {
  align-self: flex-end;
  background: var(--cds-primary);
  color: #fff;
  border-bottom-right-radius: 0.25rem;
}

.chat-bubble--model {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.08);
  color: #e1cab0;
  border-bottom-left-radius: 0.25rem;
}

.chat-bubble--typing {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.6rem 0.85rem;
}

.chat-bubble--typing span {
  display: block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(225, 202, 176, 0.5);
  animation: typing-dot 1.2s infinite ease-in-out;
}

.chat-bubble--typing span:nth-child(2) { animation-delay: 0.2s; }
.chat-bubble--typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-dot {
  0%, 80%, 100% { transform: scale(1); opacity: 0.5; }
  40% { transform: scale(1.3); opacity: 1; }
}

/* ── Handoff bar ── */
.chat-handoff {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.55rem 0.85rem;
  background: rgba(37, 211, 102, 0.08);
  border-top: 1px solid rgba(37, 211, 102, 0.2);
  flex-wrap: wrap;
}

.chat-handoff-text {
  font-size: 0.82rem;
  color: rgba(225, 202, 176, 0.8);
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.chat-handoff-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  background: #25d366;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s;
}

.chat-handoff-btn:hover {
  background: #1da851;
}

/* ── Error ── */
.chat-error {
  margin: 0;
  padding: 0.3rem 0.85rem;
  font-size: 0.8rem;
  color: #ff7b7b;
}

/* ── Input ── */
.chat-input-row {
  display: flex;
  gap: 0.4rem;
  padding: 0.6rem 0.7rem;
  border-top: 1px solid rgba(216, 189, 160, 0.1);
  background: #1b1814;
}

.chat-input {
  flex: 1;
  min-height: 38px;
  border: 1px solid rgba(216, 189, 160, 0.2);
  border-radius: 999px;
  padding: 0.35rem 0.85rem;
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.06);
  color: #e1cab0;
  outline: none;
  transition: border-color 0.15s;
}

.chat-input::placeholder {
  color: rgba(225, 202, 176, 0.4);
}

.chat-input:focus {
  border-color: var(--cds-primary);
}

.chat-send-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: none;
  background: var(--cds-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s, opacity 0.15s;
}

.chat-send-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* ── Email form inline ── */
.chat-email-form {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding: 0.65rem 0.85rem;
  border-top: 1px solid rgba(216, 189, 160, 0.12);
  background: rgba(255, 255, 255, 0.04);
}

.chat-email-form-title {
  margin: 0 0 0.2rem;
  font-size: 0.82rem;
  color: rgba(225, 202, 176, 0.75);
}

.chat-email-input {
  min-height: 36px;
  border: 1px solid rgba(216, 189, 160, 0.2);
  border-radius: 0.6rem;
  padding: 0.35rem 0.7rem;
  font-size: 0.88rem;
  background: rgba(255, 255, 255, 0.06);
  color: #e1cab0;
  outline: none;
  font-family: inherit;
  transition: border-color 0.15s;
}

.chat-email-input::placeholder { color: rgba(225, 202, 176, 0.35); }
.chat-email-input:focus { border-color: var(--cds-primary); }
.chat-email-input:disabled { opacity: 0.5; }

.chat-email-textarea {
  min-height: 68px;
  resize: none;
}

.chat-email-error {
  margin: 0;
  font-size: 0.8rem;
  color: #ff7b7b;
}

.chat-email-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.45rem 1rem;
  border: none;
  border-radius: 999px;
  background: var(--cds-primary);
  color: #fff;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
}

.chat-email-submit:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Transition ── */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.97);
}

/* ── Responsive ── */
@media (min-width: 768px) {
  .chat-widget {
    left: 1.5rem;
    bottom: 1.5rem;
  }

  .chat-trigger {
    width: 54px;
    height: 54px;
    font-size: 1.75rem;
  }

  .chat-messages {
    max-height: 380px;
  }
}
</style>
