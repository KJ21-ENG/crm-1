<template>
  <div class="flex items-center justify-between mb-6">
    <div class="flex items-center gap-4">
      <h1 class="text-2xl font-bold text-gray-900">{{ title }}</h1>
      <slot name="title-actions"></slot>
    </div>
    <div class="flex items-center gap-3">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  }
})
</script> 