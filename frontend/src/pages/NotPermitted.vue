<template>
  <div class="grid h-full place-items-center px-4 py-20 text-center text-lg text-ink-gray-6">
    <div>
      <div class="mb-2 text-ink-gray-7">
        {{ __('Not permitted to access {0}', [moduleLabel]) }}
      </div>
      <Button :route="{ name: 'Leads' }">
        <template #prefix><LeadsIcon class="w-4" /></template>
        {{ __('Go to Leads') }}
      </Button>
    </div>
  </div>
  
</template>

<script setup>
import { useRoute } from 'vue-router'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import { computed } from 'vue'

const route = useRoute()
const moduleLabel = computed(() => route.query.module || 'this page')
</script>

