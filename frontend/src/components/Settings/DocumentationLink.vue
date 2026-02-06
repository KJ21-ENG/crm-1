<template>
  <div class="p-6">
    <div class="bg-white rounded-lg border shadow-sm p-8 text-center">
      <div class="mb-4">
        <FeatherIcon name="book" class="w-16 h-16 mx-auto text-blue-500" />
      </div>
      <h2 class="text-xl font-bold text-gray-900 mb-2">System Documentation</h2>
      <p class="text-gray-600 mb-6 max-w-md mx-auto">
        Access the comprehensive guide for Eshin Broking CRM, including modules, workflows, and compliance procedures.
      </p>
      <Button
        variant="solid"
        size="lg"
        @click="openDocs"
      >
        Open Documentation
      </Button>
    </div>
  </div>
</template>

<script setup>
import { Button, FeatherIcon } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()

function openDocs() {
  // Close settings modal if possible (optional, handled by routing)
  router.push({ name: 'Documentation' })
}
</script>
