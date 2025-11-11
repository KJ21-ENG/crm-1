<template>
  <div class="flex items-center justify-between border-t px-3 py-2 sm:px-5">
    <!-- Left side - Page info and page size selector -->
    <div class="flex items-center gap-4">
      <!-- Page size selector -->
      <div class="flex items-center gap-2">
        <span class="text-sm text-ink-gray-7">{{ __('Show') }}</span>
        <FormControl
          type="select"
          :modelValue="pageSize"
          :options="pageSizeOptions"
          @update:modelValue="handlePageSizeChange"
          class="w-20"
        />
        <span class="text-sm text-ink-gray-7">{{ __('per page') }}</span>
      </div>
      
      <!-- Page info -->
      <div class="text-sm text-ink-gray-7">
        {{ __('Showing {0} to {1} of {2} results', [
          startIndex + 1,
          Math.min(endIndex, totalCount),
          totalCount
        ]) }}
      </div>
    </div>

    <!-- Right side - Pagination controls -->
    <div class="flex items-center gap-2">
      <!-- Previous page button -->
      <Button
        variant="ghost"
        size="sm"
        :disabled="currentPage <= 1"
        @click="goToPage(currentPage - 1)"
      >
        <template #prefix>
          <FeatherIcon name="chevron-left" class="h-4 w-4" />
        </template>
        {{ __('Previous') }}
      </Button>

      <!-- Page numbers -->
      <div class="flex items-center gap-1">
        <!-- First page -->
        <Button
          v-if="showFirstPage"
          variant="ghost"
          size="sm"
          @click="goToPage(1)"
          class="min-w-[32px]"
        >
          1
        </Button>

        <!-- Ellipsis after first page -->
        <span v-if="showFirstEllipsis" class="px-2 text-ink-gray-5">...</span>

        <!-- Page numbers -->
        <Button
          v-for="page in visiblePages"
          :key="page"
          :variant="page === currentPage ? 'solid' : 'ghost'"
          size="sm"
          @click="goToPage(page)"
          class="min-w-[32px]"
        >
          {{ page }}
        </Button>

        <!-- Ellipsis before last page -->
        <span v-if="showLastEllipsis" class="px-2 text-ink-gray-5">...</span>

        <!-- Last page -->
        <Button
          v-if="showLastPage"
          variant="ghost"
          size="sm"
          @click="goToPage(totalPages)"
          class="min-w-[32px]"
        >
          {{ totalPages }}
        </Button>
      </div>

      <!-- Next page button -->
      <Button
        variant="ghost"
        size="sm"
        :disabled="currentPage >= totalPages"
        @click="goToPage(currentPage + 1)"
      >
        {{ __('Next') }}
        <template #suffix>
          <FeatherIcon name="chevron-right" class="h-4 w-4" />
        </template>
      </Button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Button, FormControl, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 20
  },
  totalCount: {
    type: Number,
    default: 0
  },
  pageSizeOptions: {
    type: Array,
    default: () => [
      { label: '20', value: 20 },
      { label: '50', value: 50 },
      { label: '100', value: 100 }
    ]
  }
})

const emit = defineEmits(['pageChange', 'pageSizeChange'])

// Computed properties
const totalPages = computed(() => {
  return Math.ceil(props.totalCount / props.pageSize)
})

const startIndex = computed(() => {
  return (props.currentPage - 1) * props.pageSize
})

const endIndex = computed(() => {
  return props.currentPage * props.pageSize
})

// Pagination logic for showing page numbers
const maxVisiblePages = 5

const visiblePages = computed(() => {
  const pages = []
  const halfVisible = Math.floor(maxVisiblePages / 2)
  
  let start = Math.max(1, props.currentPage - halfVisible)
  let end = Math.min(totalPages.value, start + maxVisiblePages - 1)
  
  // Adjust start if we're near the end
  if (end - start < maxVisiblePages - 1) {
    start = Math.max(1, end - maxVisiblePages + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const showFirstPage = computed(() => {
  return visiblePages.value[0] > 1
})

const showLastPage = computed(() => {
  return visiblePages.value[visiblePages.value.length - 1] < totalPages.value
})

const showFirstEllipsis = computed(() => {
  return visiblePages.value[0] > 2
})

const showLastEllipsis = computed(() => {
  return visiblePages.value[visiblePages.value.length - 1] < totalPages.value - 1
})

// Methods
function goToPage(page) {
  if (page >= 1 && page <= totalPages.value && page !== props.currentPage) {
    emit('pageChange', page)
  }
}

function handlePageSizeChange(newPageSize) {
  emit('pageSizeChange', newPageSize)
}
</script>


