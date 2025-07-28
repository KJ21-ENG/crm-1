<template>
  <div class="column grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
    <div
      v-if="column.label && !column.hideLabel"
      class="text-ink-gray-9 max-w-fit text-base col-span-full"
    >
      {{ column.label }}
    </div>
    <template v-for="field in column.fields" :key="field.fieldname">
      <Field :field="field" :data-name="field.fieldname" />
    </template>
  </div>
</template>
<script setup>
import Field from '@/components/FieldLayout/Field.vue'

const props = defineProps({
  column: Object,
})
</script>
