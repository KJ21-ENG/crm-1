<template>
  <Dialog
    v-model="show"
    :options="{
      title: __('Assign to Role'),
      size: 'xl',
      actions: [
        {
          label: __('Cancel'),
          variant: 'subtle',
          onClick: () => {
            selectedRole = ''
            show = false
          },
        },
        {
          label: __('Assign'),
          variant: 'solid',
          loading: isAssigning,
          onClick: () => assignToRole(),
        },
      ],
    }"
    @close="
      () => {
        selectedRole = ''
      }
    "
  >
    <template #body-content>
      <div class="space-y-4">
        <!-- Role Selection -->
        <div>
          <label class="block text-sm font-medium text-ink-gray-9 mb-2">
            {{ __('Select Role for Assignment') }}
          </label>
          <select 
            v-model="selectedRole"
            class="form-control w-full"
            :disabled="isAssigning"
          >
            <option value="">{{ __('Choose a role...') }}</option>
            <option 
              v-for="role in availableRoles.data" 
              :key="role.role" 
              :value="role.role"
              :disabled="!role.enabled"
            >
              {{ role.role }} ({{ role.user_count }} {{ __('users') }})
            </option>
          </select>
        </div>

        <!-- Preview Next Assignment -->
        <div v-if="selectedRole && nextAssignment.data && nextAssignment.data.success" class="mt-4 p-3 bg-ink-gray-1 rounded-lg border">
          <div class="flex items-center gap-3">
            <div class="flex-shrink-0">
              <UserAvatar :user="nextAssignment.data.next_user" size="sm" />
            </div>
            <div>
              <p class="text-sm font-medium text-ink-gray-9">
                {{ __('Will be assigned to: {0}', [nextAssignment.data.next_user]) }}
              </p>
              <p class="text-xs text-ink-gray-6">
                {{ __('Position {0} of {1} in round-robin cycle', [nextAssignment.data.current_position + 1, nextAssignment.data.total_users]) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Role Status Information -->
        <div v-if="selectedRole && roleStatus.data && roleStatus.data.success" class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <h4 class="text-sm font-medium text-blue-900 mb-2">{{ __('Role Assignment Status') }}</h4>
          <div class="text-xs text-blue-700 space-y-1">
            <p>{{ __('Total Users: {0}', [roleStatus.data.data.total_users]) }}</p>
            <p v-if="roleStatus.data.data.last_assigned_user">
              {{ __('Last Assigned: {0}', [roleStatus.data.data.last_assigned_user]) }}
            </p>
            <p v-if="roleStatus.data.data.last_assigned_on">
              {{ __('Last Assigned On: {0}', [formatDate(roleStatus.data.data.last_assigned_on)]) }}
            </p>
            <p>{{ __('Total Assignments: {0}', [roleStatus.data.data.assignment_count]) }}</p>
          </div>
        </div>

        <!-- Task Assignment Info -->
        <div v-if="selectedRole" class="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
          <div class="flex items-center gap-2">
            <FeatherIcon name="info" class="h-4 w-4 text-green-600" />
            <p class="text-sm text-green-800">
              {{ __('A user from "{0}" role will be automatically selected using round-robin logic', [selectedRole]) }}
            </p>
          </div>
          <p class="text-xs text-green-600 mt-1">
            {{ __('Task assignment will work with the selected user') }}
          </p>
        </div>

        <ErrorMessage class="mt-2" v-if="error" :message="__(error)" />
        
        <!-- Success Message -->
        <div v-if="successMessage" class="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p class="text-sm text-green-800">{{ successMessage }}</p>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import UserAvatar from '@/components/UserAvatar.vue'
import { usersStore } from '@/stores/users'
import { createResource, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { formatDate } from '@/utils'

const props = defineProps({
  doc: {
    type: Object,
    default: null,
  },
  doctype: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'assigned'])

const { getUser } = usersStore()

const show = defineModel()
const selectedRole = ref('')
const isAssigning = ref(false)
const error = ref('')
const successMessage = ref('')

// Get available roles for assignment
const availableRoles = createResource({
  url: 'crm.api.role_assignment.get_assignable_roles',
  auto: true,
})

// Preview next assignment when role is selected
const nextAssignment = createResource({
  url: 'crm.api.role_assignment.preview_next_assignment',
  makeParams: () => ({ role_name: selectedRole.value }),
  auto: false,
})

// Get role status information
const roleStatus = createResource({
  url: 'crm.api.role_assignment.get_role_assignment_status',
  makeParams: () => ({ role_name: selectedRole.value }),
  auto: false,
})

// Watch for role selection changes
watch(selectedRole, (newRole) => {
  error.value = ''
  if (newRole) {
    nextAssignment.fetch()
    roleStatus.fetch()
  }
})

async function assignToRole() {
  if (!selectedRole.value) {
    error.value = __('Please select a role')
    return
  }

  isAssigning.value = true
  error.value = ''

  try {
    const result = await call('crm.api.role_assignment.assign_to_role', {
      lead_name: props.doc.name,
      role_name: selectedRole.value,
      assigned_by: null // Will use current user
    })

    if (result.success) {
      // Emit success event with new response structure
      emit('assigned', {
        assigned_user: result.assigned_user,
        assigned_role: result.role,
        user_full_name: result.assigned_user, // Use email as fallback
        message: result.message,
        task_created: result.task_created
      })

      // Show success message
      successMessage.value = result.message || `Successfully assigned to ${result.assigned_user}`
      
      // Close modal after delay
      setTimeout(() => {
        emit('close')
      }, 1500)
    } else {
      error.value = result.error || 'Assignment failed'
    }

  } catch (err) {
    error.value = err.message || __('Failed to assign to role')
  } finally {
    isAssigning.value = false
  }
}
</script> 