<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
    
    <div class="grid grid-cols-2 gap-4">
      <button
        v-for="action in actions"
        :key="action.title"
        @click="handleAction(action)"
        class="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all duration-200 group"
      >
        <div 
          :class="[
            'p-3 rounded-full',
            getActionIconBg(action.color)
          ]"
        >
          <FeatherIcon 
            :name="action.icon" 
            :class="[
              'w-5 h-5',
              getActionIconColor(action.color)
            ]"
          />
        </div>
        
        <div class="flex-1 text-left">
          <p class="font-medium text-gray-900 group-hover:text-gray-700">
            {{ action.title }}
          </p>
          <p class="text-sm text-gray-500">
            Create new {{ action.title.toLowerCase() }}
          </p>
        </div>
        
        <FeatherIcon 
          name="chevron-right" 
          class="w-4 h-4 text-gray-400 group-hover:text-gray-600"
        />
      </button>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  actions: {
    type: Array,
    default: () => []
  }
})

const getActionIconBg = (color) => {
  const colors = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    orange: 'bg-orange-100',
    purple: 'bg-purple-100',
    red: 'bg-red-100',
    yellow: 'bg-yellow-100'
  }
  return colors[color] || colors.blue
}

const getActionIconColor = (color) => {
  const colors = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    purple: 'text-purple-600',
    red: 'text-red-600',
    yellow: 'text-yellow-600'
  }
  return colors[color] || colors.blue
}

const handleAction = (action) => {
  if (action.route) {
    // Navigate to the respective page and trigger the modal
    if (action.route === '/leads/new') {
      router.push({ 
        name: 'Leads',
        query: { showLeadModal: 'true' }
      })
    } else if (action.route === '/tickets/new') {
      router.push({ 
        name: 'Tickets',
        query: { showTicketModal: 'true' }
      })
    } else {
      router.push(action.route)
    }
  }
}
</script> 