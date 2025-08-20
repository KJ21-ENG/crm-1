<template>
  <Dialog
    v-model="show"
    :options="dialogOptions"
    @close="
      () => {
        selectedRole = ''
        selectedUser = ''
        assignmentType = 'role'
      }
    "
  >
    <template #body-content>
      <div class="space-y-4">
        <!-- Current Assignments Display (All Users) -->
        <div v-if="currentAssignments.data && currentAssignments.data.length > 0" class="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
          <h4 class="text-sm font-medium text-gray-900 mb-2">{{ __('Current Assignments') }}</h4>
          <div class="space-y-2">
            <div 
              v-for="assignment in currentAssignments.data" 
              :key="assignment.name"
              class="flex items-center gap-3 p-2 bg-white rounded border border-gray-100"
            >
              <div class="flex-shrink-0">
                <UserAvatar :user="assignment.allocated_to" size="sm" />
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">
                  {{ getUser(assignment.allocated_to).full_name }}
                </p>
                <p class="text-xs text-gray-600">
                  {{ __('Assigned on: {0}', [formatDate(assignment.creation)]) }}
                </p>
              </div>
              <div class="flex-shrink-0">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium" 
                      :class="assignment.status === 'Open' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                  {{ assignment.status }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Assignment Type Selection -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-ink-gray-9 mb-2">
            {{ __('Assignment Type') }}
          </label>
          <div class="flex gap-4 flex-wrap">
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="radio" 
                v-model="assignmentType" 
                value="role" 
                class="form-radio"
                :disabled="isAssigning"
              />
              <span class="text-sm">{{ __('Round-Robin Role Assignment') }}</span>
              <Popover trigger="hover" placement="top">
                <template #target>
                  <FeatherIcon name="info" class="w-4 h-4 text-ink-gray-6 cursor-help" />
                </template>
                <template #body-main>
                  <div class="p-2 text-xs leading-4 max-w-xs">
                    <template v-for="r in debugRoles" :key="r.role + '-dbg'">
                      <div class="font-medium">{{ r.role }} ({{ r.user_count }})</div>
                      <div class="ml-2 text-ink-gray-7">
                        <template v-if="Array.isArray(r.user_names) && r.user_names.length">
                          <ul class="list-disc ml-4">
                            <li v-for="n in r.user_names" :key="r.role + n">{{ n }}</li>
                          </ul>
                        </template>
                        <div v-else>{{ __('No users') }}</div>
                      </div>
                      <div class="h-2" />
                    </template>
                  </div>
                </template>
              </Popover>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="radio" 
                v-model="assignmentType" 
                value="user" 
                class="form-radio"
                :disabled="isAssigning || !isAdmin"
              />
              <span class="text-sm">{{ __('Direct Employee Assignment') }}</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="radio" 
                v-model="assignmentType" 
                value="request" 
                class="form-radio"
                :disabled="isAssigning"
              />
              <span class="text-sm">{{ __('Request specific employee (admin approval)') }}</span>
            </label>
          </div>
        </div>

        <!-- Role Selection -->
        <div v-if="assignmentType === 'role'">
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
              v-for="role in filteredRoles" 
              :key="role.role" 
              :value="role.role"
              :disabled="!role.enabled"
            >
              {{ role.role }}
            </option>
          </select>

          <!-- Debug list moved to tooltip -->

          <!-- If no roles available to assign -->
          <div v-if="filteredRoles.length === 0" class="mt-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              <p class="text-sm text-yellow-800">
                {{ __('All eligible users from every role are already assigned to this document') }}
              </p>
            </div>
          </div>
          
          <!-- Message when all eligible employees are assigned -->
          <div v-if="selectedRole && allEligibleEmployeesAssigned" class="mt-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              <p class="text-sm text-yellow-800">
                {{ roleAssignmentStatus.data?.message || __('All eligible employees from "{0}" role are already assigned to this lead/ticket', [selectedRole]) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Direct User Selection / Request Selection -->
        <div v-if="assignmentType === 'user' || assignmentType === 'request'">
          <label class="block text-sm font-medium text-ink-gray-9 mb-2">
            {{ assignmentType === 'user' ? __('Select Employee for Direct Assignment') : __('Select Employee to Request') }}
          </label>
          <select 
            v-model="selectedUser"
            class="form-control w-full"
            :disabled="isAssigning"
          >
            <option value="">{{ __('Choose an employee...') }}</option>
            <option 
              v-for="user in availableUsersRequestList" 
              :key="user.name" 
              :value="user.name"
              :disabled="!user.enabled"
            >
              {{ user.full_name }} ({{ user.name }}) - {{ user.role }}
            </option>
          </select>
          <div v-if="assignmentType === 'request'" class="mt-2">
            <label class="block text-sm font-medium text-ink-gray-9 mb-1">{{ __('Reason (optional)') }}</label>
            <textarea v-model="requestReason" class="form-control w-full" rows="3" :placeholder="__('Add a note for admin...')" />
            <div class="text-xs text-amber-600 mt-1">
              {{ __('This will send a request to admins. It will be assigned only after approval.') }}
            </div>
          </div>
          
          <!-- Message when no available users for direct assignment -->
          <div v-if="assignmentType === 'user' && availableUsersForDirectAssignment.length === 0" class="mt-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              <p class="text-sm text-yellow-800">
                {{ __('All employees are already assigned to this lead/ticket') }}
              </p>
            </div>
          </div>
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
import { createResource, call, Tooltip, FeatherIcon, Popover } from 'frappe-ui'
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

const { getUser, isAdmin } = usersStore()

const show = defineModel()
const selectedRole = ref('')
const selectedUser = ref('')
const assignmentType = ref('role')
const isAssigning = ref(false)
const error = ref('')
const successMessage = ref('')
const requestReason = ref('')
const dialogOptions = computed(() => ({
  title: __('Assign to Role') + (props.doctype === 'CRM Ticket' ? ' (Ticket)' : ' (Lead)'),
  size: 'xl',
  actions: [
    {
      label: __('Cancel'),
      variant: 'subtle',
      onClick: () => {
        selectedRole.value = ''
        selectedUser.value = ''
        assignmentType.value = 'role'
        show.value = false
      },
    },
    assignmentType.value === 'request'
      ? {
          label: __('Request'),
          variant: 'solid',
          loading: isAssigning.value,
          onClick: () => assignToRole(),
        }
      : {
          label: __('Assign'),
          variant: 'solid',
          loading: isAssigning.value,
          onClick: () => assignToRole(),
        },
  ],
}))

// Get available roles for assignment (now includes user_names for debugging)
const availableRoles = createResource({
  url: 'crm.api.role_assignment.get_assignable_roles',
  auto: true,
})

// Get available users for direct assignment (Admin Only)
const availableUsers = createResource({
  url: 'crm.api.role_assignment.get_assignable_users',
  auto: false,
})

// Preview next assignment when role is selected
const nextAssignment = createResource({
  url: 'crm.api.role_assignment.preview_next_assignment',
  makeParams: () => ({ role_name: selectedRole.value }),
  auto: false,
})

// Get current assignments for the lead/ticket
const currentAssignments = createResource({
  url: 'crm.api.role_assignment.get_current_assignments',
  makeParams: () => ({ 
    doc_name: props.doc.name,
    doctype: props.doctype 
  }),
  auto: true,
})

// Check if all eligible users for a role have been assigned to this document
const roleAssignmentStatus = createResource({
  url: 'crm.api.role_assignment.check_all_role_users_assigned',
  makeParams: () => ({ 
    role_name: selectedRole.value,
    doc_name: props.doc.name,
    doctype: props.doctype 
  }),
  auto: false,
})

  // Track per-role "all assigned" status for filtering round-robin roles
  const rolesStatus = ref({})

  const filteredRoles = computed(() => {
    const roles = availableRoles.data || []
    const disallowed = new Set(['CRM User', 'CRM Manager'])
    return roles
      .filter((r) => r.enabled)
      .filter((r) => !disallowed.has(r.role))
  })

const debugRoles = computed(() => (availableRoles.data || []).map(r => ({
  role: r.role,
  user_count: r.user_count || 0,
  user_names: Array.isArray(r.user_names) ? r.user_names : [],
})))

// Computed property to get available users for direct assignment (filtered by current assignments)
const availableUsersForDirectAssignment = computed(() => {
  if (!availableUsers.data) return []
  const currentAssignedUsers = currentAssignments.data?.map(a => a.allocated_to) || []
  const cu = getUser()
  const currentIdentifiers = new Set([cu?.name, cu?.email].filter(Boolean))
  return availableUsers.data
    .filter(user => !currentAssignedUsers.includes(user.name))
    // Exclude current user by matching either by user.name (usually email) or email
    .filter(user => !currentIdentifiers.has(user.name) && !currentIdentifiers.has(user.email))
})

// Public list for request flow (no admin restriction)
const publicAssignableUsers = createResource({
  url: 'crm.api.assignment_requests.get_assignable_users_public',
  auto: true,
})
const availableUsersRequestList = computed(() => {
  if (assignmentType.value === 'user') return availableUsersForDirectAssignment.value
  const data = publicAssignableUsers.data || []
  const currentAssignedUsers = currentAssignments.data?.map(a => a.allocated_to) || []
  return data.filter(u => !currentAssignedUsers.includes(u.name))
})

// Computed property to check if all eligible employees for the selected role are already assigned
const allEligibleEmployeesAssigned = computed(() => {
  if (!selectedRole.value || !roleAssignmentStatus.data) return false
  return roleAssignmentStatus.data.all_assigned || false
})

// Watch for assignment type changes
watch(assignmentType, (newType) => {
  error.value = ''
  // Clear selected data when switching types
  selectedRole.value = ''
  selectedUser.value = ''
  
  if (newType === 'user' && isAdmin) {
    availableUsers.fetch()
  }
  if (newType === 'request') {
    publicAssignableUsers.fetch()
  }
})

// Watch for role selection changes
watch(selectedRole, (newRole) => {
  error.value = ''
  if (newRole) {
    nextAssignment.fetch()
    roleAssignmentStatus.fetch()
  }
})

// When current assignments or roles load, pre-compute roles with all users already assigned (batch API)
watch([() => availableRoles.data, () => currentAssignments.data], async ([roles]) => {
  if (!roles || !Array.isArray(roles)) return
  try {
    const res = await call('crm.api.role_assignment.get_roles_all_assigned_status', {
      roles: roles.map(r => r.role),
      doc_name: props.doc.name,
      doctype: props.doctype,
    })
    rolesStatus.value = res?.status || {}
  } catch (e) {
    rolesStatus.value = {}
  }
})

// Watch for user selection changes
watch(selectedUser, (newUser) => {
  error.value = ''
})

async function assignToRole() {
  if (assignmentType.value === 'role' && !selectedRole.value) {
    error.value = __('Please select a role')
    return
  }
  
  if (assignmentType.value === 'user' && !selectedUser.value) {
    error.value = __('Please select an employee')
    return
  }

  // Check if all eligible users are assigned for round-robin
  if (assignmentType.value === 'role' && allEligibleEmployeesAssigned.value) {
    error.value = __('All eligible employees from this role have already been assigned to this lead/ticket')
    return
  }

  isAssigning.value = true
  error.value = ''

  try {
    let result
    
    if (assignmentType.value === 'role') {
      // Role-based assignment
      if (props.doctype === 'CRM Ticket') {
        result = await call('crm.api.ticket.assign_ticket_to_role', {
          ticket_name: props.doc.name,
          role_name: selectedRole.value,
          assigned_by: null, // Will use current user
          skip_task_creation: false // Allow task creation for manual role assignment
        })
      } else {
        // Default to lead assignment
        result = await call('crm.api.role_assignment.assign_to_role', {
          lead_name: props.doc.name,
          role_name: selectedRole.value,
          assigned_by: null // Will use current user
        })
      }
    } else if (assignmentType.value === 'user') {
      // Direct user assignment
      if (props.doctype === 'CRM Ticket') {
        result = await call('crm.api.ticket.assign_ticket_to_user', {
          ticket_name: props.doc.name,
          user_name: selectedUser.value,
          assigned_by: null // Will use current user
        })
      } else {
        // Default to lead assignment
        result = await call('crm.api.role_assignment.assign_to_user', {
          lead_name: props.doc.name,
          user_name: selectedUser.value,
          assigned_by: null // Will use current user
        })
      }
    } else if (assignmentType.value === 'request') {
      // Request admin approval for assignment
      result = await call('crm.api.assignment_requests.create_assignment_request', {
        reference_doctype: props.doctype,
        reference_name: props.doc.name,
        requested_user: selectedUser.value,
        reason: requestReason.value,
      })
      // capture debug response if any
      if (result?.debug) {
        lastRequestDebug.value = result.debug
        console.log('Request debug:', result.debug)
      }
      if (result?.success) {
        successMessage.value = __('Request submitted to admins for approval')
        setTimeout(() => {
          show.value = false
          emit('close')
        }, 800)
        return
      }
    }

    if (result.success) {
      // Emit success event with new response structure
      emit('assigned', {
        assigned_user: result.assigned_user,
        assigned_role: result.role || 'Direct Assignment',
        user_full_name: result.assigned_user, // Use email as fallback
        message: result.message,
        task_created: result.task_created
      })

      // Close modal immediately
      show.value = false
      
      // Emit close event to trigger navigation
      emit('close')
    } else {
      error.value = result.error || 'Assignment failed'
    }

  } catch (err) {
    error.value = err.message || __('Failed to assign')
  } finally {
    isAssigning.value = false
  }
}

// Debug helper: expose lastRequestDebug when creating request
const lastRequestDebug = ref(null)

</script> 