import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createDialog } from './utils/dialogs'
import { initSocket } from './socket'
import router from './router'
import translationPlugin from './translation'
import { posthogPlugin } from './telemetry'
import App from './App.vue'

import {
  FrappeUI,
  Button,
  Input,
  TextInput,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  setConfig,
  frappeRequest,
  FeatherIcon,
} from 'frappe-ui'

let globalComponents = {
  Button,
  TextInput,
  Input,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  FeatherIcon,
}

// create a pinia instance
let pinia = createPinia()

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)
app.use(FrappeUI)
app.use(pinia)
app.use(router)
app.use(translationPlugin)
app.use(posthogPlugin)
for (let key in globalComponents) {
  app.component(key, globalComponents[key])
}

app.config.globalProperties.$dialog = createDialog

let socket
if (import.meta.env.DEV) {
  frappeRequest({ url: '/api/method/crm.www.crm.get_context_for_dev' }).then(
    (values) => {
      for (let key in values) {
        window[key] = values[key]
      }
      socket = initSocket()
      app.config.globalProperties.$socket = socket
      app.mount('#app')
    },
  )
} else {
  socket = initSocket()
  app.config.globalProperties.$socket = socket
  app.mount('#app')
}

if (import.meta.env.DEV) {
  window.$dialog = createDialog
}

// Global safety net: auto-reload once on unhandled chunk-load failures
window.addEventListener('unhandledrejection', (event) => {
  try {
    const reason = event && (event.reason || {})
    const message = String(reason && (reason.message || reason))
    const matches =
      /Failed to fetch dynamically imported module/i.test(message) ||
      /Loading chunk (\d+|[A-Za-z0-9_-]+) failed/i.test(message) ||
      /Importing a module script failed/i.test(message) ||
      /ChunkLoadError/i.test(message)
    const alreadyReloaded = sessionStorage.getItem('crm_global_chunk_reload') === '1'
    if (matches && !alreadyReloaded) {
      sessionStorage.setItem('crm_global_chunk_reload', '1')
      window.location.reload()
    }
  } catch (_) {
    // ignore
  }
})
