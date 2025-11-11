<template>
  <Dialog v-model="show" :options="{ title: __('Insert POD ID') }">
    <template #body-content>
      <div class="mb-4">
        <div class="mb-1.5 text-sm text-ink-gray-5">{{ __('POD ID') }}</div>
        <FormControl
          v-model="podId"
          type="text"
          size="md"
          :placeholder="__('Enter POD ID')"
          @keyup.enter="insertPodId"
        />
        <div class="mt-1 text-xs text-ink-gray-4">
          {{ __('This POD ID will be applied to {0} selected lead(s)', [recordCount]) }}
        </div>
      </div>
    </template>
    <template #actions>
      <Button
        class="w-full"
        variant="solid"
        @click="insertPodId"
        :loading="loading"
        :label="__('Insert POD ID for {0} Leads', [recordCount])"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { FormControl, call, toast } from 'frappe-ui'
import { ref, computed } from 'vue'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  selectedValues: {
    type: Set,
    required: true,
  },
})

const show = defineModel()

const emit = defineEmits(['reload'])

const recordCount = computed(() => props.selectedValues?.size || 0)

const podId = ref('')
const loading = ref(false)

function insertPodId() {
  if (!podId.value.trim()) {
    toast.error(__('Please enter a POD ID'))
    return
  }

  loading.value = true
  
  call(
    'crm.api.lead_operations.bulk_insert_pod_id',
    {
      doctype: props.doctype,
      docnames: Array.from(props.selectedValues),
      pod_id: podId.value.trim(),
    }
  ).then((result) => {
    const data = result?.data || {}
    const updated = data.updated_count || 0
    const skipped = data.skipped_existing || []
    const failed = data.failed_leads || []

    if (updated > 0) {
      toast.success(__('POD ID inserted successfully for {0} lead(s)', [updated]))
    }

    if (skipped.length > 0) {
      toast.error(__('Skipped (POD ID already present):'))
      skipped.slice(0, 20).forEach((lead) => toast.error(lead))
      if (skipped.length > 20) {
        toast.error(__('... and {0} more', [skipped.length - 20]))
      }
    }

    if (failed.length > 0) {
      toast.error(__('Failed:'))
      failed.slice(0, 20).forEach((lead) => toast.error(lead))
      if (failed.length > 20) {
        toast.error(__('... and {0} more', [failed.length - 20]))
      }
    }

    podId.value = ''
    loading.value = false
    show.value = false
    emit('reload')
  }).catch((error) => {
    toast.error(__('Error inserting POD ID: {0}', [error.message || error]))
    loading.value = false
  })
}
</script>
