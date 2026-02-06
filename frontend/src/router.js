import { createRouter, createWebHistory } from 'vue-router'
import { userResource } from '@/stores/user'
import { sessionStore } from '@/stores/session'
import { viewsStore } from '@/stores/views'
import { permissionsStore } from '@/stores/permissions'

const routes = [
  {
    path: '/',
    name: 'Home',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  // Notifications route removed from sidebar; keep commented out to disable navigation
  // {
  //   path: '/notifications',
  //   name: 'Notifications',
  //   component: () => import('@/pages/MobileNotification.vue'),
  // },
  {
    alias: '/tickets',
    path: '/tickets/view/:viewType?',
    name: 'Tickets',
    component: () => import('@/pages/Tickets.vue'),
  },
  {
    path: '/tickets/:ticketId',
    name: 'Ticket',
    component: () => import(`@/pages/${handleMobileView('Ticket')}.vue`),
    props: true,
  },
  {
    alias: '/leads',
    path: '/leads/view/:viewType?',
    name: 'Leads',
    component: () => import('@/pages/Leads.vue'),
  },
  {
    path: '/leads/:leadId',
    name: 'Lead',
    component: () => import(`@/pages/${handleMobileView('Lead')}.vue`),
    props: true,
  },
  // Commented out - Deal module not in use
  // {
  //   alias: '/deals',
  //   path: '/deals/view/:viewType?',
  //   name: 'Deals',
  //   component: () => import('@/pages/Deals.vue'),
  // },
  // {
  //   path: '/deals/:dealId',
  //   name: 'Deal',
  //   component: () => import(`@/pages/${handleMobileView('Deal')}.vue`),
  //   props: true,
  // },
  {
    alias: '/notes',
    path: '/notes/view/:viewType?',
    name: 'Notes',
    component: () => import('@/pages/Notes.vue'),
  },
  {
    alias: '/tasks',
    path: '/tasks/view/:viewType?',
    name: 'Tasks',
    component: () => import('@/pages/Tasks.vue'),
  },
  {
    alias: '/requests',
    path: '/requests/view/:viewType?',
    name: 'Requests',
    component: () => import('@/pages/Requests.vue'),
  },
  // Commented out - Contacts module not in use
  // {
  //   alias: '/contacts',
  //   path: '/contacts/view/:viewType?',
  //   name: 'Contacts',
  //   component: () => import('@/pages/Contacts.vue'),
  // },
  // {
  //   path: '/contacts/:contactId',
  //   name: 'Contact',
  //   component: () => import(`@/pages/${handleMobileView('Contact')}.vue`),
  //   props: true,
  // },
  {
    alias: '/customers',
    path: '/customers/view/:viewType?',
    name: 'Customers',
    component: () => import('@/pages/Customers.vue'),
  },
  {
    path: '/customers/:customerId',
    name: 'Customer',
    component: () => import(`@/pages/${handleMobileView('Customer')}.vue`),
    props: true,
  },
  // Commented out - Organizations module not in use
  // {
  //   alias: '/organizations',
  //   path: '/organizations/view/:viewType?',
  //   name: 'Organizations',
  //   component: () => import('@/pages/Organizations.vue'),
  // },
  {
    alias: '/support-pages',
    path: '/support-pages/view/:viewType?',
    name: 'Support Pages',
    component: () => import('@/pages/SupportPages.vue'),
  },
  // {
  //   path: '/organizations/:organizationId',
  //   name: 'Organization',
  //   component: () => import(`@/pages/${handleMobileView('Organization')}.vue`),
  //   props: true,
  // },
  {
    alias: '/call-logs',
    path: '/call-logs/view/:viewType?',
    name: 'Call Logs',
    component: () => import('@/pages/CallLogs.vue'),
  },
  {
    path: '/round-robin',
    name: 'Round Robin',
    component: () => import('@/pages/RoundRobinManager.vue'),
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: () => import('@/pages/Welcome.vue'),
  },
  {
    path: '/docs',
    name: 'Documentation',
    component: () => import('@/pages/Documentation.vue'),
  },
  {
    path: '/not-permitted',
    name: 'Not Permitted',
    component: () => import('@/pages/NotPermitted.vue'),
  },
  {
    path: '/:invalidpath',
    name: 'Invalid Page',
    component: () => import('@/pages/InvalidPage.vue'),
  },
]

const handleMobileView = (componentName) => {
  return window.innerWidth < 768 ? `Mobile${componentName}` : componentName
}

let router = createRouter({
  history: createWebHistory('/crm'),
  routes,
})

// Auto-reload once if a route's dynamically imported chunk fails to load
// (common after a deploy or asset cache corruption). This prevents the UI
// from becoming non-interactive due to unresolved async components.
function shouldReloadForError(err) {
  if (!err) return false
  const message = String(err && (err.message || err))
  return (
    /Failed to fetch dynamically imported module/i.test(message) ||
    /Loading chunk (\d+|[A-Za-z0-9_-]+) failed/i.test(message) ||
    /Importing a module script failed/i.test(message) ||
    /ChunkLoadError/i.test(message)
  )
}

router.onError((err) => {
  try {
    const alreadyReloaded = sessionStorage.getItem('crm_router_chunk_reload') === '1'
    if (!alreadyReloaded && shouldReloadForError(err)) {
      sessionStorage.setItem('crm_router_chunk_reload', '1')
      window.location.reload()
    }
  } catch (_) {
    // Fallback: if sessionStorage is inaccessible just reload once
    if (shouldReloadForError(err)) {
      window.location.reload()
    }
  }
})

router.beforeEach(async (to, from, next) => {
  const { isLoggedIn } = sessionStore()

  isLoggedIn && (await userResource.promise)
  const pstore = permissionsStore()
  isLoggedIn && (await pstore.permissions.promise)

  if (to.name === 'Home' && isLoggedIn) {
    const { views, getDefaultView } = viewsStore()
    await views.promise

    let defaultView = getDefaultView()
    if (!defaultView) {
      next({ name: 'Leads' })
      return
    }

    let { route_name, type, name, is_standard } = defaultView
    route_name = route_name || 'Leads'

    if (name && !is_standard) {
      next({ name: route_name, params: { viewType: type }, query: { view: name } })
    } else {
      next({ name: route_name, params: { viewType: type } })
    }
  } else if (!isLoggedIn) {
    window.location.href = '/login?redirect-to=/crm'
  } else if (to.matched.length === 0) {
    next({ name: 'Invalid Page' })
  } else {
    // Module-level guard
    const routeName = to.name
    const routeToModule = {
      'Dashboard': 'Dashboard',
      'Tickets': 'Tickets',
      'Ticket': 'Tickets',
      'Leads': 'Leads',
      'Lead': 'Leads',
      'Customers': 'Customers',
      'Customer': 'Customers',
      'Support Pages': 'Support Pages',
      'Notes': 'Notes',
      'Tasks': 'Tasks',
      'Call Logs': 'Call Logs',
    }
    const mod = routeToModule[routeName]
    if (mod && !pstore.canRead(mod)) {
      next({ name: 'Not Permitted', query: { module: mod } })
      return
    }
  }
  if (['Lead'].includes(to.name) && !to.hash) {
    let storageKey = 'lastLeadTab'
    const activeTab = localStorage.getItem(storageKey) || 'activity'
    const hash = '#' + activeTab
    next({ ...to, hash })
  } else {
    next()
  }
})

// Update document title based on current route
router.afterEach((to) => {
  let title = 'Frappe CRM'

  // Build dynamic title based on route and view parameters
  const routeTitles = {
    'Home': 'CRM',
    'Dashboard': 'Dashboard',
    'Tickets': 'Tickets',
    'Ticket': 'Ticket',
    'Leads': 'Leads',
    'Lead': 'Lead',
    'Customers': 'Customers',
    'Customer': 'Customer',
    'Support Pages': 'Support Pages',
    'Notes': 'Notes',
    'Tasks': 'Tasks',
    'Call Logs': 'Call Logs',
    'Round Robin': 'Round Robin',
    'Welcome': 'Welcome',
    'Not Permitted': 'Access Denied',
    'Invalid Page': 'Page Not Found'
  }

  const baseTitle = routeTitles[to.name] || 'CRM'

  // Check if there's a view parameter to append view type
  if (to.params.viewType && to.params.viewType !== 'list') {
    const viewTypeMap = {
      'kanban': 'Kanban',
      'group_by': 'Group By',
      'calendar': 'Calendar'
    }
    const viewType = viewTypeMap[to.params.viewType] || to.params.viewType
    title = `${baseTitle} - ${viewType} - CRM`
  } else if (to.query.view) {
    // If there's a specific view name, use it
    title = `${baseTitle} - ${to.query.view} - CRM`
  } else {
    // Default format
    title = `${baseTitle} - CRM`
  }

  document.title = title
})

export default router
