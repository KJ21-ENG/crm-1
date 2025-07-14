<template>
  <div
    v-if="visible"
    ref="target"
    class="absolute z-20 h-screen bg-surface-white transition-all duration-300 ease-in-out"
    :style="{
      'box-shadow': '8px 0px 8px rgba(0, 0, 0, 0.1)',
      'max-width': '350px',
      'min-width': '350px',
      left: 'calc(100% + 1px)',
      top: '60px', // Offset to show below main notifications
    }"
  >
    <div class="flex h-screen flex-col text-ink-gray-9">
      <div
        class="z-20 flex items-center justify-between border-b bg-surface-white px-5 py-2.5"
      >
        <div class="text-base font-medium">{{ __('Task Reminders') }}</div>
        <div class="flex gap-1">
          <Tooltip :text="__('Mark all as read')">
            <div>
              <Button variant="ghost" @click="() => markAllAsRead()">
                <template #icon>
                  <MarkAsDoneIcon class="h-4 w-4" />
                </template>
              </Button>
            </div>
          </Tooltip>
          <Tooltip :text="__('Test Notification')">
            <div>
              <Button variant="ghost" @click="() => createTestNotification()">
                <template #icon>
                  <TestIcon class="h-4 w-4" />
                </template>
              </Button>
            </div>
          </Tooltip>
          <Tooltip :text="__('Close')">
            <div>
              <Button variant="ghost" @click="() => toggle()">
                <template #icon>
                  <FeatherIcon name="x" class="h-4 w-4" />
                </template>
              </Button>
            </div>
          </Tooltip>
        </div>
      </div>
      <div
        v-if="taskNotifications.data?.length"
        class="divide-y divide-outline-gray-modals overflow-auto text-base"
      >
        <div
          v-for="n in taskNotifications.data"
          :key="n.name"
          class="flex cursor-pointer items-start gap-2.5 px-4 py-2.5 hover:bg-surface-gray-2"
          @click="handleNotificationClick(n)"
        >
          <div class="mt-1 flex items-center gap-2.5">
            <div
              class="size-[5px] rounded-full"
              :class="[n.status === 'Read' ? 'bg-transparent' : 'bg-blue-500']"
            />
            <TaskIcon 
              class="size-7"
              :class="[
                n.notification_type === 'Due Date Reminder' ? 'text-orange-500' : '',
                n.notification_type === 'Overdue Task' ? 'text-red-500' : '',
                n.notification_type === 'Task Assignment' ? 'text-blue-500' : '',
                n.notification_type === 'Task Completion' ? 'text-green-500' : ''
              ]"
            />
          </div>
          <div class="flex-1">
            <div v-if="n.notification_text" v-html="n.notification_text" />
            <div v-else class="mb-2 space-x-1 leading-5 text-ink-gray-5">
              <span class="font-medium text-ink-gray-9">
                {{ n.notification_type }}
              </span>
              <span v-if="n.task_title">
                {{ n.task_title }}
              </span>
            </div>
            <div class="flex items-center gap-2 text-sm text-ink-gray-5">
              <span>{{ __(timeAgo(n.sent_at)) }}</span>
              <span v-if="n.task_priority" class="flex items-center gap-1">
                <TaskPriorityIcon :priority="n.task_priority" />
                {{ n.task_priority }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="n.reference_doctype && n.reference_docname"
              variant="ghost"
              size="sm"
              @click.stop="openReference(n)"
            >
              <template #icon>
                <ArrowUpRightIcon class="h-3 w-3" />
              </template>
            </Button>
            <Button
              v-if="n.status !== 'Read'"
              variant="ghost"
              size="sm"
              @click.stop="markAsRead(n.name)"
            >
              <template #icon>
                <MarkAsDoneIcon class="h-3 w-3" />
              </template>
            </Button>
          </div>
        </div>
      </div>
      <div
        v-else
        class="flex flex-1 flex-col items-center justify-center gap-2"
      >
        <TaskIcon class="h-20 w-20 text-ink-gray-2" />
        <div class="text-lg font-medium text-ink-gray-4">
          {{ __('No task notifications') }}
        </div>
        <Button
          variant="outline"
          size="sm"
          @click="createTestNotification"
        >
          {{ __('Create Test Notification') }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import TaskPriorityIcon from '@/components/Icons/TaskPriorityIcon.vue'
import MarkAsDoneIcon from '@/components/Icons/MarkAsDoneIcon.vue'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import TestIcon from '@/components/Icons/SquareAsterisk.vue'
import {
  visible,
  taskNotifications,
  taskNotificationsStore,
} from '@/stores/taskNotifications'
import { globalStore } from '@/stores/global'
import { timeAgo } from '@/utils'
import { onClickOutside } from '@vueuse/core'
import { capture } from '@/telemetry'
import { Tooltip } from 'frappe-ui'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { $socket } = globalStore()
const { mark_as_read, toggle, mark_notification_as_read, create_test_notification } = taskNotificationsStore()

const target = ref(null)
onClickOutside(
  target,
  () => {
    if (visible.value) toggle()
  },
  {
    ignore: ['#task-notifications-btn'],
  },
)

function markAsRead(notificationName) {
  capture('task_notification_mark_as_read')
  mark_notification_as_read(notificationName)
}

function markAllAsRead() {
  capture('task_notification_mark_all_as_read')
  mark_as_read.reload()
}

function createTestNotification() {
  capture('task_notification_create_test')
  create_test_notification.reload()
}

function handleNotificationClick(notification) {
  if (notification.status !== 'Read') {
    markAsRead(notification.name)
  }
  
  // Navigate to task or reference document
  if (notification.task) {
    // Navigate to task page with task highlighted
    router.push({
      name: 'Tasks',
      query: { open: notification.task }
    })
  } else if (notification.reference_doctype && notification.reference_docname) {
    openReference(notification)
  }
}

function openReference(notification) {
  if (notification.reference_doctype === 'CRM Lead') {
    router.push({
      name: 'Lead',
      params: { leadId: notification.reference_docname },
      hash: '#tasks'
    })
  } else if (notification.reference_doctype === 'CRM Deal') {
    router.push({
      name: 'Deal',
      params: { dealId: notification.reference_docname },
      hash: '#tasks'
    })
  }
}

onBeforeUnmount(() => {
  $socket.off('crm_task_notification')
})

onMounted(() => {
  $socket.on('crm_task_notification', (data) => {
    taskNotifications.reload()
    
    // Show browser notification if supported
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('CRM Task Reminder', {
        body: data.message || 'You have a new task notification',
        icon: '/assets/crm/images/logo.svg'
      })
    }
  })
})
</script>

<style scoped>
/* Custom scrollbar for notification area */
.overflow-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 