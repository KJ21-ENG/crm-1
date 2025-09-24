<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <Button variant="solid" :label="__('Create')" @click="showCreateModal = true">
        <template #prefix>
          <FeatherIcon name="plus" class="h-4" />
        </template>
      </Button>
    </template>
  </LayoutHeader>
  
  <div class="flex h-full overflow-hidden">
    <div class="flex-1 flex flex-col">
      
      <!-- Content -->
      <div class="flex-1 overflow-auto">
        <!-- Search Bar - Always Visible in White Area -->
        <div class="p-5">
          <div class="relative max-w-md">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <FeatherIcon name="search" class="h-5 w-5 text-ink-gray-4" />
            </div>
            <TextInput
              v-model="searchQuery"
              :placeholder="__('Search by page name or description...')"
              class="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              v-if="searchQuery.trim()"
              @click="clearSearch"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-ink-gray-4 hover:text-ink-gray-6"
              :title="__('Clear search')"
            >
              <FeatherIcon name="x" class="h-5 w-5" />
            </button>
          </div>
        </div>
        
        <div v-if="supportPages.loading" class="flex items-center justify-center h-64">
          <div class="text-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <div class="text-lg text-ink-gray-6">{{ __('Loading support pages...') }}</div>
          </div>
        </div>
        
        <div v-else-if="!paginatedData.length" class="flex items-center justify-center h-64">
          <div class="text-center">
            <SupportPagesIcon class="h-12 w-12 text-ink-gray-4 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-ink-gray-9 mb-2">
              {{ searchQuery.trim() ? __('No pages match your search') : __('No support pages found') }}
            </h3>
            <p class="text-ink-gray-6 mb-4">
              {{ searchQuery.trim() ? __('Try adjusting your search terms') : __('Create your first support page to get started') }}
            </p>
            <Button 
              v-if="!searchQuery.trim() && canWriteSupport"
              variant="solid" 
              :label="__('Create Support Page')" 
              @click="showCreateModal = true"
            >
              <template #prefix>
                <FeatherIcon name="plus" class="h-4" />
              </template>
            </Button>
          </div>
        </div>
        
        <div v-else class="px-5 pb-5">
          <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div 
              v-for="page in paginatedData" 
              :key="page.name"
              class="border rounded-lg p-4 hover:shadow-md transition-shadow"
              :class="{ 'border-green-200 bg-green-50': page.is_active, 'border-gray-200 bg-gray-50': !page.is_active }"
            >
              <div class="flex items-start justify-between mb-3">
                <div class="flex-1">
                  <h3 class="font-medium text-ink-gray-9 mb-1">{{ page.page_name }}</h3>
                  <p class="text-sm text-ink-gray-6">{{ page.description || __('No description') }}</p>
                </div>
                <Badge 
                  :label="page.is_active ? __('Active') : __('Inactive')"
                  :theme="page.is_active ? 'green' : 'gray'"
                  variant="subtle"
                />
              </div>
              
              <div class="mb-3">
                <p class="text-xs text-ink-gray-5 mb-1">{{ __('Support Link') }}</p>
                <a 
                  :href="page.support_link" 
                  target="_blank" 
                  class="text-sm text-blue-600 hover:text-blue-800 truncate block"
                >
                  {{ page.support_link }}
                </a>
              </div>
              
              <div class="flex gap-2">
                <Button 
                  size="sm" 
                  variant="outline" 
                  :label="__('Edit')" 
                  @click="editPage(page)"
                  v-if="canWriteSupport"
                />
                <Button 
                  size="sm" 
                  variant="outline" 
                  theme="red" 
                  :label="__('Delete')" 
                  @click="deletePage(page)"
                  v-if="canWriteSupport"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Pagination -->
  <Pagination
    v-if="paginatedData.length > 0 && totalCount > 0"
    class="border-t px-3 py-2 sm:px-5"
    :current-page="currentPage"
    :page-size="pageSize"
    :total-count="totalCount"
    @page-change="handlePageChange"
    @page-size-change="handlePageSizeChange"
  />
  
  <!-- Create/Edit Modal -->
  <Dialog 
    v-model="showCreateModal" 
    :options="{ title: editingPage ? __('Edit Support Page') : __('Create Support Page') }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-ink-gray-7 mb-2">
            {{ __('Page Name') }} <span class="text-red-600">*</span>
          </label>
          <TextInput 
            v-model="formData.page_name" 
            :placeholder="__('Enter page name')" 
            required
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-ink-gray-7 mb-2">
            {{ __('Support Link') }} <span class="text-red-600">*</span>
          </label>
          <TextInput 
            v-model="formData.support_link" 
            :placeholder="__('https://example.com/support')" 
            required
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-ink-gray-7 mb-2">{{ __('Description') }}</label>
          <TextInput 
            v-model="formData.description" 
            :placeholder="__('Brief description of this support page')" 
          />
        </div>
        
        <div class="flex items-center">
          <input 
            id="is_active" 
            v-model="formData.is_active" 
            type="checkbox" 
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label for="is_active" class="ml-2 block text-sm text-ink-gray-7">
            {{ __('Active') }}
          </label>
        </div>
      </div>
    </template>
    
    <template #actions>
      <Button 
        variant="outline" 
        :label="__('Cancel')" 
        @click="cancelEdit"
      />
      <Button 
        variant="solid" 
        :label="editingPage ? __('Update') : __('Create')" 
        @click="savePage"
        :loading="saving"
      />
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import SupportPagesIcon from '@/components/Icons/SupportPagesIcon.vue'
import Pagination from '@/components/Pagination.vue'
import { 
  Breadcrumbs, 
  Button, 
  TextInput, 
  Dialog, 
  Badge, 
  FeatherIcon, 
  createResource, 
  call,
  toast 
} from 'frappe-ui'
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { permissionsStore } from '@/stores/permissions'

const router = useRouter()

// Permissions
const { canWrite } = permissionsStore()
const canWriteSupport = computed(() => canWrite('Support Pages'))

// State
const showCreateModal = ref(false)
const editingPage = ref(null)
const saving = ref(false)

// Pagination state
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

// Search state
const searchQuery = ref('')

// Form data
const formData = reactive({
  page_name: '',
  support_link: '',
  description: '',
  is_active: true
})

// Breadcrumbs
const breadcrumbs = [
  { label: __('Support Pages'), route: { name: 'Support Pages' } }
]

// Support Pages Resource
const supportPages = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Support Pages',
    fields: ['name', 'page_name', 'support_link', 'description', 'is_active', 'created_by', 'creation_date'],
    order_by: 'creation_date desc'
  },
  auto: true,
  onResponse: (response) => {
    // Update total count from response
    if (response && response.length !== undefined) {
      totalCount.value = response.length
    }
  }
})

// Computed property for paginated data
const paginatedData = computed(() => {
  if (!supportPages.data) return []
  
  // Filter data based on search query
  let filteredData = supportPages.data
  
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filteredData = supportPages.data.filter(page => 
      page.page_name?.toLowerCase().includes(query) ||
      page.description?.toLowerCase().includes(query)
    )
  }
  
  // Update total count for pagination
  totalCount.value = filteredData.length
  
  // Apply pagination to filtered data
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  
  return filteredData.slice(startIndex, endIndex)
})

// Methods
function editPage(page) {
  editingPage.value = page
  formData.page_name = page.page_name
  formData.support_link = page.support_link
  formData.description = page.description || ''
  formData.is_active = page.is_active
  showCreateModal.value = true
}

function cancelEdit() {
  editingPage.value = null
  formData.page_name = ''
  formData.support_link = ''
  formData.description = ''
  formData.is_active = true
  showCreateModal.value = false
}

async function savePage() {
  if (!formData.page_name || !formData.support_link) {
    toast.error(__('Please fill in all required fields'))
    return
  }
  // Accept http(s) URLs or domain names like xyz.com
  const supportLinkPattern = /^(https?:\/\/[\w.-]+(?:\/\S*)?|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$/
  if (!supportLinkPattern.test(formData.support_link)) {
    toast.error(__('Support link must be a valid URL (http://, https://) or a domain name like xyz.com'))
    return
  }
  
  saving.value = true
  
  try {
    if (editingPage.value) {
      // Update existing page
      await call('frappe.client.set_value', {
        doctype: 'CRM Support Pages',
        name: editingPage.value.name,
        fieldname: {
          page_name: formData.page_name,
          support_link: formData.support_link,
          description: formData.description,
          is_active: formData.is_active
        }
      })
      toast.success(__('Support page updated successfully'))
    } else {
      // Create new page
      await call('frappe.client.insert', {
        doc: {
          doctype: 'CRM Support Pages',
          page_name: formData.page_name,
          support_link: formData.support_link,
          description: formData.description,
          is_active: formData.is_active
        }
      })
      toast.success(__('Support page created successfully'))
    }
    
    supportPages.reload()
    cancelEdit()
  } catch (error) {
    console.error('Error saving support page:', error)
    toast.error(__('Error saving support page: {0}', [error.message]))
  } finally {
    saving.value = false
  }
}

async function deletePage(page) {
  if (!confirm(__('Are you sure you want to delete this support page?'))) {
    return
  }
  
  try {
    await call('frappe.client.delete', {
      doctype: 'CRM Support Pages',
      name: page.name
    })
    toast.success(__('Support page deleted successfully'))
    supportPages.reload()
  } catch (error) {
    console.error('Error deleting support page:', error)
    toast.error(__('Error deleting support page: {0}', [error.message]))
  }
}

function handlePageChange(page) {
  currentPage.value = page
  // No need to reload for client-side pagination
}

function handlePageSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1 // Reset to first page when page size changes
  // No need to reload for client-side pagination
}

function clearSearch() {
  searchQuery.value = ''
  supportPages.reload() // Reload data to show all items
}

// Watch for data changes to update total count
watch(() => supportPages.data, (newData) => {
  if (newData && newData.length > 0) {
    // Don't set totalCount here as it's now handled in paginatedData computed
  } else {
    totalCount.value = 0
  }
}, { immediate: true })

// Watch for search query changes to reset pagination
watch(searchQuery, () => {
  currentPage.value = 1 // Reset to first page when searching
})

onMounted(() => {
  if (!supportPages.data) {
    supportPages.fetch()
  }
})
</script> 
