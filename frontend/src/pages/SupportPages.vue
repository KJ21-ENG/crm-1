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
        <div v-if="supportPages.loading" class="flex items-center justify-center h-64">
          <div class="text-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <div class="text-lg text-ink-gray-6">{{ __('Loading support pages...') }}</div>
          </div>
        </div>
        
        <div v-else-if="!paginatedData.length" class="flex items-center justify-center h-64">
          <div class="text-center">
            <SupportPagesIcon class="h-12 w-12 text-ink-gray-4 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-ink-gray-9 mb-2">{{ __('No support pages found') }}</h3>
            <p class="text-ink-gray-6 mb-4">{{ __('Create your first support page to get started') }}</p>
            <Button variant="solid" :label="__('Create Support Page')" @click="showCreateModal = true">
              <template #prefix>
                <FeatherIcon name="plus" class="h-4" />
              </template>
            </Button>
          </div>
        </div>
        
        <div v-else class="p-5">
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
                />
                <Button 
                  size="sm" 
                  variant="outline" 
                  theme="red" 
                  :label="__('Delete')" 
                  @click="deletePage(page)"
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
          <label class="block text-sm font-medium text-ink-gray-7 mb-2">{{ __('Page Name') }}</label>
          <TextInput 
            v-model="formData.page_name" 
            :placeholder="__('Enter page name')" 
            required
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-ink-gray-7 mb-2">{{ __('Support Link') }}</label>
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

const router = useRouter()

// State
const showCreateModal = ref(false)
const editingPage = ref(null)
const saving = ref(false)

// Pagination state
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

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
  
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  
  return supportPages.data.slice(startIndex, endIndex)
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
  
  if (!formData.support_link.startsWith('http://') && !formData.support_link.startsWith('https://')) {
    toast.error(__('Support link must start with http:// or https://'))
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

// Watch for data changes to update total count
watch(() => supportPages.data, (newData) => {
  if (newData && newData.length > 0) {
    totalCount.value = newData.length
  } else {
    totalCount.value = 0
  }
}, { immediate: true })

onMounted(() => {
  if (!supportPages.data) {
    supportPages.fetch()
  }
})
</script> 