// Task Filter Utility - Automatically applies today's due date filter
// This file should be imported and used in the Tasks page

import { computed } from 'vue'

/**
 * Creates a default filter for today's tasks
 * @returns {Object} Filter object for today's due date
 */
export function getTodayTaskFilter() {
  const today = new Date()
  const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate())
  const endOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 23, 59, 59)

  return {
    due_date: ['between', [
      startOfDay.toISOString().split('T')[0] + ' 00:00:00', 
      endOfDay.toISOString().split('T')[0] + ' 23:59:59'
    ]]
  }
}

/**
 * Hook to automatically apply today's filter when Tasks page loads
 * @param {Object} viewControls - Reference to the ViewControls component
 * @param {Object} tasks - Reference to the tasks data
 */
export function useTodayTaskFilter(viewControls, tasks) {
  const applyTodayFilter = () => {
    if (!viewControls.value) {
      console.log('🔍 ViewControls not available yet')
      return
    }
    
    // Wait for the component to be fully loaded and data to be available
    setTimeout(() => {
      const todayFilter = getTodayTaskFilter()
      
      // Apply the filter through the ViewControls component's updateFilter method
      if (viewControls.value.updateFilter) {
        console.log('🔍 Applying today filter:', todayFilter)
        viewControls.value.updateFilter(todayFilter)
      } else {
        console.log('🔍 updateFilter method not found, trying alternative approach')
        // Alternative approach: directly set the filters
        if (viewControls.value.list && viewControls.value.list.params) {
          viewControls.value.list.params.filters = todayFilter
          viewControls.value.list.reload()
        }
      }
    }, 500) // Increased delay to ensure component is fully loaded
  }

  const applyFilterWithRetry = (maxRetries = 5) => {
    let retryCount = 0
    
    const tryApply = () => {
      if (!viewControls.value) {
        if (retryCount < maxRetries) {
          retryCount++
          console.log(`🔍 Retry ${retryCount}: ViewControls not ready, retrying...`)
          setTimeout(tryApply, 200)
        }
        return
      }
      
      const todayFilter = getTodayTaskFilter()
      console.log('🔍 Applying today filter:', todayFilter)
      
      if (viewControls.value.updateFilter) {
        viewControls.value.updateFilter(todayFilter)
      } else {
        console.log('🔍 updateFilter method not found')
      }
    }
    
    tryApply()
  }

  return {
    applyTodayFilter,
    applyFilterWithRetry
  }
}

/**
 * Computed property for today's filter
 */
export const todayTaskFilter = computed(() => getTodayTaskFilter()) 