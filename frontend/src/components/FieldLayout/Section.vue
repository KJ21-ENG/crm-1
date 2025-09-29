<template>
  <div
    v-if="!section.hidden"
    class="section"
    :class="[
      section.hideBorder
        ? 'pt-4'
        : 'border-t border-outline-gray-modals mt-5 pt-5',
    ]"
  >
    <Section
      class="text-lg font-medium"
      :class="{ 'px-3 sm:px-5': hasTabs }"
      :labelClass="['text-lg font-medium', { 'px-3 sm:px-5': hasTabs }]"
      :label="section.label"
      :hideLabel="section.hideLabel || !section.label"
      :opened="section.opened"
      :collapsible="section.collapsible"
      collapseIconPosition="right"
    >
      <!-- Render fields in aligned rows across columns -->
      <div
        :style="{ display: 'grid', gridTemplateColumns: `repeat(${(section.columns || []).length}, minmax(0, 1fr))`, gap: '1rem' }"
        class="mt-4"
      >
        <template v-for="rowIndex in rowCount" :key="rowIndex">
          <template v-for="colIndex in (section.columns || []).length" :key="colIndex">
            <div>
              <Field v-if="getFieldAt(colIndex-1, rowIndex-1)" :field="getFieldAt(colIndex-1, rowIndex-1)" @swap="$emit('swap')"/>
            </div>
          </template>
        </template>
      </div>
    </Section>
  </div>
</template>
<script setup>
import Section from '@/components/Section.vue'
import Column from '@/components/FieldLayout/Column.vue'
import { inject } from 'vue'

const props = defineProps({
  section: Object,
})

const hasTabs = inject('hasTabs')
// compute row count and helper to fetch fields by position
import { computed } from 'vue'

const rowCount = computed(() => {
  const cols = props.section?.columns || []
  let max = 0
  cols.forEach((c) => {
    const len = (c.fields || []).length
    if (len > max) max = len
  })
  return max || 0
})

function getFieldAt(colIndex, rowIndex) {
  const cols = props.section?.columns || []
  const col = cols[colIndex]
  if (!col) return null
  const field = col.fields?.[rowIndex]
  return field || null
}
</script>
