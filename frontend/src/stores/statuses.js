import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import { capture } from '@/telemetry'
import { parseColor } from '@/utils'
import { defineStore } from 'pinia'
import { createListResource } from 'frappe-ui'
import { reactive, h } from 'vue'

export const statusesStore = defineStore('crm-statuses', () => {
  let leadStatusesByName = reactive({})
  let dealStatusesByName = reactive({})
  let ticketStatusesByName = reactive({})
  let communicationStatusesByName = reactive({})

  const leadStatuses = createListResource({
    doctype: 'CRM Lead Status',
    fields: ['name', 'color', 'position'],
    orderBy: 'position asc',
    cache: 'lead-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        status.color = parseColor(status.color)
        leadStatusesByName[status.name] = status
      }
      return statuses
    },
  })

  const dealStatuses = createListResource({
    doctype: 'CRM Deal Status',
    fields: ['name', 'color', 'position'],
    orderBy: 'position asc',
    cache: 'deal-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        status.color = parseColor(status.color)
        dealStatusesByName[status.name] = status
      }
      return statuses
    },
  })

  const ticketStatuses = createListResource({
    doctype: 'CRM Ticket Status',
    fields: ['name', 'color', 'position'],
    orderBy: 'position asc',
    cache: 'ticket-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        status.color = parseColor(status.color)
        ticketStatusesByName[status.name] = status
      }
      return statuses
    },
  })

  const communicationStatuses = createListResource({
    doctype: 'CRM Communication Status',
    fields: ['name'],
    cache: 'communication-statuses',
    initialData: [],
    auto: true,
    transform(statuses) {
      for (let status of statuses) {
        communicationStatusesByName[status.name] = status
      }
      return statuses
    },
  })

  function getLeadStatus(name) {
    if (!name) {
      name = leadStatuses.data[0].name
    }
    return leadStatusesByName[name]
  }

  function getDealStatus(name) {
    if (!name) {
      name = dealStatuses.data[0].name
    }
    return dealStatusesByName[name]
  }

  function getTicketStatus(name) {
    if (!name) {
      name = ticketStatuses.data[0].name
    }
    return ticketStatusesByName[name]
  }

  function getCommunicationStatus(name) {
    if (!name) {
      name = communicationStatuses.data[0].name
    }
    return communicationStatuses[name]
  }

  function statusOptions(
    doctype,
    document,
    statuses = [],
    triggerOnChange = null,
  ) {
    let statusesByName =
      doctype == 'deal' ? dealStatusesByName : 
      doctype == 'ticket' ? ticketStatusesByName : 
      leadStatusesByName

    if (document?.statuses?.length) {
      statuses = document.statuses
    }

    if (statuses?.length) {
      statusesByName = statuses.reduce((acc, status) => {
        acc[status] = statusesByName[status]
        return acc
      }, {})
    }

    let options = []
    for (const status in statusesByName) {
      options.push({
        label: statusesByName[status]?.name,
        value: statusesByName[status]?.name,
        icon: () => h(IndicatorIcon, { class: statusesByName[status]?.color }),
        onClick: async () => {
          const selectedName = statusesByName[status]?.name

          // Prevent applying the same status again for documents that already have it
          if (document && document.doc && document.doc.status === selectedName) {
            try {
              const { toast } = await import('frappe-ui')
              toast.error(`${selectedName} is already the current status`)
            } catch (e) {
              console.error('Failed to show toast for duplicate status', e)
            }
            return
          }

          capture('status_changed', { doctype, status })
          if (document) {
            // Special handling for lead status changes to avoid validation issues
            if (doctype === 'lead') {
              await handleLeadStatusChange(document, statusesByName[status]?.name, triggerOnChange)
            } else {
              // Use original method for other doctypes
              await triggerOnChange?.('status', statusesByName[status]?.name)
              document.save.submit()
            }
          }
        },
      })
    }
    return options
  }

  // Helper function to handle lead status changes with Client ID and Rejection Reason validation
  async function handleLeadStatusChange(document, newStatus, triggerOnChange) {
    try {
      // Check if status requires Client ID
      const requiresClientId = ['Account Opened', 'Account Active', 'Account Activated'].includes(newStatus)
      // Check if status requires Rejection Reason
      const requiresRejectionReason = newStatus === 'Rejected - Follow-up Required'
      
      if (requiresClientId && !document.doc.client_id) {
        // This will trigger the Client ID modal in the Lead.vue component
        // The modal will handle the status change after Client ID is provided
        await triggerOnChange?.('status', newStatus)
        return
      }
      
      if (requiresRejectionReason && !document.doc.rejection_reason) {
        // This will trigger the Rejection Reason modal in the Lead.vue component
        // The modal will handle the status change after Rejection Reason is provided
        await triggerOnChange?.('status', newStatus)
        return
      }
      
      // For status changes that require Client ID, use custom API to avoid validation issues
      if (requiresClientId) {
        const { call } = await import('frappe-ui')
        const result = await call('crm.api.lead_operations.update_lead_status_with_client_id', {
          lead_name: document.doc.name,
          new_status: newStatus,
          client_id: document.doc.client_id
        })
        
        if (result.success) {
          // Reload the document to reflect changes
          await document.reload()
          // Show success message
          const { toast } = await import('frappe-ui')
          toast.success('Lead status updated successfully')
        } else {
          throw new Error(result.message)
        }
      } else if (requiresRejectionReason) {
        // For status changes that require Rejection Reason, use custom API to avoid validation issues
        const { call } = await import('frappe-ui')
        const result = await call('crm.api.lead_operations.update_lead_status_with_rejection_reason', {
          lead_name: document.doc.name,
          new_status: newStatus,
          rejection_reason: document.doc.rejection_reason
        })
        
        if (result.success) {
          // Reload the document to reflect changes
          await document.reload()
          // Show success message
          const { toast } = await import('frappe-ui')
          toast.success('Lead status updated successfully')
        } else {
          throw new Error(result.message)
        }
      } else {
        // Use original method for non-special status changes
        await triggerOnChange?.('status', newStatus)
        document.save.submit()
      }
    } catch (error) {
      console.error('Error updating lead status:', error)
      const { toast } = await import('frappe-ui')
      toast.error(error.message || 'Failed to update lead status')
    }
  }

  return {
    leadStatuses,
    dealStatuses,
    ticketStatuses,
    communicationStatuses,
    getLeadStatus,
    getDealStatus,
    getTicketStatus,
    getCommunicationStatus,
    statusOptions,
  }
})
