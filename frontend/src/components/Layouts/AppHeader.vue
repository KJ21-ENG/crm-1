<template>
  <div class="flex items-center border-b pr-5">
    <Teleport v-if="teleportTargetReady" to="#app-header-right">
      <UniversalSearch />
    </Teleport>
    <div id="app-header" class="flex-1"></div>
    <div class="flex items-center gap-3">
      <UniversalSearch v-if="!teleportTargetReady" />
      <CallUI />
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import UniversalSearch from '@/components/UniversalSearch/UniversalSearch.vue'
import CallUI from '@/components/Telephony/CallUI.vue'

const teleportTargetReady = ref(false)
let observer = null

const updateTeleportTarget = () => {
  teleportTargetReady.value = !!document.querySelector('#app-header-right')
}

onMounted(() => {
  updateTeleportTarget()
  observer = new MutationObserver(updateTeleportTarget)
  observer.observe(document.body, { childList: true, subtree: true })
})

onBeforeUnmount(() => {
  observer && observer.disconnect()
  observer = null
})
</script>
