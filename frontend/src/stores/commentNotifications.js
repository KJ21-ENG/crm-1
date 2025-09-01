import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { computed, ref } from 'vue'
import { useStorage } from '@vueuse/core'

export const commentDockVisible = ref(false)

export const commentNotifications = createResource({
  url: 'crm.api.comment_notifications.get_comment_notifications',
  initialData: [],
  auto: true,
})

export const unreadCommentCount = computed(
  () => commentNotifications.data?.filter((n) => n.status !== 'Read').length || 0,
)

export const commentNotificationsStore = defineStore('crm-comment-notifications', () => {
  const mutedThreads = useStorage('crm_comment_muted_threads', [])
  const mark_all_read = createResource({
    url: 'crm.api.comment_notifications.mark_all_comment_notifications_read',
    onSuccess: () => {
      mark_all_read.params = {}
      commentNotifications.reload()
    },
  })

  const mark_one_read = createResource({
    url: 'crm.api.comment_notifications.mark_comment_notification_read',
    onSuccess: () => {
      mark_one_read.params = {}
      commentNotifications.reload()
    },
  })

  const quick_reply = createResource({
    url: 'crm.api.comment_notifications.quick_reply',
    onSuccess: () => {
      quick_reply.params = {}
      commentNotifications.reload()
    },
  })

  function toggle() {
    commentDockVisible.value = !commentDockVisible.value
    if (commentDockVisible.value && !commentNotifications.data?.length) {
      commentNotifications.reload()
    }
  }

  function markAsRead(name) {
    mark_one_read.params = { notification_name: name }
    mark_one_read.reload()
  }

  function markAllAsRead() {
    mark_all_read.reload()
  }

  function sendQuickReply(reference_doctype, reference_docname, content) {
    quick_reply.params = { reference_doctype, reference_docname, content }
    quick_reply.reload()
  }

  function isMuted(reference_doctype, reference_docname) {
    return (mutedThreads.value || []).some(
      (x) => x && x.d === reference_doctype && x.n === reference_docname,
    )
  }

  function toggleMute(reference_doctype, reference_docname) {
    const list = mutedThreads.value || []
    const idx = list.findIndex((x) => x && x.d === reference_doctype && x.n === reference_docname)
    if (idx >= 0) {
      list.splice(idx, 1)
    } else {
      list.push({ d: reference_doctype, n: reference_docname })
    }
    mutedThreads.value = list
  }

  return {
    unreadCommentCount,
    markAllAsRead,
    markAsRead,
    sendQuickReply,
    isMuted,
    toggleMute,
    toggle,
  }
})


