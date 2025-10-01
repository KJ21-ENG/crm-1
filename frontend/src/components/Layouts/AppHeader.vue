<template>
  <div class="flex items-center border-b pr-5">
    <div id="app-header" class="flex-1"></div>
    <div class="flex items-center gap-3">
      <UniversalSearch />
      <CallUI />
    </div>
  </div>
</template>

<script setup>
import UniversalSearch from '@/components/UniversalSearch/UniversalSearch.vue'
import CallUI from '@/components/Telephony/CallUI.vue'
</script>
