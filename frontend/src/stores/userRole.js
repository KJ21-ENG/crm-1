import { ref, computed } from 'vue'
import { frappeRequest } from 'frappe-ui'

export function useUserRole() {
  const currentUserRole = ref(null)
  const userRoles = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // Check if user is admin based on roles
  const isAdminUser = computed(() => {
    console.log('🔍 DEBUG: isAdminUser computed - userRoles:', userRoles.value)
    
    if (!userRoles.value || userRoles.value.length === 0) {
      console.log('🔍 DEBUG: No user roles available, returning false')
      return false
    }
    
    // Admin roles that have access to all dashboard tabs
    const adminRoles = [
      'Administrator',
      'System Manager',
      'CRM Manager',
      'Dashboard Manager'
    ]
    
    const hasAdminRole = userRoles.value.some(role => adminRoles.includes(role))
    console.log('🔍 DEBUG: Has admin role:', hasAdminRole, 'Roles:', userRoles.value)
    
    return hasAdminRole
  })

  // Get user roles from backend
  const fetchUserRoles = async () => {
    if (isLoading.value) return
    
    isLoading.value = true
    error.value = null
    
    try {
      console.log('🔍 DEBUG: Fetching user roles...')
      
      // Try the new API endpoint first
      try {
        const response = await frappeRequest({
          url: '/api/method/crm.api.dashboard.get_user_roles',
          method: 'GET'
        })
        
        console.log('🔍 DEBUG: Raw response:', response)
        
        if (response.message) {
          userRoles.value = response.message.roles || []
          currentUserRole.value = response.message.primary_role || 'User'
          
          console.log('🔍 DEBUG: User roles fetched successfully:', userRoles.value)
          console.log('🔍 DEBUG: Primary role:', currentUserRole.value)
          console.log('🔍 DEBUG: Is admin user:', isAdminUser.value)
          return
        }
      } catch (apiError) {
        console.log('🔍 DEBUG: API endpoint failed, trying fallback:', apiError.message)
      }
      
      // Fallback: try to get user info from existing dashboard API
      try {
        const dashboardResponse = await frappeRequest({
          url: '/api/method/crm.api.dashboard.get_user_dashboard_data',
          method: 'GET',
          params: { view: 'daily' }
        })
        
        if (dashboardResponse.message && dashboardResponse.message.user_info) {
          // Extract user info from dashboard response
          const userInfo = dashboardResponse.message.user_info
          console.log('🔍 DEBUG: Got user info from dashboard:', userInfo)
          
          // Try to infer roles from user info
          if (userInfo.name === 'Administrator' || userInfo.name === 'admin@example.com') {
            userRoles.value = ['Administrator']
            currentUserRole.value = 'Administrator'
          } else {
            userRoles.value = ['User']
            currentUserRole.value = 'User'
          }
          
          console.log('🔍 DEBUG: Fallback user roles:', userRoles.value)
          return
        }
      } catch (dashboardError) {
        console.log('🔍 DEBUG: Dashboard fallback also failed:', dashboardError.message)
      }
      
      // Final fallback: use session information
      console.log('🔍 DEBUG: Using final fallback - session-based role detection')
      
      // Check if we're logged in as admin by looking at the current user
      // This is a simple heuristic based on common admin usernames
      const currentUser = getCurrentUserFromSession()
      console.log('🔍 DEBUG: Current user from session:', currentUser)
      
      if (currentUser === 'Administrator' || currentUser === 'admin@example.com' || currentUser === 'newadmin@example.com') {
        userRoles.value = ['Administrator']
        currentUserRole.value = 'Administrator'
      } else {
        userRoles.value = ['User']
        currentUserRole.value = 'User'
      }
      
      console.log('🔍 DEBUG: Final fallback user roles:', userRoles.value)
      
    } catch (err) {
      console.error('❌ ERROR: Failed to fetch user roles:', err)
      error.value = err.message || 'Failed to fetch user roles'
      
      // Fallback to default user role
      userRoles.value = ['User']
      currentUserRole.value = 'User'
    } finally {
      isLoading.value = false
    }
  }

  // Helper function to get current user from session
  const getCurrentUserFromSession = () => {
    try {
      // Try to get user from cookies or session storage
      const cookies = document.cookie.split(';').reduce((acc, cookie) => {
        const [key, value] = cookie.trim().split('=')
        acc[key] = value
        return acc
      }, {})
      
      // Look for user_id in cookies
      if (cookies.user_id) {
        return cookies.user_id
      }
      
      // Try to get from localStorage or sessionStorage
      const sessionUser = localStorage.getItem('user_id') || sessionStorage.getItem('user_id')
      if (sessionUser) {
        return sessionUser
      }
      
      // Default fallback
      return 'User'
    } catch (e) {
      console.log('🔍 DEBUG: Error getting user from session:', e)
      return 'User'
    }
  }

  // Initialize user role information
  const initializeUserRole = async () => {
    console.log('🔍 DEBUG: Initializing user role...')
    await fetchUserRoles()
  }

  // Check if user has specific role
  const hasRole = (roleName) => {
    return userRoles.value.includes(roleName)
  }

  // Check if user has any of the specified roles
  const hasAnyRole = (roleNames) => {
    return userRoles.value.some(role => roleNames.includes(role))
  }

  // Check if user has all of the specified roles
  const hasAllRoles = (roleNames) => {
    return roleNames.every(role => userRoles.value.includes(role))
  }

  return {
    // State
    currentUserRole,
    userRoles,
    isLoading,
    error,
    
    // Computed
    isAdminUser,
    
    // Actions
    fetchUserRoles,
    initializeUserRole,
    hasRole,
    hasAnyRole,
    hasAllRoles
  }
}
