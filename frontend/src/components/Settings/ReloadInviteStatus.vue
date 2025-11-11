<template>
  <button
    class="inline-flex items-center p-1 text-gray-500 hover:text-gray-700 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
    @click="handleReload"
    :title="__('Reload invitation status')"
    :disabled="loading"
  >
    <FeatherIcon 
      name="refresh-cw" 
      class="w-4 h-4"
      :class="{ 'animate-spin': loading }" 
    />
  </button>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['reload'])

const handleReload = () => {
  if (!props.loading) {
    emit('reload')
  }
}
</script>
