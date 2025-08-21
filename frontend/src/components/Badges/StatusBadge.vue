<template>
  <div
    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
    :class="badgeClasses"
  >
    {{ status }}
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
  },
  // Accept an explicit color token (e.g. 'blue-600') or a theme name (e.g. 'blue')
  color: {
    type: String,
    default: 'gray-700',
  },
})

// Compute classes for text color and a lighter background tone
const badgeClasses = computed(() => {
  // If color is provided as theme (like 'blue'), map to text/bg tokens
  // Allow passing full tailwind token like 'blue-700' as well
  const themeMatch = props.color.match(/^([a-zA-Z]+)(?:-(\d{2,3}))?$/)
  if (themeMatch) {
    const theme = themeMatch[1]
    const tone = themeMatch[2] || '700'
    // text color uses the tone, background uses 50 for lighter look
    return `text-${theme}-${tone} bg-${theme}-50`
  }

  // Fallback to neutral
  return 'text-gray-700 bg-gray-50'
})
</script>