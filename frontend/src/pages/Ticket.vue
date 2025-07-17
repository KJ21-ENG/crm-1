<template>
  <LayoutHeader v-if="ticket.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="ticket.data._customActions?.length"
        :actions="ticket.data._customActions"
      />
      <CustomActions
        v-if="document.actions?.length"
        :actions="document.actions"
      />
      <AssignTo
        v-model="assignees.data"
        :data="document.doc"
        doctype="CRM Ticket"
      />
      <Dropdown
        v-if="document.doc"
        :options="
          statusOptions(
            'ticket',
            document,
            ticket.data._customStatuses,
            triggerOnChange,
          )
        "
      >
        <template #default="{ open }">
          <Button :label="document.doc.status">
            <template #prefix>
              <IndicatorIcon
                :class="getTicketStatusColor(document.doc.status)"
              />
            </template>
            <template #suffix>
              <FeatherIcon
                :name="open ? 'chevron-up' : 'chevron-down'"
                class="h-4"
              />
            </template>
          </Button>
        </template>
      </Dropdown>
      <Dropdown
        v-if="document.doc?.status !== 'Closed'"
        :options="[
          {
            label: __('Escalate Ticket'),
            icon: 'arrow-up',
            onClick: () => showEscalateModal = true,
          },
          {
            label: __('Auto Assign'),
            icon: 'user-plus',
            onClick: () => autoAssignTicket(),
          },
          {
            label: __('Department Metrics'),
            icon: 'bar-chart-3',
            onClick: () => showDepartmentMetrics = true,
          },
        ]"
      >
        <template #default="{ open }">
          <Button variant="outline">
            <template #prefix>
              <FeatherIcon name="more-horizontal" class="h-4" />
            </template>
            {{ __('Actions') }}
            <template #suffix>
              <FeatherIcon
                :name="open ? 'chevron-up' : 'chevron-down'"
                class="h-4"
              />
            </template>
          </Button>
        </template>
      </Dropdown>
      <Button
        v-if="document.doc?.status !== 'Closed'"
        :label="__('Close Ticket')"
        variant="solid"
        theme="red"
        @click="showCloseTicketModal = true"
      />
    </template>
  </LayoutHeader>
  <div v-if="ticket?.data" class="flex h-full overflow-hidden">
    <Tabs as="div" v-model="tabIndex" :tabs="tabs">
      <template #tab-panel>
        <Activities
          ref="activities"
          doctype="CRM Ticket"
          :tabs="tabs"
          v-model:reload="reload"
          v-model:tabIndex="tabIndex"
          v-model="ticket"
          @afterSave="reloadAssignees"
        />
      </template>
    </Tabs>
    <Resizer class="flex flex-col justify-between border-l" side="right">
      <div
        class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
        @click="copyToClipboard(ticket.data.name)"
      >
        {{ __(ticket.data.name) }}
      </div>
      
      <!-- Customer Info Section -->
      <FileUploader
        @success="(file) => updateField('image', file.file_url)"
        :validateFile="validateIsImageFile"
      >
        <template #default="{ openFileSelector, error }">
          <div class="flex items-center justify-start gap-5 border-b p-5">
            <div class="group relative size-12">
              <Avatar
                size="3xl"
                class="size-12"
                :label="customerName"
                :image="ticket.data.image"
              />
              <component
                :is="ticket.data.image ? Dropdown : 'div'"
                v-bind="
                  ticket.data.image
                    ? {
                        options: [
                          {
                            icon: 'upload',
                            label: ticket.data.image
                              ? __('Change image')
                              : __('Upload image'),
                            onClick: openFileSelector,
                          },
                          {
                            icon: 'trash-2',
                            label: __('Remove image'),
                            onClick: () => updateField('image', ''),
                          },
                        ],
                      }
                    : { onClick: openFileSelector }
                "
                class="!absolute bottom-0 left-0 right-0"
              >
                <div
                  class="z-1 absolute bottom-0.5 left-0 right-0.5 flex h-9 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-3 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
                  style="
                    -webkit-clip-path: inset(12px 0 0 0);
                    clip-path: inset(12px 0 0 0);
                  "
                >
                  <CameraIcon class="size-4 cursor-pointer text-white" />
                </div>
              </component>
            </div>
            <div class="flex flex-col gap-2.5 truncate">
              <Tooltip :text="ticket.data.ticket_subject || __('Set ticket subject')">
                <div class="truncate text-2xl font-medium text-ink-gray-9">
                  {{ title }}
                </div>
              </Tooltip>
              <div class="text-sm text-ink-gray-7">
                Customer: {{ customerName }}
              </div>
              <div class="flex gap-1.5">
                <Tooltip v-if="callEnabled" :text="__('Make a call')">
                  <div>
                    <Button
                      @click="
                        () =>
                          ticket.data.mobile_no
                            ? makeCall(ticket.data.mobile_no)
                            : toast.error(__('No phone number set'))
                      "
                    >
                      <template #icon>
                        <PhoneIcon />
                      </template>
                    </Button>
                  </div>
                </Tooltip>
                <Tooltip :text="__('Send an email')">
                  <div>
                    <Button
                      @click="
                        ticket.data.email
                          ? openEmailBox()
                          : toast.error(__('No email set'))
                      "
                    >
                      <template #icon>
                        <Email2Icon />
                      </template>
                    </Button>
                  </div>
                </Tooltip>
                <Tooltip v-if="whatsappEnabled" :text="__('Send WhatsApp')">
                  <div>
          <Button
                      @click="
                        ticket.data.mobile_no
                          ? openWhatsApp()
                          : toast.error(__('No phone number set'))
                      "
                    >
                      <template #icon>
                        <WhatsAppIcon />
                      </template>
                    </Button>
                  </div>
                </Tooltip>
                <Tooltip :text="__('Create Task')">
                  <div>
                    <Button @click="showCreateTaskModal = true">
                      <template #icon>
                        <TaskIcon />
                      </template>
                    </Button>
                  </div>
                </Tooltip>
                <Tooltip :text="__('Attach a file')">
                  <div>
                    <Button @click="showFilesUploader = true">
                      <template #icon>
                        <AttachmentIcon />
                      </template>
                    </Button>
                  </div>
                </Tooltip>
                <Tooltip :text="__('Delete')">
                  <div>
          <Button
                      @click="deleteTicketWithModal(ticket.data.name)"
                      variant="subtle"
                      theme="red"
                      icon="trash-2"
                    />
                  </div>
                </Tooltip>
              </div>
              <ErrorMessage :message="__(error)" />
            </div>
        </div>
      </template>
      </FileUploader>

      <!-- SLA Status Section -->
      <SLASection
        v-if="ticket.data.sla_status"
        v-model="ticket.data"
        @updateField="updateField"
      />

      <!-- Support Metrics Section -->
      <div class="border-b p-5">
        <div class="mb-3 text-sm font-medium text-ink-gray-7">
          {{ __('Support Details') }}
        </div>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-ink-gray-6">{{ __('Priority') }}</span>
            <Badge
              :label="ticket.data.priority"
              :variant="'subtle'"
              :theme="getPriorityColor(ticket.data.priority)"
            />
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-ink-gray-6">{{ __('Department') }}</span>
            <span class="text-sm text-ink-gray-8">{{ ticket.data.department || 'Support' }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-ink-gray-6">{{ __('Issue Type') }}</span>
            <span class="text-sm text-ink-gray-8">{{ ticket.data.issue_type || 'General' }}</span>
          </div>
          <div v-if="ticket.data.resolution_time" class="flex items-center justify-between">
            <span class="text-sm font-medium text-ink-gray-6">{{ __('Resolution Time') }}</span>
            <span class="text-sm text-ink-gray-8">{{ formatDuration(ticket.data.resolution_time) }}</span>
          </div>
          <div v-if="ticket.data.first_response_time" class="flex items-center justify-between">
            <span class="text-sm font-medium text-ink-gray-6">{{ __('First Response') }}</span>
            <span class="text-sm text-ink-gray-8">{{ formatDuration(ticket.data.first_response_time) }}</span>
          </div>
        </div>
          </div>



      <!-- Related Items -->
      <div v-if="relatedTickets.data?.length" class="border-b p-5">
        <div class="mb-3 text-sm font-medium text-ink-gray-7">
          {{ __('Related Tickets') }}
        </div>
        <div class="space-y-2">
          <div
            v-for="relatedTicket in relatedTickets.data"
            :key="relatedTicket.name"
            class="flex items-center justify-between rounded bg-ink-gray-1 p-2"
          >
            <div class="flex-1">
              <div class="text-sm font-medium text-ink-gray-9">
                {{ relatedTicket.ticket_subject }}
            </div>
              <div class="text-xs text-ink-gray-6">
                {{ relatedTicket.status }} • {{ formatDate(relatedTicket.creation) }}
            </div>
            </div>
            <Button
              variant="ghost"
                size="sm"
              @click="router.push({ name: 'Ticket', params: { ticketId: relatedTicket.name } })"
            >
              {{ __('View') }}
            </Button>
          </div>
        </div>
      </div>

      <!-- Dynamic Fields Section -->
      <div
        v-if="sections.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <SidePanelLayout
          :sections="sections.data"
          doctype="CRM Ticket"
          :docname="ticket.data.name"
          @reload="sections.reload"
          @afterFieldChange="reloadAssignees"
        />
      </div>
    </Resizer>
  </div>
  <div v-else-if="ticket.loading" class="flex h-full items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
      <div class="text-lg text-ink-gray-6">{{ __('Loading ticket...') }}</div>
    </div>
  </div>
  <ErrorPage
    v-else-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />
  
  <!-- Modals -->
  <Dialog
    v-model="showCloseTicketModal"
    :options="{
      title: __('Close Ticket'),
      size: 'md',
      actions: [
        {
          label: __('Close Ticket'),
          variant: 'solid',
          theme: 'red',
          onClick: closeTicket,
        },
      ],
    }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div>
          <label class="mb-2 block text-sm font-medium text-ink-gray-7">
            {{ __('Resolution') }}
          </label>
          <TextEditor
            v-model="resolutionText"
            :placeholder="__('Describe how the issue was resolved...')"
            editor-class="min-h-32"
          />
        </div>
        <div>
          <label class="mb-2 block text-sm font-medium text-ink-gray-7">
            {{ __('Customer Satisfaction') }}
          </label>
          <Dropdown
            v-model="satisfactionRating"
            :options="[
              { label: __('Very Satisfied'), value: 5 },
              { label: __('Satisfied'), value: 4 },
              { label: __('Neutral'), value: 3 },
              { label: __('Dissatisfied'), value: 2 },
              { label: __('Very Dissatisfied'), value: 1 },
            ]"
            placeholder="Select rating..."
          />
        </div>
      </div>
    </template>
  </Dialog>

  <TaskModal
    v-if="showCreateTaskModal"
    v-model="showCreateTaskModal"
    :defaults="{
      reference_doctype: 'CRM Ticket',
      reference_name: ticket.data?.name,
      assigned_to: ticket.data?.assigned_to,
      title: `Follow-up for ${ticket.data?.ticket_subject}`,
    }"
  />

  <!-- Escalation Modal -->
  <Dialog
    v-model="showEscalateModal"
    :options="{
      title: __('Escalate Ticket'),
      size: 'md',
      actions: [
        {
          label: __('Escalate'),
          variant: 'solid',
          theme: 'orange',
          onClick: escalateTicket,
        },
      ],
    }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div>
          <label class="mb-2 block text-sm font-medium text-ink-gray-7">
            {{ __('Escalation Reason') }}
          </label>
          <TextEditor
            v-model="escalationReason"
            :placeholder="__('Why is this ticket being escalated?')"
            editor-class="min-h-24"
          />
        </div>
        <div>
          <label class="mb-2 block text-sm font-medium text-ink-gray-7">
            {{ __('Escalate To (Optional)') }}
          </label>
          <Dropdown
            v-model="escalateTo"
            :options="managerUsers"
            placeholder="Select manager or leave empty for auto-assignment"
          />
        </div>
        <div class="p-3 bg-orange-50 border border-orange-200 rounded">
          <div class="flex items-center gap-2 text-orange-700">
            <FeatherIcon name="arrow-up" class="h-4 w-4" />
            <span class="font-medium text-sm">{{ __('Escalation Effects') }}</span>
          </div>
          <div class="text-xs text-orange-600 mt-1">
            • Priority will be increased automatically<br>
            • Ticket will be flagged as escalated<br>
            • Managers will be notified<br>
            • SLA timelines will be adjusted
          </div>
        </div>
      </div>
    </template>
  </Dialog>

  <!-- Department Metrics Modal -->
  <Dialog
    v-model="showDepartmentMetrics"
    :options="{
      title: __('Department Metrics'),
      size: 'xl',
    }"
  >
    <template #body-content>
      <div v-if="departmentMetrics.loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
        <div class="text-ink-gray-6">{{ __('Loading metrics...') }}</div>
      </div>
      
      <div v-else-if="departmentMetrics.data" class="space-y-6">
        <!-- Status Distribution -->
        <div>
          <h4 class="font-semibold text-ink-gray-9 mb-3">{{ __('Status Distribution') }}</h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              v-for="status in departmentMetrics.data.status_distribution"
              :key="status.status"
              class="p-3 rounded border text-center"
            >
              <div class="text-2xl font-bold text-ink-gray-9">{{ status.count }}</div>
              <div class="text-sm text-ink-gray-6">{{ status.status }}</div>
            </div>
          </div>
        </div>

        <!-- Priority Distribution -->
        <div>
          <h4 class="font-semibold text-ink-gray-9 mb-3">{{ __('Priority Distribution') }}</h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              v-for="priority in departmentMetrics.data.priority_distribution"
              :key="priority.priority"
              class="p-3 rounded border text-center"
            >
              <div class="text-2xl font-bold" :class="getPriorityTextColor(priority.priority)">
                {{ priority.count }}
              </div>
              <div class="text-sm text-ink-gray-6">{{ priority.priority }}</div>
            </div>
          </div>
        </div>

        <!-- Performance Metrics -->
        <div class="grid md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-semibold text-ink-gray-9 mb-3">{{ __('Escalation Metrics') }}</h4>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-ink-gray-6">Total Escalated:</span>
                <span class="font-medium">{{ departmentMetrics.data.escalation_metrics.total_escalated || 0 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-6">Avg. Escalation Time:</span>
                <span class="font-medium">
                  {{ Math.round(departmentMetrics.data.escalation_metrics.avg_escalation_time_hours || 0) }}h
                </span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 class="font-semibold text-ink-gray-9 mb-3">{{ __('Resolution Metrics') }}</h4>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-ink-gray-6">Total Resolved:</span>
                <span class="font-medium">{{ departmentMetrics.data.resolution_metrics.total_resolved || 0 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-ink-gray-6">Avg. Resolution Time:</span>
                <span class="font-medium">
                  {{ Math.round(departmentMetrics.data.resolution_metrics.avg_resolution_time_hours || 0) }}h
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Dialog>

  <FilesUploader
    v-if="ticket.data?.name"
    v-model="showFilesUploader"
    doctype="CRM Ticket"
    :docname="ticket.data.name"
    @after="
      () => {
        activities?.all_activities?.reload()
        changeTabTo('attachments')
      }
    "
    />
</template>

<script setup>
import ErrorPage from '@/components/ErrorPage.vue'
import Resizer from '@/components/Resizer.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import CustomActions from '@/components/CustomActions.vue'
import AssignTo from '@/components/AssignTo.vue'
import Activities from '@/components/Activities/Activities.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import SLASection from '@/components/SLASection.vue'
import FilesUploader from '@/components/FilesUploader/FilesUploader.vue'
import TaskModal from '@/components/Modals/TaskModal.vue'
import { statusesStore } from '@/stores/statuses'
import { useActiveTabManager } from '@/composables/useActiveTabManager'
import { useDocument } from '@/data/document'
import { whatsappEnabled, whatsappSupportEnabled, callEnabled } from '@/composables/settings'
import { usersStore } from '@/stores/users'
import { globalStore } from '@/stores/global'
import { getSettings } from '@/stores/settings'
import { viewsStore } from '@/stores/views'
import { formatDate, copyToClipboard, validateIsImageFile, timeAgo } from '@/utils'
import { getView } from '@/utils/view'
import { 
  Breadcrumbs, 
  Avatar, 
  Button, 
  Badge, 
  Tabs, 
  FileUploader, 
  TextEditor, 
  ErrorMessage, 
  Tooltip, 
  Dropdown, 
  Dialog, 
  usePageMeta, 
  createResource, 
  call, 
  toast, 
  FeatherIcon 
} from 'frappe-ui'
import { useRoute } from 'vue-router'
import { computed, ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const { getView: getViewFromStore } = viewsStore()
const { brand } = getSettings()
const { makeCall, $dialog } = globalStore()
const { statusOptions } = statusesStore()
const { isManager } = usersStore()

const props = defineProps({
  ticketId: {
    type: String,
    required: true,
  },
})

const route = useRoute()
const router = useRouter()

const showCloseTicketModal = ref(false)
const showCreateTaskModal = ref(false)
const showFilesUploader = ref(false)
const showEscalateModal = ref(false)
const showDepartmentMetrics = ref(false)
const resolutionText = ref('')
const satisfactionRating = ref(null)
const reload = ref(false)
const errorTitle = ref('')
const errorMessage = ref('')
const activities = ref(null)

// Escalation form data
const escalationReason = ref('')
const escalateTo = ref(null)

// Main ticket resource
const ticket = createResource({
  url: 'frappe.client.get',
  params: { 
    doctype: 'CRM Ticket',
    name: props.ticketId
  },
  cache: ['ticket', props.ticketId],
  onSuccess: (data) => {
    console.log('Ticket data loaded:', data)
    errorTitle.value = ''
    errorMessage.value = ''
  },
  onError: (err) => {
    console.error('Error loading ticket:', err)
    if (err.messages?.[0]) {
      errorTitle.value = __('Not permitted')
      errorMessage.value = __(err.messages?.[0])
    } else {
      errorTitle.value = __('Ticket not found')
      errorMessage.value = __('The ticket you are looking for does not exist.')
    }
  },
})

onMounted(() => {
  if (ticket.data) return
  ticket.fetch()
})

const { triggerOnChange, document } = useDocument('CRM Ticket', props.ticketId)

const assignees = createResource({
  url: 'crm.api.doc.get_assigned_users',
  params: { doctype: 'CRM Ticket', name: props.ticketId },
  auto: true,
})

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'CRM Ticket'],
  params: { doctype: 'CRM Ticket' },
  auto: true,
})

// Load related tickets for the same customer
const relatedTickets = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Ticket',
    filters: {
      mobile_no: ticket.data?.mobile_no,
      name: ['!=', props.ticketId]
    },
    fields: ['name', 'ticket_subject', 'status', 'creation'],
    limit: 5,
    order_by: 'creation desc'
  },
  auto: false,
})

// Watch for ticket data changes to load related tickets
watch(() => ticket.data?.mobile_no, (mobile_no) => {
  if (mobile_no) {
    relatedTickets.update({
      params: {
        ...relatedTickets.params,
        filters: {
          mobile_no,
          name: ['!=', props.ticketId]
        }
      }
    })
    relatedTickets.fetch()
  }
})

// Manager users for escalation
const managerUsers = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'User',
    filters: {
      role_profile_name: ['in', ['Support Manager', 'Senior Support']],
      enabled: 1
    },
    fields: ['name', 'full_name'],
    order_by: 'full_name'
  },
  auto: true,
  transform: (data) => {
    return data.map(user => ({
      label: user.full_name,
      value: user.name
    }))
  }
})

// Department metrics resource
const departmentMetrics = createResource({
  url: 'crm.api.ticket.get_department_metrics',
  makeParams: () => ({
    department: ticket.data?.department
  }),
  auto: false
})

const breadcrumbs = computed(() => {
  let items = [{ label: __('Tickets'), route: { name: 'Tickets' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'CRM Ticket')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Tickets',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: title.value,
    route: { name: 'Ticket', params: { ticketId: ticket.data?.name } },
  })
  return items
})

const title = computed(() => {
  return ticket.data?.ticket_subject || ticket.data?.name || props.ticketId
})

const customerName = computed(() => {
  return ticket.data?.first_name || ticket.data?.customer_name || 'Customer'
})

usePageMeta(() => {
  return {
    title: title.value,
    icon: brand.favicon,
  }
})

const tabs = computed(() => {
  let tabOptions = [
    {
      name: 'Activity',
      label: __('Activity'),
      icon: ActivityIcon,
    },
    {
      name: 'WhatsApp Support',
      label: __('WhatsApp Support'),
      icon: WhatsAppIcon,
      condition: () => whatsappSupportEnabled.value,
    },
    {
      name: 'Calls',
      label: __('Calls'),
      icon: PhoneIcon,
    },
    {
      name: 'Attachments',
      label: __('Attachments'),
      icon: AttachmentIcon,
    },
    {
      name: 'Comments',
      label: __('Comments'),
      icon: CommentIcon,
    },
    {
      name: 'Tasks',
      label: __('Tasks'),
      icon: TaskIcon,
    },
    {
      name: 'Notes',
      label: __('Notes'),
      icon: NoteIcon,
    },
    {
      name: 'Data',
      label: __('Data'),
      icon: DetailsIcon,
    },
    // Keep WhatsApp and Emails at the end if needed
    {
      name: 'WhatsApp',
      label: __('WhatsApp'),
      icon: WhatsAppIcon,
      condition: () => whatsappEnabled.value,
    },
    {
      name: 'Emails',
      label: __('Emails'),
      icon: EmailIcon,
    },
  ]
  return tabOptions.filter((tab) => (tab.condition ? tab.condition() : true))
})

const { tabIndex, changeTabTo } = useActiveTabManager(tabs, 'lastTicketTab')

function getTicketStatusColor(status) {
  const colors = {
    'New': 'text-blue-600',
    'Open': 'text-orange-600',
    'In Progress': 'text-yellow-600',
    'Pending Customer': 'text-purple-600',
    'Resolved': 'text-green-600',
    'Closed': 'text-gray-600',
  }
  return colors[status] || 'text-gray-600'
}

function getPriorityColor(priority) {
  const colors = {
    'Low': 'blue',
    'Medium': 'orange',
    'High': 'red',
    'Urgent': 'purple',
  }
  return colors[priority] || 'gray'
}

function formatDuration(seconds) {
  if (!seconds) return 'N/A'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

function reloadAssignees() {
  assignees.reload()
}

async function openEmailBox() {
  let emailId = ticket.data.email
  window.location.href = `mailto:${emailId}`
}

async function openWhatsApp() {
  let mobile = ticket.data.mobile_no
  window.open(`https://wa.me/${mobile}`, '_blank')
}

async function closeTicket() {
  try {
    // Update status first
    await updateField('status', 'Closed')
    
    if (resolutionText.value) {
      await updateField('resolution', resolutionText.value)
    }
    
    if (satisfactionRating.value) {
      await updateField('satisfaction_rating', satisfactionRating.value)
    }
    
    showCloseTicketModal.value = false
    resolutionText.value = ''
    satisfactionRating.value = null
    ticket.reload()
    toast.success(__('Ticket closed successfully'))
  } catch (error) {
    toast.error(__('Error closing ticket'))
  }
}

function deleteTicketWithModal(ticketName) {
  $dialog({
    title: __('Delete Ticket'),
    message: __('Are you sure you want to delete this ticket? This action cannot be undone.'),
    variant: 'solid',
    theme: 'red',
    actions: [
      {
        label: __('Delete'),
        variant: 'solid',
        theme: 'red',
        onClick: async (close) => {
          try {
            await call('frappe.client.delete', {
              doctype: 'CRM Ticket',
              name: ticketName
            })
            toast.success(__('Ticket deleted successfully'))
            router.push({ name: 'Tickets' })
            close()
          } catch (error) {
            toast.error(__('Error deleting ticket'))
          }
        },
      },
    ],
  })
}

function updateTicket(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  if (!Array.isArray(fieldname) && validateRequired(fieldname, value)) return

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'CRM Ticket',
      name: props.ticketId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      ticket.reload()
      reload.value = true
      toast.success(__('Ticket updated successfully'))
      callback?.()
    },
    onError: (err) => {
      toast.error(err.messages?.[0] || __('Error updating ticket'))
    },
  })
}

function validateRequired(fieldname, value) {
  let meta = ticket.data.fields_meta || {}
  if (meta[fieldname]?.reqd && !value) {
    toast.error(__('{0} is a required field', [meta[fieldname].label]))
    return true
  }
  return false
}

function updateField(name, value, callback) {
  updateTicket(name, value, () => {
    ticket.data[name] = value
    callback?.()
  })
}

// Escalation functions
async function escalateTicket() {
  try {
    await call('crm.api.ticket.escalate_ticket', {
      ticket_name: props.ticketId,
      escalation_reason: escalationReason.value,
      escalate_to: escalateTo.value
    })
    
    showEscalateModal.value = false
    escalationReason.value = ''
    escalateTo.value = null
    ticket.reload()
    toast.success(__('Ticket escalated successfully'))
  } catch (error) {
    toast.error(error.messages?.[0] || __('Error escalating ticket'))
  }
}

async function autoAssignTicket() {
  try {
    const result = await call('crm.api.ticket.auto_assign_ticket', {
      ticket_name: props.ticketId
    })
    
    if (result) {
      ticket.reload()
      assignees.reload()
      toast.success(__('Ticket auto-assigned successfully'))
    } else {
      toast.error(__('No suitable agent found for auto-assignment'))
    }
  } catch (error) {
    toast.error(error.messages?.[0] || __('Error auto-assigning ticket'))
  }
}

function getPriorityTextColor(priority) {
  const colors = {
    'Low': 'text-blue-600',
    'Medium': 'text-orange-600', 
    'High': 'text-red-600',
    'Urgent': 'text-purple-600'
  }
  return colors[priority] || 'text-gray-600'
}

watch(showDepartmentMetrics, (show) => {
  if (show && ticket.data?.department) {
    departmentMetrics.reload()
  }
})
</script> 