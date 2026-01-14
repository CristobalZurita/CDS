# 🌐 TRADUCCIÓN COMPLETA AL ESPAÑOL - CIRUJANO DE SINTETIZADORES

---

## 🗂️ ARCHIVOS INCLUIDOS Y DÓNDE VAN

| Archivo | Destino | Descripción |
|---------|---------|-------------|
| `strings.js` | `./src/composables/strings.js` | **CRÍTICO** - Todos los textos del sistema |
| `ContactSection.vue` | `./src/vue/content/sections/ContactSection.vue` | Sección de contacto |
| `PolicySection.vue` | `./src/vue/content/sections/PolicySection.vue` | Política de privacidad |
| `LicenseSection.vue` | `./src/vue/content/sections/LicenseSection.vue` | Términos y condiciones |
| `PortfolioSection.vue` | `./src/vue/content/sections/PortfolioSection.vue` | Portafolio (opcional) |
| `TeamSection.vue` | `./src/vue/content/sections/TeamSection.vue` | Equipo (opcional) |

---

## 📝 TRADUCCIONES EN strings.js

| Inglés (ANTES) | Español (AHORA) |
|----------------|-----------------|
| `"About"` | `"Nosotros"` |
| `"All"` | `"Todas"` |
| `"Thank you for getting in touch!"` | `"¡Gracias por contactarnos!"` |
| `"Your message has been received..."` | `"Tu mensaje ha sido recibido..."` |
| `"E-mail"` | `"Correo electrónico"` |
| `"Please fill all the fields."` | `"Por favor completa todos los campos."` |
| `"Please enter a valid e-mail address."` | `"Por favor ingresa un correo electrónico válido."` |
| `"There was an error sending the message."` | `"Hubo un error al enviar el mensaje."` |
| `"Loading..."` | `"Cargando..."` |
| `"Message"` | `"Mensaje"` |
| `"Name"` | `"Nombre"` |
| `"Send Message"` | `"Enviar mensaje"` |
| `"Sending Message..."` | `"Enviando mensaje..."` |
| `"Subject"` | `"Asunto"` |
| `"Tags:"` | `"Etiquetas:"` |
| `"Where To Find"` | `"Dónde encontrarnos"` |

---

## 📄 TRADUCCIONES EN ContactSection.vue

| Inglés (ANTES) | Español (AHORA) |
|----------------|-----------------|
| `"*Contact* Us"` | `"*Contáctanos*"` |
| `"Don't hesitate to reach us out!"` | `"¡No dudes en escribirnos!"` |

---

## 📄 TRADUCCIONES EN PolicySection.vue

| Inglés (ANTES) | Español (AHORA) |
|----------------|-----------------|
| `"*Privacy* Policy"` | `"Política de *Privacidad*"` |
| `"Understanding our practices"` | `"Cómo manejamos tu información"` |
| `"Collected Information"` | `"Información recopilada"` |
| `"Cookies"` | `"Cookies"` |
| `"Security"` | `"Seguridad"` |
| `"Links"` | `"Enlaces"` |
| Todo el contenido interno | Traducido completamente |

---

## 📄 TRADUCCIONES EN LicenseSection.vue

| Inglés (ANTES) | Español (AHORA) |
|----------------|-----------------|
| `"Usage *License*"` | `"*Términos* y Condiciones"` |
| `"Terms and Attributions"` | `"Licencia de uso y atribuciones"` |
| `"Usage"` | `"Uso del sitio"` |
| `"MIT License"` | `"Servicios"` |
| `"Disclaimer Note"` | `"Responsabilidad"` |
| Todo el contenido | Adaptado a Cirujano de Sintetizadores |

---

## 📄 TRADUCCIONES EN PortfolioSection.vue (opcional)

| Inglés (ANTES) | Español (AHORA) |
|----------------|-----------------|
| `"Get to know our amazing projects!"` | `"Conoce algunos de nuestros trabajos"` |
| Categorías en inglés | Categorías en español |

---

## 📄 TRADUCCIONES EN TeamSection.vue (opcional)

| Inglés (ANTES) | Español (AHORA) |
|----------------|-----------------|
| `"Our *Team*"` | `"Nuestro *Equipo*"` |
| `"Meet the main characters..."` | `"Conoce a las personas detrás del taller"` |

---

## ⚠️ ARCHIVOS QUE YA ESTABAN EN ESPAÑOL

Estos archivos del VOLCADO05 ya están correctamente en español y NO necesitan cambios:

- ✅ `AboutSection.vue` - "Sobre el taller"
- ✅ `ServicesSection.vue` - "Nuestros Servicios"
- ✅ `HistorySection.vue` - "Nuestra Historia"
- ✅ `FeaturedProjectSection.vue` - "Último trabajo"
- ✅ `FaqSection.vue` - "Preguntas Frecuentes"
- ✅ `ReviewsSection.vue` - "Opiniones de Clientes"
- ✅ `HeroSection.vue` - "MANTENCIÓN • RESTAURACIÓN • REPARACIÓN"
- ✅ `Master.vue` - Footer en español

---

## 🚀 INSTRUCCIONES DE INSTALACIÓN

1. Reemplaza `./src/composables/strings.js` con el archivo `strings.js`
2. Reemplaza `./src/vue/content/sections/ContactSection.vue`
3. Reemplaza `./src/vue/content/sections/PolicySection.vue`
4. Reemplaza `./src/vue/content/sections/LicenseSection.vue`
5. (Opcional) Reemplaza `PortfolioSection.vue` y `TeamSection.vue`
6. Ejecuta `npm run dev` y verifica

---

## 🧭 EJECUCIÓN LOCAL (BACKEND + FRONTEND)

Para navegar y probar la app completa en tu máquina:

1. Inicia el backend (usa SQLite por defecto):

```bash
# desde la raíz del proyecto
uvicorn backend.app.main:app --reload --port 8000
```

2. Inicia el frontend (Vite):

```bash
npm install
npm run dev
```

3. Abre la URL del frontend (por defecto http://localhost:5173) y asegúrate de que la API esté configurada en `http://localhost:8000/api/v1`.

Notas operativas:

- Para correr pruebas: `python -m pytest backend`
- Para una ejecución tipo producción con Postgres:
	- Exporta `DATABASE_URL` apuntando al Postgres y ejecuta `alembic upgrade head` antes de arrancar.
	- Si existen transacciones duplicadas en `payments.transaction_id`, ejecuta primero `python scripts/dedupe_payments_transaction_ids.py --dry-run` y luego `--apply`.

---

## 🔒 Seguridad local rápida

- **No pipes**: **no** hagas `curl ... | sh` ni `curl ... | bash`. Inspecciona las respuestas antes de ejecutar.
- Para parsear JSON sin `jq` usa Python seguro:

```bash
# obtener respuesta y verla de forma legible
curl -sS http://127.0.0.1:8000/api/v1/auth/login -d '{"email":"...","password":"..."}' -H 'Content-Type: application/json' | python -m json.tool
```

- Corremos `tools/scan_unsafe.sh` para detectar patrones peligrosos (eval, new Function, innerHTML) antes de commits.

---

## ✅ RESULTADO FINAL

Después de aplicar estos cambios, **TODA la página estará en español**:
- Formulario de contacto
- Mensajes de error y éxito
- Página de política de privacidad
- Página de términos y condiciones
- Textos del sistema (cargando, enviando, etc.)

---

**Fecha:** 2 de enero de 2026
**Versión:** 3.0 - Traducción completa al español
