# Frontend Development

Guide to developing the Vue.js frontend for Eshin CRM.

---

## Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Vue.js | 3.x | UI framework |
| Vite | 5.x | Build tool |
| Frappe UI | Latest | Component library |
| Tailwind CSS | 3.x | Styling |
| Pinia/Vuex | - | State management |

---

## Development Setup

### Install Dependencies

```bash
cd ~/frappe-bench/apps/crm/frontend
yarn install
```

### Start Development Server

```bash
yarn dev
```

Access at: `http://localhost:8080`

### Build for Production

```bash
yarn build
```

Or via bench:
```bash
cd ~/frappe-bench
bench build --app crm
```

---

## Directory Structure

```
frontend/src/
├── components/      # Reusable components
│   ├── Activities/  # Activity feed
│   ├── CRM/        # Core CRM components
│   ├── Layouts/    # Page layouts
│   └── Modals/     # Modal dialogs
├── pages/          # Route pages
├── stores/         # State management
├── composables/    # Vue composables
├── utils/          # Utility functions
├── router.js       # Vue Router config
└── main.js         # App entry
```

---

## Creating a Component

### Basic Component

```vue
<!-- src/components/MyComponent.vue -->
<template>
  <div class="my-component">
    <h2>{{ title }}</h2>
    <slot></slot>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update'])

const handleUpdate = () => {
  emit('update', { data: 'value' })
}
</script>

<style scoped>
.my-component {
  padding: 1rem;
}
</style>
```

### Using Frappe UI

```vue
<template>
  <Button @click="handleClick">Click Me</Button>
  <Dialog v-model="showDialog">
    <template #body>Dialog content</template>
  </Dialog>
  <FormControl v-model="inputValue" label="Input" />
</template>

<script setup>
import { Button, Dialog, FormControl } from 'frappe-ui'
import { ref } from 'vue'

const showDialog = ref(false)
const inputValue = ref('')

const handleClick = () => {
  showDialog.value = true
}
</script>
```

---

## Creating a Page

### Page Component

```vue
<!-- src/pages/MyPage.vue -->
<template>
  <LayoutHeader>
    <template #left-header>
      <h1>My Page</h1>
    </template>
    <template #right-header>
      <Button @click="create">+ Create</Button>
    </template>
  </LayoutHeader>
  
  <div class="page-content">
    <!-- Content -->
  </div>
</template>

<script setup>
import { LayoutHeader } from '@/components/Layouts'
import { Button } from 'frappe-ui'
</script>
```

### Register Route

```javascript
// src/router.js
{
  path: '/crm/my-page',
  name: 'MyPage',
  component: () => import('@/pages/MyPage.vue'),
}
```

---

## API Calls

### Using call()

```javascript
import { call } from 'frappe-ui'

// Simple call
const result = await call('crm.api.doc.get_list', {
  doctype: 'CRM Lead',
  filters: { status: 'New' }
})

// With error handling
try {
  const data = await call('crm.api.doc.get_doc', {
    doctype: 'CRM Lead',
    name: 'LEAD-001'
  })
} catch (error) {
  console.error('API Error:', error)
}
```

### Using createResource

```javascript
import { createResource } from 'frappe-ui'

const leadResource = createResource({
  url: 'crm.api.doc.get_doc',
  params: {
    doctype: 'CRM Lead',
    name: leadName
  },
  auto: true,
  onSuccess(data) {
    console.log('Lead loaded:', data)
  }
})

// Access data
console.log(leadResource.data)

// Reload
leadResource.reload()
```

---

## State Management

### Using Stores

```javascript
// src/stores/leads.js
import { defineStore } from 'pinia'
import { call } from 'frappe-ui'

export const useLeadsStore = defineStore('leads', {
  state: () => ({
    leads: [],
    loading: false
  }),
  
  actions: {
    async fetchLeads(filters = {}) {
      this.loading = true
      try {
        this.leads = await call('crm.api.doc.get_list', {
          doctype: 'CRM Lead',
          filters
        })
      } finally {
        this.loading = false
      }
    }
  }
})
```

### Using in Component

```vue
<script setup>
import { useLeadsStore } from '@/stores/leads'

const leadsStore = useLeadsStore()

// Fetch on mount
onMounted(() => {
  leadsStore.fetchLeads()
})
</script>

<template>
  <div v-if="leadsStore.loading">Loading...</div>
  <LeadList v-else :leads="leadsStore.leads" />
</template>
```

---

## Styling

### Tailwind Classes

```vue
<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <h2 class="text-lg font-semibold text-gray-900">Title</h2>
    <p class="mt-2 text-sm text-gray-600">Description</p>
  </div>
</template>
```

### Scoped Styles

```vue
<style scoped>
.custom-class {
  @apply p-4 bg-white rounded-lg;
}
</style>
```

---

## Component Mapping

| UI Screen | Component Path |
|-----------|----------------|
| Lead Modal | `components/Modals/LeadModal.vue` |
| Ticket Modal | `components/Modals/TicketModal.vue` |
| Task Modal | `components/Modals/TaskModal.vue` |
| Sidebar | `components/Layouts/AppSidebar.vue` |
| Activity Feed | `components/Activities/` |
| Dashboard | `pages/Dashboard.vue` |

---

## Hot Reload

Development server supports hot reload:
- Changes to `.vue` files update instantly
- State is preserved during updates
- Full reload for structural changes

---

## Related Guides

- [Repository Structure](repo-structure.md)
- [Testing](testing.md)
