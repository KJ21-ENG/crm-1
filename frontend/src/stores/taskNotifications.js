import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { computed, ref } from 'vue'

export const visible = ref(false)

export const taskNotifications = createResource({
  url: 'crm.api.task_notifications.get_task_notifications',
  initialData: [],
  auto: true,
})

export const unreadTaskNotificationsCount = computed(
  () => taskNotifications.data?.filter((n) => n.status !== 'Read').length || 0,
)

export const taskNotificationsStore = defineStore('crm-task-notifications', () => {
  const mark_as_read = createResource({
    url: 'crm.api.task_notifications.mark_all_notifications_read',
    onSuccess: () => {
      mark_as_read.params = {}
      taskNotifications.reload()
    },
  })

  const mark_notification_as_read = createResource({
    url: 'crm.api.task_notifications.mark_notification_read',
    onSuccess: () => {
      mark_notification_as_read.params = {}
      taskNotifications.reload()
    },
  })

  const create_test_notification = createResource({
    url: 'crm.api.task_notifications.create_test_task_notification',
    onSuccess: () => {
      create_test_notification.params = {}
      taskNotifications.reload()
    },
  })

  function toggle() {
    visible.value = !visible.value
  }

  function mark_doc_as_read(notificationName) {
    mark_notification_as_read.params = { notification_name: notificationName }
    mark_notification_as_read.reload()
    toggle()
  }

  return {
    unreadTaskNotificationsCount,
    mark_as_read,
    mark_notification_as_read,
    create_test_notification,
    mark_doc_as_read,
    toggle,
  }
}) 