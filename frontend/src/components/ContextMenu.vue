<template>
  <div
    v-if="show"
    class="fixed z-50 bg-white border border-gray-200 rounded-lg shadow-lg py-1 min-w-48 context-menu"
    :style="position"
    @click.stop
  >
    <div
      v-for="(action, index) in actions"
      :key="index"
      class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer flex items-center gap-2"
      @click="handleActionClick(action)"
    >
      <component v-if="action.icon" :is="action.icon" class="h-4 w-4" />
      <span>{{ action.label }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  x: {
    type: Number,
    default: 0,
  },
  y: {
    type: Number,
    default: 0,
  },
  actions: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['action-click', 'close'])

const position = computed(() => {
  const menuWidth = 192 // min-w-48 = 12rem = 192px
  const menuHeight = props.actions.length * 40 + 16 // Approximate height based on items
  
  let left = props.x
  let top = props.y
  
  // Check if menu would go off-screen horizontally
  if (left + menuWidth > window.innerWidth) {
    left = window.innerWidth - menuWidth - 10
  }
  
  // Check if menu would go off-screen vertically
  if (top + menuHeight > window.innerHeight) {
    top = window.innerHeight - menuHeight - 10
  }
  
  // Ensure menu doesn't go off-screen to the left or top
  left = Math.max(10, left)
  top = Math.max(10, top)
  
  return {
    left: `${left}px`,
    top: `${top}px`,
  }
})

const handleActionClick = (action) => {
  emit('action-click', action)
  emit('close')
}

const handleClickOutside = (event) => {
  // Check if the click is outside the context menu
  const contextMenu = document.querySelector('.context-menu')
  if (contextMenu && !contextMenu.contains(event.target)) {
    emit('close')
  }
}

const handleContextMenu = (event) => {
  // Always prevent default if the custom menu is open
  if (props.show) {
    event.preventDefault()
    event.stopPropagation()
    event.stopImmediatePropagation()
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('contextmenu', handleContextMenu, true)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('contextmenu', handleContextMenu, true)
})
</script>
