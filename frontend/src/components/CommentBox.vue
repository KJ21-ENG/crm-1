<template>
  <TextEditor
    :key="usersKey"
    ref="textEditor"
    :editor-class="['prose-sm max-w-none', editable && 'min-h-[7rem]']"
    :content="content"
    @change="editable ? (content = $event) : null"
    :starterkit-options="{ heading: { levels: [2, 3, 4, 5, 6] } }"
    :placeholder="placeholder"
    :editable="editable"
    :mentions="users"
  >
    <template v-slot:editor="{ editor }">
      <EditorContent
        :class="[
          editable &&
            'sm:mx-10 mx-4 max-h-[50vh] overflow-y-auto border-t py-3',
        ]"
        :editor="editor"
      />
    </template>
    <template v-slot:bottom>
      <div v-if="editable" class="flex flex-col gap-2">
        <div class="flex flex-wrap gap-2 sm:px-10 px-4">
          <AttachmentItem
            v-for="a in attachments"
            :key="a.file_url"
            :label="a.file_name"
          >
            <template #suffix>
              <FeatherIcon
                class="h-3.5"
                name="x"
                @click.stop="removeAttachment(a)"
              />
            </template>
          </AttachmentItem>
        </div>
        <div
          class="flex justify-between gap-2 overflow-hidden border-t sm:px-10 px-4 py-2.5"
        >
          <div class="flex gap-1 items-center overflow-x-auto">
            <TextEditorBubbleMenu :buttons="textEditorMenuButtons" />
            <IconPicker
              v-model="emoji"
              v-slot="{ togglePopover }"
              @update:modelValue="() => appendEmoji()"
            >
              <Button variant="ghost" @click="togglePopover()">
                <template #icon>
                  <SmileIcon class="h-4" />
                </template>
              </Button>
            </IconPicker>
            <FileUploader
              :upload-args="{
                doctype: doctype,
                docname: modelValue.value?.name,
                private: true,
              }"
              @success="(f) => attachments.push(f)"
            >
              <template #default="{ openFileSelector }">
                <Button
                  theme="gray"
                  variant="ghost"
                  @click="openFileSelector()"
                >
                  <template #icon>
                    <AttachmentIcon class="h-4" />
                  </template>
                </Button>
              </template>
            </FileUploader>
          </div>
          <div class="mt-2 flex items-center justify-end space-x-2 sm:mt-0">
            <Button v-bind="discardButtonProps || {}" :label="__('Discard')" />
            <Button
              variant="solid"
              v-bind="submitButtonProps || {}"
              :label="__('Comment')"
            />
          </div>
        </div>
      </div>
    </template>
  </TextEditor>
</template>
<script setup>
import IconPicker from '@/components/IconPicker.vue'
import SmileIcon from '@/components/Icons/SmileIcon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import AttachmentItem from '@/components/AttachmentItem.vue'
import { usersStore } from '@/stores/users'
import { TextEditorBubbleMenu, TextEditor, FileUploader, call } from 'frappe-ui'
import { capture } from '@/telemetry'
import { EditorContent } from '@tiptap/vue-3'
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  placeholder: {
    type: String,
    default: null,
  },
  editable: {
    type: Boolean,
    default: true,
  },
  doctype: {
    type: String,
    default: 'CRM Lead',
  },
  editorProps: {
    type: Object,
    default: () => ({}),
  },
  submitButtonProps: {
    type: Object,
    default: () => ({}),
  },
  discardButtonProps: {
    type: Object,
    default: () => ({}),
  },
})

const modelValue = defineModel()
const attachments = defineModel('attachments')
const content = defineModel('content')

const usersStoreInstance = usersStore()
const usersList = usersStoreInstance.users

const textEditor = ref(null)
const emoji = ref('')

// Assigned mention users state: null = loading/not fetched, [] = no assigns, [..] = mapped users
const assignedMentionUsers = ref(null)

const editor = computed(() => {
  return textEditor.value.editor
})

function appendEmoji() {
  editor.value.commands.insertContent(emoji.value)
  editor.value.commands.focus()
  emoji.value = ''
  capture('emoji_inserted_in_comment', { emoji: emoji.value })
}

function removeAttachment(attachment) {
  attachments.value = attachments.value.filter((a) => a !== attachment)
}

const users = computed(() => {
  // If assignedMentionUsers has been fetched, return it (even if empty)
  if (assignedMentionUsers.value !== null) {
    return assignedMentionUsers.value
  }

  // Otherwise, still loading / not fetched: return empty list (no fallback)
  return []
})

const usersKey = computed(() => {
  return users.value.map((u) => u.value).join(',') || 'all-users'
})

onMounted(() => {
  // Always print mount-time debug info so we can see what modelValue contains
  // eslint-disable-next-line no-console
  console.info('[CommentBox] mounted modelValue:', modelValue)
  // eslint-disable-next-line no-console
  console.info('[CommentBox] usersList resource:', usersList)
  // Kick off loading of assignedMentionUsers if _assign exists
  // Trigger initial compute via the watcher below by doing nothing here.
})

// Recompute assignedMentionUsers whenever the modelValue or usersList changes
watch(
  [() => modelValue.value, () => usersList?.loading, () => usersList?.data],
  async () => {
    try {
      let rawAssign = modelValue.value?._assign
      let parentAssign = rawAssign ? (Array.isArray(rawAssign) ? rawAssign : JSON.parse(rawAssign)) : []

      // If frontend doc doesn't include _assign, try fetching it from server
      if ((!parentAssign || !parentAssign.length) && modelValue.value?.name) {
        try {
          const res = await call('frappe.client.get_value', {
            doctype: 'CRM Lead',
            filters: { name: modelValue.value.name },
            fieldname: '_assign',
          })
          // call() may return the value directly or wrapped in message
          const fetched = res?._assign || res?.message?._assign || (res?.message && res.message._assign)
          if (fetched) {
            rawAssign = fetched
            parentAssign = Array.isArray(fetched) ? fetched : JSON.parse(fetched)
          }
        } catch (err) {
          // eslint-disable-next-line no-console
          console.warn('[CommentBox] failed to fetch _assign via API', err)
        }
      }

      if (parentAssign && parentAssign.length) {
        // wait until usersList is available
        let attempts = 0
        while ((!usersList || usersList.loading || !usersList.data) && attempts < 20) {
          await new Promise((r) => setTimeout(r, 100))
          attempts++
        }

        const mapped = parentAssign
          .map((id) => {
            try {
              return usersStoreInstance.getUser(id)
            } catch (e) {
              return null
            }
          })
          .filter((u) => u && (u.enabled === undefined || u.enabled))
          .map((user) => ({ label: (user.full_name || user.name || '').toString().trim(), value: user.name }))

        assignedMentionUsers.value = mapped
        // eslint-disable-next-line no-console
        console.info('[CommentBox] assignedMentionUsers set:', mapped.map((m) => m.value))
      } else {
        // no parentAssign -> allow crmUsers fallback
        const crmUsersArr = usersList?.data?.crmUsers || []
        const fallback = crmUsersArr
          .filter((u) => u.enabled)
          .map((user) => ({ label: (user.full_name || user.name || '').toString().trim(), value: user.name }))
        assignedMentionUsers.value = fallback
        // eslint-disable-next-line no-console
        console.info('[CommentBox] no parentAssign, assignedMentionUsers fallback set:', fallback.map((f) => f.value))
      }
    } catch (e) {
      assignedMentionUsers.value = []
      // eslint-disable-next-line no-console
      console.error('[CommentBox] error computing assignedMentionUsers', e)
    }
  },
  { immediate: true },
)

defineExpose({ editor })

const textEditorMenuButtons = [
  'Paragraph',
  ['Heading 2', 'Heading 3', 'Heading 4', 'Heading 5', 'Heading 6'],
  'Separator',
  'Bold',
  'Italic',
  'Separator',
  'Bullet List',
  'Numbered List',
  'Separator',
  'Align Left',
  'Align Center',
  'Align Right',
  'FontColor',
  'Separator',
  'Image',
  'Video',
  'Link',
  'Blockquote',
  'Code',
  'Horizontal Rule',
  [
    'InsertTable',
    'AddColumnBefore',
    'AddColumnAfter',
    'DeleteColumn',
    'AddRowBefore',
    'AddRowAfter',
    'DeleteRow',
    'MergeCells',
    'SplitCell',
    'ToggleHeaderColumn',
    'ToggleHeaderRow',
    'ToggleHeaderCell',
    'DeleteTable',
  ],
]
</script>
