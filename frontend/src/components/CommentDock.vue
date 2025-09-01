<template>
  <div
    v-if="commentDockVisible"
    ref="panel"
    class="fixed right-4 bottom-4 z-30 w-[360px] max-h-[70vh] rounded-lg border bg-surface-white shadow-xl flex flex-col"
  >
    <div class="flex items-center justify-between border-b px-4 py-2.5">
      <div class="text-base font-medium">{{ __('Comments') }}</div>
      <div class="flex items-center gap-1">
        <Tooltip :text="__('Mark all as read')">
          <div>
            <Button variant="ghost" size="sm" @click="markAllAsRead">
              <FeatherIcon name="check" class="h-4 w-4" />
            </Button>
          </div>
        </Tooltip>
        <Tooltip :text="__('Close')">
          <div>
            <Button variant="ghost" size="sm" @click="toggle">
              <FeatherIcon name="x" class="h-4 w-4" />
            </Button>
          </div>
        </Tooltip>
      </div>
    </div>
    <div v-if="commentNotifications.data?.length" class="flex-1 overflow-auto divide-y">
      <div
        v-for="n in commentNotifications.data"
        :key="n.name"
        class="flex items-start gap-2 px-4 py-3 hover:bg-surface-gray-2"
      >
        <div class="mt-1">
          <div class="size-[6px] rounded-full" :class="n.status === 'Read' ? 'bg-transparent' : 'bg-blue-500'" />
        </div>
        <div class="flex-1 min-w-0">
          <div v-if="n.notification_text" v-html="n.notification_text" class="text-sm leading-5" />
          <div class="flex items-center gap-2 text-xs text-ink-gray-6 mt-1">
            <span>{{ __(timeAgo(n.sent_at)) }}</span>
            <span v-if="n.reference_doctype && n.reference_docname" class="truncate">
              {{ n.reference_doctype }} • {{ n.reference_docname }}
            </span>
          </div>
          <div v-if="n.reference_doctype && n.reference_docname" class="mt-2 flex gap-2">
            <Input v-model="quickReplyText[n.name]" size="sm" placeholder="Reply..." class="flex-1" />
            <Button size="sm" variant="subtle" @click="sendReply(n)">{{ __('Send') }}</Button>
          </div>
        </div>
        <div class="flex items-center gap-1">
          <Button v-if="n.status !== 'Read'" variant="ghost" size="sm" @click="markAsRead(n.name)">
            <FeatherIcon name="check" class="h-4 w-4" />
          </Button>
          <Button v-if="n.reference_doctype && n.reference_docname" variant="ghost" size="sm" @click="openReference(n)">
            <FeatherIcon name="arrow-up-right" class="h-4 w-4" />
          </Button>
          <Button
            v-if="n.reference_doctype && n.reference_docname"
            variant="ghost"
            size="sm"
            :class="isMuted(n.reference_doctype, n.reference_docname) ? 'text-ink-gray-6' : ''"
            @click="toggleMute(n.reference_doctype, n.reference_docname)"
          >
            <FeatherIcon :name="isMuted(n.reference_doctype, n.reference_docname) ? 'bell-off' : 'bell'" class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
    <div v-else class="flex flex-1 items-center justify-center p-8 text-ink-gray-5">
      {{ __('No comment notifications') }}
    </div>
  </div>

  <!-- Floating button -->
  <button
    class="fixed right-4 bottom-4 z-20 grid place-items-center rounded-full bg-blue-600 text-white shadow-lg h-12 w-12"
    @click="toggle"
    aria-label="Toggle Comments"
  >
    <span class="relative">
      <FeatherIcon name="message-square" class="h-5 w-5" />
      <span v-if="unreadCommentCount" class="absolute -right-2 -top-2 rounded-full bg-red-500 text-[10px] leading-4 px-[6px]">
        {{ unreadCommentCount > 99 ? '99+' : unreadCommentCount }}
      </span>
    </span>
  </button>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Tooltip, FeatherIcon, Input, Button } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { timeAgo } from '@/utils'
import {
  commentNotifications,
  commentDockVisible,
  unreadCommentCount,
  commentNotificationsStore,
} from '@/stores/commentNotifications'
import { globalStore } from '@/stores/global'

const router = useRouter()
const { $socket } = globalStore()
const { toggle, markAllAsRead, markAsRead, sendQuickReply, isMuted, toggleMute } = commentNotificationsStore()

const quickReplyText = ref({})

function openReference(n) {
  if (n.reference_doctype === 'CRM Lead') {
    router.push({ name: 'Lead', params: { leadId: n.reference_docname }, hash: '#comments' })
  } else if (n.reference_doctype === 'CRM Deal') {
    router.push({ name: 'Deal', params: { dealId: n.reference_docname }, hash: '#comments' })
  } else if (n.reference_doctype === 'CRM Ticket') {
    router.push({ name: 'Ticket', params: { ticketId: n.reference_docname }, hash: '#comments' })
  }
}

function sendReply(n) {
  const text = quickReplyText.value[n.name]
  if (!text) return
  sendQuickReply(n.reference_doctype, n.reference_docname, text)
  quickReplyText.value[n.name] = ''
}

function onKeydown(e) {
  if (e.shiftKey && (e.key === 'C' || e.key === 'c')) {
    e.preventDefault()
    toggle()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  $socket.on('crm_task_notification', (data) => {
    // Reuse the same channel; backend publishes mentions/new messages via CRM Task Notification
    // Always refresh to keep unread badge accurate
    commentNotifications.reload()
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
</style>


