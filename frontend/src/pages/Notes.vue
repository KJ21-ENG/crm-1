<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Notes" />
    </template>
    <template #right-header>
      <Button v-if="canWriteNotes" variant="solid" :label="__('Create')" @click="createNote">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="notes"
    v-model:loadMore="loadMore"
    v-model:updatedPageCount="updatedPageCount"
    doctype="FCRM Note"
    :options="{
      defaultViewName: __('Notes View'),
    }"
  />
  <div class="flex-1 overflow-y-auto">
    <div
      v-if="notes.data?.data?.length"
      class="grid grid-cols-1 gap-2 px-3 pb-2 sm:grid-cols-4 sm:gap-4 sm:px-5 sm:pb-3"
    >
      <div
        v-for="note in notes.data.data"
        class="group flex h-56 cursor-pointer flex-col justify-between gap-2 rounded-lg border px-5 py-4 shadow-sm hover:bg-surface-menu-bar"
        @click="editNote(note)"
      >
        <div class="flex items-center justify-between">
          <div class="truncate text-lg font-medium text-ink-gray-9">
            {{ note.title }}
          </div>
          <Dropdown
            :options="(
              canWriteNotes
                ? [
                    {
                      label: __('Delete'),
                      icon: 'trash-2',
                      onClick: () => deleteNote(note.name),
                    },
                  ]
                : []
            )"
            @click.stop
          >
            <Button
              icon="more-horizontal"
              variant="ghosted"
              class="hover:bg-surface-white"
            />
          </Dropdown>
        </div>
        <TextEditor
          v-if="note.content"
          :content="note.content"
          :editable="false"
          editor-class="prose-sm text-p-sm max-w-none text-ink-gray-5 focus:outline-none"
          class="flex-1 overflow-hidden"
        />
        <div class="mt-2 flex items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <UserAvatar :user="note.owner" size="xs" />
            <div class="text-sm text-ink-gray-8">
              {{ getUser(note.owner).full_name }}
            </div>
            <!-- Customer info injected from backend: customer_name & customer_mobile_no -->
            <div v-if="note.customer_name" class="text-sm text-ink-gray-7 ml-3">
              • {{ note.customer_name }}
              <span v-if="note.customer_mobile_no"> ({{ note.customer_mobile_no }})</span>
            </div>
          </div>
          <Tooltip :text="formatDate(note.modified)">
            <div class="text-sm text-ink-gray-7">
              {{ __(timeAgo(note.modified)) }}
            </div>
          </Tooltip>
        </div>
      </div>
    </div>
  </div>
  <Pagination
    v-if="notes.data?.data?.length && notes.data?.total_count > 0"
    class="border-t px-3 py-2 sm:px-5"
    :current-page="currentPage"
    :page-size="pageSize"
    :total-count="notes.data.total_count"
    @page-change="handlePageChange"
    @page-size-change="handlePageSizeChange"
  />
  <div v-else class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <NoteIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Notes')]) }}</span>
      <Button v-if="canWriteNotes" :label="__('Create')" @click="createNote">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
  <NoteModal
    v-model="showNoteModal"
    v-model:reloadNotes="notes"
    :note="currentNote"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import NoteModal from '@/components/Modals/NoteModal.vue'
import ViewControls from '@/components/ViewControls.vue'
import Pagination from '@/components/Pagination.vue'
import { usersStore } from '@/stores/users'
import { timeAgo, formatDate } from '@/utils'
import { TextEditor, call, Dropdown, Tooltip } from 'frappe-ui'
import { ref, watch, computed } from 'vue'
import { permissionsStore } from '@/stores/permissions'

const { getUser } = usersStore()

const showNoteModal = ref(false)
const currentNote = ref(null)

const notes = ref({})
const loadMore = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Permissions
const { canWrite } = permissionsStore()
const canWriteNotes = computed(() => canWrite('Notes'))

// Add pagination computed properties
const currentPage = computed(() => {
  // Use the current page from the list data if available, otherwise fallback to 1
  if (!notes.value?.data?.page_length) return 1
  const start = notes.value.data.start || 0
  const pageLength = notes.value.data.page_length
  const calculatedPage = Math.floor(start / pageLength) + 1
  
  console.log('🔍 Notes Debug - Current page calculation:', {
    start,
    pageLength,
    calculatedPage,
    listData: notes.value?.data
  })
  
  return calculatedPage
})

const pageSize = computed(() => {
  // Try to get page length from multiple possible sources
  // First try to get it from ViewControls internal state
  const viewControlsPageLength = viewControls.value?.list?.params?.page_length
  
  // Fallback to the notes data
  const dataPageLength = notes.value?.data?.page_length || 
                        notes.value?.data?.page_length_count || 
                        updatedPageCount.value || 
                        20
  
  // Use ViewControls value if available, otherwise fallback to data
  const pageLength = viewControlsPageLength || dataPageLength
  
  console.log('🔍 Notes Debug - Page size calculation:', {
    pageLength,
    viewControlsPageLength,
    dataPageLength,
    dataPageLengthFromNotes: notes.value?.data?.page_length,
    dataPageLengthCount: notes.value?.data?.page_length_count,
    updatedPageCount: updatedPageCount.value,
    notesData: notes.value?.data
  })
  
  return pageLength
})

// Add pagination methods
function handlePageChange(page) {
  console.log('🔍 Notes Debug - Page change requested:', page)
  if (viewControls.value) {
    viewControls.value.goToPage(page)
  }
}

function handlePageSizeChange(pageSize) {
  console.log('🔍 Notes Debug - Page size change requested:', pageSize)
  console.log('🔍 Notes Debug - ViewControls ref:', viewControls.value)
  console.log('🔍 Notes Debug - ViewControls methods:', {
    updatePageLength: typeof viewControls.value?.updatePageLength,
    goToPage: typeof viewControls.value?.goToPage
  })
  
  if (viewControls.value) {
    try {
      viewControls.value.updatePageLength(pageSize)
      console.log('🔍 Notes Debug - updatePageLength called successfully')
    } catch (error) {
      console.error('🔍 Notes Debug - Error calling updatePageLength:', error)
    }
  } else {
    console.warn('🔍 Notes Debug - ViewControls ref is null')
  }
}

watch(
  () => notes.value?.data?.page_length_count,
  (val, old_value) => {
    openNoteFromURL()
    if (!val || val === old_value) return
    updatedPageCount.value = val
  },
)

// Add a watch to see when the notes data changes
watch(
  () => notes.value?.data,
  (newData, oldData) => {
    console.log('🔍 Notes Debug - Data changed:', {
      newData,
      oldData,
      pageLength: newData?.page_length,
      pageLengthCount: newData?.page_length_count,
      totalCount: newData?.total_count
    })
  },
  { deep: true }
)

function createNote() {
  currentNote.value = {
    title: '',
    content: '',
  }
  showNoteModal.value = true
}

function editNote(note) {
  currentNote.value = note
  showNoteModal.value = true
}

async function deleteNote(name) {
  await call('frappe.client.delete', {
    doctype: 'FCRM Note',
    name,
  })
  notes.value.reload()
}

const openNoteFromURL = () => {
  const searchParams = new URLSearchParams(window.location.search)
  const noteName = searchParams.get('open')

  if (noteName && notes.value?.data?.data) {
    const foundNote = notes.value.data.data.find(
      (note) => note.name === noteName,
    )
    if (foundNote) {
      editNote(foundNote)
    }
    searchParams.delete('open')
    window.history.replaceState(null, '', window.location.pathname)
  }
}
</script>
