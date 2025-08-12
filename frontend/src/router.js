import { createRouter, createWebHistory } from 'vue-router'
import { userResource } from '@/stores/user'
import { sessionStore } from '@/stores/session'
import { viewsStore } from '@/stores/views'

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
    path: '/welcome',
    name: 'Welcome',
    component: () => import('@/pages/Welcome.vue'),
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

router.beforeEach(async (to, from, next) => {
  const { isLoggedIn } = sessionStore()

  isLoggedIn && (await userResource.promise)

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
  } else if (['Lead'].includes(to.name) && !to.hash) {
    let storageKey = 'lastLeadTab'
    const activeTab = localStorage.getItem(storageKey) || 'activity'
    const hash = '#' + activeTab
    next({ ...to, hash })
  } else {
    next()
  }
})

export default router
