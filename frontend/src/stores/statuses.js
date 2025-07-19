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
          capture('status_changed', { doctype, status })
          if (document) {
            await triggerOnChange?.('status', statusesByName[status]?.name)
            document.save.submit()
          }
        },
      })
    }
    return options
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
