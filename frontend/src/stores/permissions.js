import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

export const APP_MODULES = [
  'Dashboard',
  'Tickets',
  'Leads',
  'Customers',
  'Support Pages',
  'Notes',
  'Tasks',
  'Call Logs',
]

export const permissionsStore = defineStore('crm-permissions', () => {
  const permissions = createResource({
    url: 'crm.api.permissions.get_current_user_module_permissions',
    cache: 'crm-user-module-permissions',
    initialData: {},
    auto: true,
  })

  function level(module) {
    const data = permissions.data || {}
    return data[module] || 'Read & Write'
  }

  function canRead(module) {
    const l = level(module)
    return l === 'Read' || l === 'Read & Write'
  }

  function canWrite(module) {
    return level(module) === 'Read & Write'
  }

  return { permissions, canRead, canWrite, level }
})

