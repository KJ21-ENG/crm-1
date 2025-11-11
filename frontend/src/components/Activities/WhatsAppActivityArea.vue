<!-- WhatsApp Activity Area Component -->
<template>
  <div :id="activity.name" class="mb-4">
    <div class="mb-1 flex items-center justify-stretch gap-2 py-1 text-base">
      <div class="inline-flex items-center flex-wrap gap-1 text-ink-gray-5">
        <UserAvatar class="mr-1" :user="activity.owner" size="md" />
        <span class="font-medium text-ink-gray-8">
          {{ activity.owner_name }}
        </span>
        <span>{{ __('sent') }}</span>
        <span class="max-w-xs truncate font-medium text-ink-gray-8">
          {{ activity.data.support_page }}
        </span>
        <span>{{ __('via WhatsApp to') }}</span>
        <span class="font-medium text-ink-gray-8">
          {{ activity.data.customer_phone }}
        </span>
      </div>
      <div class="ml-auto whitespace-nowrap">
        <Tooltip :text="formatDate(activity.creation)">
          <div class="text-sm text-ink-gray-5">
            {{ __(timeAgo(activity.creation)) }}
          </div>
        </Tooltip>
      </div>
    </div>
    <div class="cursor-pointer rounded bg-surface-gray-1 px-3 py-[7.5px] text-base leading-6 transition-all duration-300 ease-in-out">
      <div class="flex items-center gap-2">
        <WhatsAppIcon class="h-5 w-5 text-green-600" />
        <div class="flex-1">
          <div class="font-medium">{{ activity.data.title }}</div>
          <div class="mt-1 text-sm text-gray-500">
            <span class="font-medium">Sent by:</span> {{ activity.data.sent_by }}
          </div>
          <div v-if="activity.data.error" class="text-sm text-red-600">
            {{ activity.data.error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import UserAvatar from '@/components/UserAvatar.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import { Tooltip } from 'frappe-ui'
import { timeAgo, formatDate } from '@/utils'

const props = defineProps({
  activity: {
    type: Object,
    required: true
  }
})
</script> 