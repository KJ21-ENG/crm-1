<template>
  <div class="flex h-full w-full bg-gray-50 overflow-hidden">
    <!-- Sidebar -->
    <div class="w-64 flex-shrink-0 bg-white border-r border-gray-200 overflow-y-auto">
      <div class="p-4 border-b border-gray-200 sticky top-0 bg-white">
        <h2 class="text-lg font-semibold text-gray-900">Documentation</h2>
      </div>
      <nav class="p-2 space-y-1">
        <div v-if="loadingFiles" class="p-4 text-sm text-gray-400">Loading modules...</div>
        <router-link
          v-for="file in markdownFiles"
          :key="file.name"
          :to="`/documentation/${file.name}`"
          class="block px-3 py-2 text-sm rounded-md transition-colors"
          :class="[
            currentModule === file.name
              ? 'bg-gray-100 text-gray-900 font-medium'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          ]"
        >
          {{ formatTitle(file.name) }}
        </router-link>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-y-auto relative">
      <div v-if="loadingContent" class="absolute inset-0 flex items-center justify-center bg-white/50 backdrop-blur-sm z-10">
        <LoadingIndicator class="w-6 h-6 text-gray-500" />
      </div>

      <div v-if="!currentModule && !loadingContent" class="flex flex-col items-center justify-center h-full text-center text-gray-500 px-4">
        <FeatherIcon name="book-open" class="w-16 h-16 mb-4 text-gray-300" stroke-width="1.5" />
        <h3 class="text-lg font-medium text-gray-900">CRM Documentation</h3>
        <p class="mt-2 text-sm max-w-md">Select a module from the sidebar to view its documentation and step-by-step guides.</p>
      </div>

      <div v-else-if="currentModule" class="p-8 max-w-4xl mx-auto pb-20 prose prose-gray max-w-none">
        <div v-html="parsedMarkdown" class="markdown-body custom-prose"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import { LoadingIndicator, FeatherIcon } from 'frappe-ui'

const route = useRoute()
const currentModule = computed(() => route.params.module || '')

const markdownFiles = ref([
  // Fallback defaults in case auto-discovery is complex via standard fetching,
  // but we can just hardcode the known modules, or fetch an index index if one exists.
  // We'll hardcode the list here or fetch it. Let's hardcode for simplicity as Vite static assets
  // cannot be `readdir` listed at runtime easily without a custom json endpoint.
  { name: '01-tickets' },
  { name: '02-leads' },
  { name: '03-customers' },
  { name: '04-support-pages' },
  { name: '05-notes' },
  { name: '06-tasks' },
  { name: '07-call-logs' },
  { name: '08-requests' },
  { name: '09-dashboard-analytics' },
  { name: '10-dashboard-referral-analytics' },
  { name: '11-dashboard-call-log-analytics' },
  { name: '12-dashboard-user-dashboard' },
  { name: '13-dashboard-views' },
  { name: '14-global-search' },
  { name: '15-task-reminders' },
  { name: '16-quick-comments-leads-tickets' },
  { name: '17-login' },
  { name: '18-profile' },
  { name: '19-general-settings' },
  { name: '20-users' },
  { name: '21-roles-and-permissions' },
  { name: '22-invite-user' },
  { name: '23-email-account' },
  { name: '24-email-templates' },
  { name: '25-office-hours' },
  { name: '26-backup' },
  { name: '27-add-ons' }
])

const loadingFiles = ref(false)
const loadingContent = ref(false)
const rawMarkdown = ref('')
const parsedMarkdown = computed(() => {
  if (!rawMarkdown.value) return ''
  // Process the markdown: fix image paths
  let md = rawMarkdown.value
  
  // Convert "Screenshot Path: `...`" into a markdown image
  md = md.replace(/^Screenshot Path:\s*`?([^`\n]+)`?/gm, (match, path) => {
    let imagePath = path.trim()
    imagePath = imagePath.replace(/apps\/crm\/docs\/documentation creation task screenshots/g, '/assets/crm/frontend/docs/screenshots')
    imagePath = imagePath.replace(/apps\\crm\\docs\\documentation creation task screenshots/g, '/assets/crm/frontend/docs/screenshots')
    return `\n![Screenshot](${imagePath})\n`
  })
  
  // Remove the Placement lines entirely
  md = md.replace(/^Placement:[^\n]*/gm, '')
  
  // Render with marked
  return marked.parse(md)
})

function formatTitle(filename) {
  // Remove numbers at start "21-roles-and-permissions.md" -> "roles and permissions" -> "Roles And Permissions"
  const name = filename.replace(/^\d+-/, '').replace(/-/g, ' ')
  return name.replace(/\b\w/g, l => l.toUpperCase())
}

async function loadMarkdownContent(moduleName) {
  if (!moduleName) {
    rawMarkdown.value = ''
    return
  }
  loadingContent.value = true
  try {
    const url = `/assets/crm/frontend/docs/content/${moduleName}.md`
    const response = await fetch(url)
    if (!response.ok) {
      if (response.status === 404) {
        rawMarkdown.value = `# Document Not Found\n\nThe documentation for module **${moduleName}** could not be found.`
      } else {
        rawMarkdown.value = `# Error\n\nFailed to load documentation.`
      }
    } else {
      rawMarkdown.value = await response.text()
    }
  } catch (err) {
    console.error(err)
    rawMarkdown.value = `# Error\n\nFailed to load documentation.`
  } finally {
    loadingContent.value = false
  }
}

watch(currentModule, (newModule) => {
  loadMarkdownContent(newModule)
}, { immediate: true })

</script>

<style>
/* Add some standard prose styles if tailwind-typography is not available */
.custom-prose h1 {
  @apply text-3xl font-bold mb-6 text-gray-900 border-b pb-2;
}
.custom-prose h2 {
  @apply text-2xl font-semibold mt-8 mb-4 text-gray-800;
}
.custom-prose h3 {
  @apply text-xl font-medium mt-6 mb-3 text-gray-800;
}
.custom-prose p {
  @apply text-gray-700 leading-relaxed mb-4;
}
.custom-prose ul {
  @apply list-disc list-outside ml-6 mb-4 text-gray-700 space-y-1;
}
.custom-prose ol {
  @apply list-decimal list-outside ml-6 mb-4 text-gray-700 space-y-1;
}
.custom-prose img {
  @apply border border-gray-200 rounded-lg shadow-sm my-6 max-w-full h-auto;
}
.custom-prose strong {
  @apply font-semibold text-gray-900;
}
</style>
