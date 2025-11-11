<template>
  <div class="flex space-x-1 rounded-lg bg-gray-100 p-1">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      :class="[
        'px-3 py-1.5 text-sm font-medium rounded-md',
        modelValue === tab.value
          ? 'bg-white text-gray-900 shadow'
          : 'text-gray-500 hover:text-gray-700'
      ]"
      @click="$emit('update:modelValue', tab.value)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true
  },
  tabs: {
    type: Array,
    required: true,
    validator: (tabs) => {
      return tabs.every(tab => 
        typeof tab === 'object' && 
        'label' in tab && 
        'value' in tab
      )
    }
  }
})

defineEmits(['update:modelValue'])
</script> 