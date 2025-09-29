<template>
  <LayoutHeader v-if="lead.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <CustomActions
        v-if="lead.data._customActions?.length"
        :actions="lead.data._customActions"
      />
      <CustomActions
        v-if="document.actions?.length"
        :actions="document.actions"
      />
      <AssignTo
        v-if="canWriteLeads"
        v-model="assignees.data"
        :data="document.doc"
        doctype="CRM Lead"
        @navigateToActivity="navigateToActivity"
      />
      <Dropdown
        v-if="document.doc && canWriteLeads"
        :options="
          statusOptions(
            'lead',
            document,
            lead.data._customStatuses,
            handleStatusChange,
          )
        "
      >
        <template #default="{ open }">
          <Button :label="document.doc.status">
            <template #prefix>
              <IndicatorIcon
                :class="getLeadStatus(document.doc.status).color"
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
      <!-- Commented out Test Lead Expire button per request -->
      <!-- <Button
        :label="__('Test Lead Expire')"
        variant="outline"
        :loading="testExpireLoading"
        @click="handleTestLeadExpire"
      /> -->
      <!-- <Button
        v-if="document.doc"
        :label="__('Auto Assign')"
        variant="outline"
        :loading="autoAssignLoading"
        @click="triggerAutoAssign"
      >
        <template #prefix>
          <FeatherIcon name="refresh-cw" class="h-4" />
        </template>
      </Button> -->
      <!-- <Button
        :label="__('Convert to Deal')"
        variant="solid"
        @click="showConvertToDealModal = true"
      /> -->
    </template>
  </LayoutHeader>
  <div v-if="lead?.data" class="flex h-full overflow-hidden">
    <Tabs as="div" v-model="tabIndex" :tabs="tabs">
      <template #tab-panel>
        <Activities
          ref="activities"
          doctype="CRM Lead"
          :tabs="tabs"
          v-model:reload="reload"
          v-model:tabIndex="tabIndex"
          v-model="lead"
          :canWrite="canWriteLeads"
          @afterSave="reloadAssignees"
        />
      </template>
    </Tabs>
    <Resizer class="flex flex-col justify-between border-l" side="right">
      <div
        class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
        @click="copyToClipboard(lead.data.name)"
      >
        {{ lead.data.name }}
      </div>
      <FileUploader
        v-if="canWriteLeads"
        @success="(file) => updateCustomerImage(file.file_url)"
        :validateFile="validateIsImageFile"
      >
        <template #default="{ openFileSelector, error }">
          <div class="flex items-center justify-start gap-5 border-b p-5">
            <div class="group relative size-12">
              <Avatar
                size="3xl"
                class="size-12"
                :label="title"
                :image="customerData.data?.image || lead.data.image"
              />
              <component
                :is="lead.data.image ? Dropdown : 'div'"
                v-bind="
                  lead.data.image
                    ? {
                        options: [
                          {
                            icon: 'upload',
                            label: lead.data.image
                              ? __('Change image')
                              : __('Upload image'),
                            onClick: openFileSelector,
                          },
                          {
                            icon: 'trash-2',
                            label: __('Remove image'),
                            onClick: () => updateCustomerImage(''),
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
              <Tooltip :text="lead.data.lead_name || __('Set first name')">
                <div class="truncate text-2xl font-medium text-ink-gray-9">
                  {{ title }}
                </div>
              </Tooltip>
              <div class="flex gap-1.5">
                <Tooltip v-if="callEnabled" :text="__('Make a call')">
                  <div>
                    <Button
                      @click="
                        () =>
                          lead.data.mobile_no
                            ? makeCall(lead.data.mobile_no)
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
                        lead.data.email
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
                <Tooltip :text="__('Go to website')">
                  <div>
                    <Button
                      @click="
                        lead.data.website
                          ? openWebsite(lead.data.website)
                          : toast.error(__('No website set'))
                      "
                    >
                      <template #icon>
                        <LinkIcon />
                      </template>
                    </Button>
                  </div>
                </Tooltip>
                <Tooltip v-if="canWriteLeads" :text="__('Attach a file')">
                  <div>
                    <Button @click="showFilesUploader = true">
                      <template #icon>
                        <AttachmentIcon />
                      </template>
                    </Button>
                  </div>
                </Tooltip>
                <Tooltip v-if="canWriteLeads" :text="__('Delete')">
                  <div>
                    <Button
                      @click="deleteLeadWithModal(lead.data.name)"
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
      <SLASection
        v-if="lead.data.sla_status"
        v-model="lead.data"
        @updateField="updateField"
      />
      <div
        v-if="sections.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <SidePanelLayout
          :sections="sections.data"
          doctype="CRM Lead"
          :docname="lead.data.name"
          :documentData="lead.data"
          @reload="sections.reload"
          @afterFieldChange="reloadAssignees"
        />
      </div>
    </Resizer>
  </div>
  <ErrorPage
    v-else-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />
  <!-- Commented out - Deal module not in use -->
  <!-- <Dialog
    v-model="showConvertToDealModal"
    :options="{
      size: 'xl',
      actions: [
        {
          label: __('Convert'),
          variant: 'solid',
          onClick: convertToDeal,
        },
      ],
    }"
  >
    <template #body-header>
      <div class="mb-6 flex items-center justify-between">
        <div>
          <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
            {{ __('Convert to Deal') }}
          </h3>
        </div>
        <div class="flex items-center gap-1">
          <Button
            v-if="isManager() && !isMobileView"
            variant="ghost"
            class="w-7"
            @click="openQuickEntryModal"
          >
            <template #icon>
              <EditIcon class="h-4 w-4" />
            </template>
          </Button>
          <Button
            variant="ghost"
            class="w-7"
            @click="showConvertToDealModal = false"
          >
            <template #icon>
              <FeatherIcon name="x" class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </div>
    </template>
    <template #body-content>
      <div class="mb-4 flex items-center gap-2 text-ink-gray-5">
        <OrganizationsIcon class="h-4 w-4" />
        <label class="block text-base">{{ __('Organization') }}</label>
      </div>
      <div class="ml-6 text-ink-gray-9">
        <div class="flex items-center justify-between text-base">
          <div>{{ __('Choose Existing') }}</div>
          <Switch v-model="existingOrganizationChecked" />
        </div>
        <Link
          v-if="existingOrganizationChecked"
          class="form-control mt-2.5"
          size="md"
          :value="existingOrganization"
          doctype="CRM Organization"
          @change="(data) => (existingOrganization = data)"
        />
        <div v-else class="mt-2.5 text-base">
          {{
            __(
              'New organization will be created based on the data in details section',
            )
          }}
        </div>
      </div>

      <div class="mb-4 mt-6 flex items-center gap-2 text-ink-gray-5">
        <ContactsIcon class="h-4 w-4" />
        <label class="block text-base">{{ __('Contact') }}</label>
      </div>
      <div class="ml-6 text-ink-gray-9">
        <div class="flex items-center justify-between text-base">
          <div>{{ __('Choose Existing') }}</div>
          <Switch v-model="existingContactChecked" />
        </div>
        <Link
          v-if="existingContactChecked"
          class="form-control mt-2.5"
          size="md"
          :value="existingContact"
          doctype="Contact"
          @change="(data) => (existingContact = data)"
        />
        <div v-else class="mt-2.5 text-base">
          {{ __("New contact will be created based on the person's details") }}
        </div>
      </div>
    </template>
  </Dialog> -->
  <FilesUploader
    v-if="lead.data?.name"
    v-model="showFilesUploader"
    doctype="CRM Lead"
    :docname="lead.data.name"
    @after="
      () => {
        activities?.all_activities?.reload()
        changeTabTo('attachments')
      }
    "
  />
  <DeleteLinkedDocModal
    v-if="showDeleteLinkedDocModal"
    v-model="showDeleteLinkedDocModal"
    :doctype="'CRM Lead'"
    :docname="props.leadId"
    name="Leads"
  />
  <ClientIdModal
    v-if="showClientIdModal"
    v-model="showClientIdModal"
    :leadId="lead.data.name"
    :targetStatus="pendingStatusChange?.value"
    :onSuccess="handleClientIdSubmit"
  />
  <RejectionReasonModal
    v-if="showRejectionReasonModal"
    v-model="showRejectionReasonModal"
    :leadId="lead.data.name"
    :targetStatus="pendingStatusChange?.value"
    :onSuccess="handleRejectionReasonSubmit"
  />
  

</template>
<script setup>
import ErrorPage from '@/components/ErrorPage.vue'
import Icon from '@/components/Icon.vue'
import Resizer from '@/components/Resizer.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import LinkIcon from '@/components/Icons/LinkIcon.vue'
// Commented out - Organizations and Contacts modules not in use
// import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
// import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Activities from '@/components/Activities/Activities.vue'
import AssignTo from '@/components/AssignTo.vue'
import FilesUploader from '@/components/FilesUploader/FilesUploader.vue'
import Link from '@/components/Controls/Link.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import SLASection from '@/components/SLASection.vue'
import CustomActions from '@/components/CustomActions.vue'
import {
  openWebsite,
  setupCustomizations,
  copyToClipboard,
  validateIsImageFile,
} from '@/utils'
import { showQuickEntryModal, quickEntryProps } from '@/composables/modals'
import { getView } from '@/utils/view'
import { getSettings } from '@/stores/settings'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'
import { globalStore } from '@/stores/global'
import { statusesStore } from '@/stores/statuses'
import { getMeta } from '@/stores/meta'
import { useDocument } from '@/data/document'
import {
  whatsappEnabled,
  whatsappSupportEnabled,
  callEnabled,
  isMobileView,
} from '@/composables/settings'
import { capture } from '@/telemetry'
import {
  createResource,
  FileUploader,
  Dropdown,
  Tooltip,
  Avatar,
  Tabs,
  Switch,
  Breadcrumbs,
  call,
  usePageMeta,
  toast,
} from 'frappe-ui'
import { useOnboarding } from 'frappe-ui/frappe'
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useActiveTabManager } from '@/composables/useActiveTabManager'
import ClientIdModal from '@/components/Modals/ClientIdModal.vue'
import RejectionReasonModal from '@/components/Modals/RejectionReasonModal.vue'
import { permissionsStore } from '@/stores/permissions'


const { brand } = getSettings()
const { user } = sessionStore()
const { isManager, isAdmin } = usersStore()
const { $dialog, $socket, makeCall } = globalStore()
const { statusOptions, getLeadStatus } = statusesStore()
const { doctypeMeta } = getMeta('CRM Lead')

const { updateOnboardingStep } = useOnboarding('frappecrm')

const route = useRoute()
const router = useRouter()

const props = defineProps({
  leadId: {
    type: String,
    required: true,
  },
})

const errorTitle = ref('')
const errorMessage = ref('')
const showDeleteLinkedDocModal = ref(false)

const lead = createResource({
  url: 'crm.fcrm.doctype.crm_lead.api.get_lead',
  params: { name: props.leadId },
  cache: ['lead', props.leadId],
  onSuccess: (data) => {
    errorTitle.value = ''
    errorMessage.value = ''
    setupCustomizations(lead, {
      doc: data,
      $dialog,
      $socket,
      router,
      toast,
      updateField,
      createToast: toast.create,
      deleteDoc: deleteLead,
      resource: { lead, sections },
      call,
    })
  },
  onError: (err) => {
    if (err.messages?.[0]) {
      errorTitle.value = __('Not permitted')
      errorMessage.value = __(err.messages?.[0])
    } else {
      router.push({ name: 'Leads' })
    }
  },
})

onMounted(() => {
  if (lead.data) return
  lead.fetch()
})

// Watch for lead data changes to load customer data
watch(() => lead.data?.customer_id, (customer_id) => {
  if (customer_id) {
    customerData.fetch()
  }
})

const reload = ref(false)
const showFilesUploader = ref(false)
const autoAssignLoading = ref(false)

 // Prevent multiple simultaneous updates

function updateLead(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  if (!Array.isArray(fieldname) && validateRequired(fieldname, value)) return

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'CRM Lead',
      name: props.leadId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      lead.reload()
      reload.value = true
      toast.success(__('Lead updated successfully'))
      callback?.()
    },
    onError: (err) => {
      console.error('Error updating lead:', err)
      
      // Handle TimestampMismatchError by refreshing the document and retrying
      if (err.messages?.[0]?.includes('TimestampMismatchError') || 
          err.messages?.[0]?.includes('timestamp')) {
        console.log('Timestamp error detected, refreshing and retrying...')
        lead.reload()
        
        // Retry the operation after a short delay
        setTimeout(() => {
          createResource({
            url: 'frappe.client.set_value',
            params: {
              doctype: 'CRM Lead',
              name: props.leadId,
              fieldname,
              value,
            },
            auto: true,
            onSuccess: () => {
              lead.reload()
              reload.value = true
              toast.success(__('Lead updated successfully'))
              callback?.()
            },
            onError: (retryErr) => {
              console.error('Retry failed:', retryErr)
              toast.error(__('Failed to update after retry. Please refresh the page and try again.'))
            },
          })
        }, 1000)
      } else {
        toast.error(err.messages?.[0] || __('Error updating lead'))
      }
    },
  })
}

function validateRequired(fieldname, value) {
  let meta = lead.data.fields_meta || {}
  if (meta[fieldname]?.reqd && !value) {
    toast.error(__('{0} is a required field', [meta[fieldname].label]))
    return true
  }
  return false
}

const breadcrumbs = computed(() => {
  let items = [{ label: __('Leads'), route: { name: 'Leads' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'CRM Lead')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Leads',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: title.value,
    route: { name: 'Lead', params: { leadId: lead.data.name } },
  })
  return items
})

const title = computed(() => {
  // Prioritize customer name over lead ID
  if (lead.data?.first_name || lead.data?.last_name) {
    const firstName = lead.data.first_name || ''
    const lastName = lead.data.last_name || ''
    return `${firstName} ${lastName}`.trim() || lead.data.name
  }
  
  // Fallback to lead name if no customer name available
  let t = doctypeMeta['CRM Lead']?.title_field || 'name'
  return lead.data?.[t] || props.leadId
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
      name: 'Emails',
      label: __('Emails'),
      icon: EmailIcon,
    },
    {
      name: 'Comments',
      label: __('Comments'),
      icon: CommentIcon,
    },
    {
      name: 'Calls',
      label: __('Calls'),
      icon: PhoneIcon,
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
      name: 'Attachments',
      label: __('Attachments'),
      icon: AttachmentIcon,
    },
    {
      name: 'WhatsApp',
      label: __('WhatsApp'),
      icon: WhatsAppIcon,
      condition: () => whatsappEnabled.value,
    },
    {
      name: 'WhatsApp Support',
      label: __('WhatsApp Support'),
      icon: WhatsAppIcon,
      condition: () => whatsappSupportEnabled.value,
    },
  ]
  return tabOptions.filter((tab) => (tab.condition ? tab.condition() : true))
})

const { tabIndex, changeTabTo } = useActiveTabManager(tabs, 'lastLeadTab')

watch(tabs, (value) => {
  if (value && route.params.tabName) {
    let index = value.findIndex(
      (tab) => tab.name.toLowerCase() === route.params.tabName.toLowerCase(),
    )
    if (index !== -1) {
      tabIndex.value = index
    }
  }
})

// Load customer data for avatar and details
const customerData = createResource({
  url: 'crm.api.customers.get_customer_data_for_lead',
  params: { lead_name: props.leadId },
  auto: false,
})

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'CRM Lead'],
  params: { doctype: 'CRM Lead' },
  auto: true,
})

async function updateField(name, value, callback) {
  // Normal field update
  updateLead(name, value, () => {
    lead.data[name] = value
    callback?.()
  })
}

async function updateCustomerImage(imageUrl) {
  if (!lead.data?.customer_id) {
    toast.error(__('No customer associated with this lead'))
    return
  }
  
  try {
    await call('crm.api.customers.update_customer_image', {
      customer_id: lead.data.customer_id,
      image: imageUrl
    })
    
    // Reload customer data to show updated image
    customerData.reload()
    toast.success(__('Customer image updated successfully'))
  } catch (error) {
    console.error('Error updating customer image:', error)
    toast.error(error.messages?.[0] || __('Error updating customer image'))
  }
}







// Helper function to handle timestamp errors
function handleTimestampError(error, operation) {
  console.error(`Timestamp error during ${operation}:`, error)
  
  if (error.message?.includes('TimestampMismatchError') || 
      error.message?.includes('timestamp') ||
      error.messages?.[0]?.includes('TimestampMismatchError') ||
      error.messages?.[0]?.includes('timestamp')) {
    
    console.log('Refreshing lead data due to timestamp error...')
    lead.reload()
    
    // Show a more helpful error message
    toast.error(__('Document was modified elsewhere. The page has been refreshed. Please try your action again.'))
    return true // Indicates timestamp error was handled
  }
  return false // Indicates no timestamp error
}

async function deleteLead(name) {
  try {
    // First, validate what's blocking deletion
    const validation = await call('crm.api.doc.validate_deletion', {
      doctype: 'CRM Lead',
      name,
    })
    
    console.log('🔍 Deletion validation:', validation)
    
    if (!validation.can_delete) {
      toast.error(`Cannot delete lead: ${validation.permission_reason}`)
      return
    }
    
    if (!validation.summary.can_proceed) {
      const problematicCount = validation.summary.problematic_count
      const errorLinks = validation.problematic_links.filter(link => link.severity === 'error')
      
      if (errorLinks.length > 0) {
        toast.error(`Cannot delete lead: Found ${errorLinks.length} blocking links: ${errorLinks.map(link => `${link.doctype} ${link.name}`).join(', ')}`)
        return
      }
    }
    
    // Show detailed info about what will be affected
    if (validation.total_linked_docs > 0) {
      const message = `This will affect ${validation.total_linked_docs} linked items. Proceed?`
      if (!confirm(message)) {
        return
      }
    }
    
    // Proceed with deletion
    await call('frappe.client.delete', {
      doctype: 'CRM Lead',
      name,
    })
    toast.success(__('Lead deleted successfully'))
    router.push({ name: 'Leads' })
  } catch (error) {
    console.error('❌ Deletion error:', error)
    toast.error(error.messages?.[0] || error.message || __('Error deleting lead'))
  }
}

async function deleteLeadWithModal(name) {
  showDeleteLinkedDocModal.value = true
}

// Commented out - Deal module not in use
// // Convert to Deal
// const showConvertToDealModal = ref(false)
// const existingContactChecked = ref(false)
// const existingOrganizationChecked = ref(false)

// const existingContact = ref('')
// const existingOrganization = ref('')

const { triggerOnChange, assignees, document } =
  useDocument('CRM Lead', props.leadId)

// Client ID Modal state
const showClientIdModal = ref(false)
const pendingStatusChange = ref(null)
const isUpdating = ref(false)
const testExpireLoading = ref(false)

// Rejection Reason Modal state
const showRejectionReasonModal = ref(false)

// Check if status change requires Client ID
function shouldRequireClientId(status) {
  return ['Account Opened', 'Account Active', 'Account Activated'].includes(status)
}

// Check if status change requires Rejection Reason
function shouldRequireRejectionReason(status) {
  return status === 'Rejected - Follow-up Required'
}

// Handle Client ID submission
async function handleClientIdSubmit() {
  isUpdating.value = true
  
  try {
    // Now proceed with the pending status change using custom API
    if (pendingStatusChange.value) {
      const result = await call('crm.api.lead_operations.update_lead_status_with_client_id', {
        lead_name: props.leadId,
        new_status: pendingStatusChange.value.value,
        client_id: null // Client ID already saved by modal
      })
      
      if (result.success) {
        console.log('✅ Status updated successfully after Client ID submission')
        // Reload the document to reflect changes
        await document.reload()
        await lead.reload()
        toast.success(__('Lead status updated successfully'))
      } else {
        throw new Error(result.message)
      }
    }
  } catch (error) {
    console.error('Error updating status after Client ID submission:', error)
    toast.error(error.message || __('Failed to update lead status'))
  } finally {
    isUpdating.value = false
    pendingStatusChange.value = null
  }
}

// Handle Client ID modal cancellation
function handleClientIdCancel() {
  showClientIdModal.value = false
  pendingStatusChange.value = null
}

// Handle Rejection Reason submission
async function handleRejectionReasonSubmit() {
  isUpdating.value = true
  
  try {
    // Now proceed with the pending status change using custom API
    if (pendingStatusChange.value) {
      const result = await call('crm.api.lead_operations.update_lead_status_with_rejection_reason', {
        lead_name: props.leadId,
        new_status: pendingStatusChange.value.value,
        rejection_reason: null // Rejection reason already saved by modal
      })
      
      if (result.success) {
        console.log('✅ Status updated successfully after Rejection Reason submission')
        // Reload the document to reflect changes
        await document.reload()
        await lead.reload()
        toast.success(__('Lead status updated successfully'))
      } else {
        throw new Error(result.message)
      }
    }
  } catch (error) {
    console.error('Error updating status after Rejection Reason submission:', error)
    toast.error(error.message || __('Failed to update lead status'))
  } finally {
    isUpdating.value = false
    pendingStatusChange.value = null
  }
}

// Handle Rejection Reason modal cancellation
function handleRejectionReasonCancel() {
  showRejectionReasonModal.value = false
  pendingStatusChange.value = null
}

// Custom function to handle status changes with Client ID and Rejection Reason checks
async function handleStatusChange(fieldname, value) {
  if (fieldname === 'status' && !isUpdating.value) {
    const newStatus = value
    const currentStatus = document.doc.status
    
    // Check if the new status requires Client ID
    if (shouldRequireClientId(newStatus) && !document.doc.client_id) {
      // Store the pending status change
      pendingStatusChange.value = { fieldname, value }
      showClientIdModal.value = true
      return
    }
    
    // Check if the new status requires Rejection Reason
    if (shouldRequireRejectionReason(newStatus) && !document.doc.rejection_reason) {
      // Store the pending status change
      pendingStatusChange.value = { fieldname, value }
      showRejectionReasonModal.value = true
      return
    }
    
    // For status changes that require Client ID, use custom API to avoid validation issues
    if (shouldRequireClientId(newStatus)) {
      try {
        const result = await call('crm.api.lead_operations.update_lead_status_with_client_id', {
          lead_name: props.leadId,
          new_status: newStatus,
          client_id: document.doc.client_id
        })
        
        if (result.success) {
          await document.reload()
          await lead.reload()
          toast.success(__('Lead status updated successfully'))
        } else {
          throw new Error(result.message)
        }
        return
      } catch (error) {
        console.error('Error updating status:', error)
        toast.error(error.message || __('Failed to update lead status'))
        return
      }
    }
    
    // For status changes that require Rejection Reason, use custom API to avoid validation issues
    if (shouldRequireRejectionReason(newStatus)) {
      try {
        const result = await call('crm.api.lead_operations.update_lead_status_with_rejection_reason', {
          lead_name: props.leadId,
          new_status: newStatus,
          rejection_reason: document.doc.rejection_reason
        })
        
        if (result.success) {
          await document.reload()
          await lead.reload()
          toast.success(__('Lead status updated successfully'))
        } else {
          throw new Error(result.message)
        }
        return
      } catch (error) {
        console.error('Error updating status:', error)
        toast.error(error.message || __('Failed to update lead status'))
        return
      }
    }
  }
  
  // Call the original triggerOnChange for non-special status changes
  await triggerOnChange(fieldname, value)
}

async function handleTestLeadExpire() {
  testExpireLoading.value = true
  console.debug('[TestLeadExpire] calling crm.api.lead_expiry.daily_mark_expired_leads')
  try {
    const res = await call('crm.api.lead_expiry.daily_mark_expired_leads')
    console.debug('[TestLeadExpire] response:', res)

    // Show success message with counts when available
    if (res && res.success) {
      const msg = `Lead expiry job executed. updated_case1=${res.updated_case1 || 0}, updated_case2=${res.updated_case2 || 0}`
      toast.success(msg)
      await lead.reload()
      await document.reload()
      return
    }

    // If response exists but success=false, show detailed info
    if (res) {
      console.error('[TestLeadExpire] failed response:', res)
      const debugMsg = res.message || res.error || JSON.stringify(res)
      toast.error(debugMsg || __('Failed to execute lead expiry job'))
    } else {
      // No response object
      console.error('[TestLeadExpire] no response returned from API')
      toast.error(__('Failed to execute lead expiry job: no response'))
    }
  } catch (err) {
    // Network / unexpected errors
    console.error('[TestLeadExpire] exception:', err)
    // Try to surface useful properties from the error
    const errMsg = err?.message || err?.response?.data || JSON.stringify(err)
    toast.error(__('Error executing lead expiry job: {0}', [errMsg]))
  } finally {
    testExpireLoading.value = false
  }
}

// Auto assign function to trigger task reassignment
async function triggerAutoAssign() {
  autoAssignLoading.value = true
  let reassignmentSuccess = false
  let parentUpdateSuccess = false
  let exhaustionData = null
  
  try {
    // Step 1: Call task reassignment function and get exhaustion data
    const result = await call('crm.api.task_reassignment.auto_reassign_overdue_tasks')
    reassignmentSuccess = true
    exhaustionData = result.exhaustion_data // Get exhaustion data from response
    console.log('Task reassignment completed successfully', { exhaustionData })
  } catch (error) {
    console.error('Task reassignment error:', error)
    toast.error(__('Task reassignment failed, but will try to update parent documents.'))
  }
  
  try {
    // Step 2: Call parent document update function with exhaustion data
    await call('crm.api.task_reassignment.update_parent_document_assignments', {
      exhaustion_data: exhaustionData
    })
    parentUpdateSuccess = true
    console.log('Parent document update completed successfully')
  } catch (error) {
    console.error('Parent document update error:', error)
    toast.error(__('Parent document update failed.'))
  }
  
  // Reload the lead data to see the changes
  await lead.reload()
  await document.reload()
  
  // Show appropriate success message
  if (reassignmentSuccess && parentUpdateSuccess) {
    toast.success(__('Auto assignment completed successfully!'))
  } else if (parentUpdateSuccess) {
    toast.success(__('Parent document updated successfully!'))
  } else if (reassignmentSuccess) {
    toast.success(__('Task reassignment completed, but parent document update failed.'))
  } else {
    toast.error(__('Auto assignment failed. Please try again.'))
  }
  
  autoAssignLoading.value = false
}

// Commented out - Deal module not in use
// async function convertToDeal() {
//   if (existingContactChecked.value && !existingContact.value) {
//     toast.error(__('Please select an existing contact'))
//     return
//   }

//   if (existingOrganizationChecked.value && !existingOrganization.value) {
//     toast.error(__('Please select an existing organization'))
//     return
//   }

//   if (!existingContactChecked.value && existingContact.value) {
//     existingContact.value = ''
//   }

//   if (!existingOrganizationChecked.value && existingOrganization.value) {
//     existingOrganization.value = ''
//   }

//   await triggerConvertToDeal?.(
//     lead.data,
//     deal,
//     () => (showConvertToDealModal.value = false),
//   )

//   let _deal = await call('crm.fcrm.doctype.crm_lead.crm_lead.convert_to_deal', {
//     lead: lead.data.name,
//     deal,
//     existing_contact: existingContact.value,
//     existing_organization: existingOrganization.value,
//   })

//   if (_deal) {
//     showConvertToDealModal.value = false
//     existingContactChecked.value = false
//     existingOrganizationChecked.value = false
//     existingContact.value = ''
//     existingOrganization.value = ''
//     capture('convert_lead_to_deal')
//     router.push({ name: 'Deal', params: { dealId: _deal } })
//   }
// }

const activities = ref(null)

// Module permissions + per-record assignment gate
const { canWrite } = permissionsStore()
const isAssignedToThisLead = computed(() => {
  try {
    const list = assignees?.data || []
    return Array.isArray(list) && list.some((a) => a?.name === user)
  } catch (e) {
    return false
  }
})
const canWriteLeads = computed(() => isAdmin() || (canWrite('Leads') && isAssignedToThisLead.value))

function openEmailBox() {
  let currentTab = tabs.value[tabIndex.value]
  if (!['Emails', 'Comments', 'Activities'].includes(currentTab.name)) {
    activities.value.changeTabTo('emails')
  }
  nextTick(() => (activities.value.emailBox.show = true))
}

// Commented out - Deal module not in use
// const deal = reactive({})

// const dealStatuses = computed(() => {
//   let statuses = statusOptions('deal')
//   if (!deal.status) {
//     deal.status = statuses[0].value
//   }
//   return statuses
// })

// const dealTabs = createResource({
//   url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
//   cache: ['RequiredFields', 'CRM Deal'],
//   params: { doctype: 'CRM Deal', type: 'Required Fields' },
//   auto: true,
//   transform: (_tabs) => {
//     let hasFields = false
//     let parsedTabs = _tabs?.forEach((tab) => {
//       tab.sections?.forEach((section) => {
//         section.columns?.forEach((column) => {
//           column.fields?.forEach((field) => {
//             hasFields = true
//             if (field.fieldname == 'status') {
//               field.fieldtype = 'Select'
//               field.options = dealStatuses.value
//               field.prefix = getDealStatus(deal.status).color
//             }

//             if (field.fieldtype === 'Table') {
//               deal[field.fieldname] = []
//             }
//           })
//         })
//       })
//     })
//     return hasFields ? parsedTabs : []
//   },
// })

// function openQuickEntryModal() {
//   showQuickEntryModal.value = true
//   quickEntryProps.value = {
//     doctype: 'CRM Deal',
//     onlyRequired: true,
//   }
//   showConvertToDealModal.value = false
// }

function reloadAssignees(data) {
  if (data?.hasOwnProperty('lead_owner')) {
    assignees.reload()
  }
}

// Navigate to activity tab after successful assignment
function navigateToActivity() {
  console.log('Navigating to Activity tab...')
  changeTabTo('Activity')
  // Also try to set the URL hash
  router.push({ ...route, hash: '#activity' })
}
</script>
