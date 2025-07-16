<template>
  <component
    v-if="assignees?.length"
    :is="assignees?.length == 1 ? 'Button' : 'div'"
  >
    <MultipleAvatar :avatars="assignees" @click="showRoleAssignmentModal = true" />
  </component>
  <Button v-else @click="showRoleAssignmentModal = true">
    {{ __('Assign to Role') }}
  </Button>
  <RoleAssignmentModal
    v-if="showRoleAssignmentModal"
    v-model="showRoleAssignmentModal"
    :doctype="doctype"
    :doc="data"
    @assigned="handleRoleAssignment"
  />
</template>
<script setup>
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import RoleAssignmentModal from '@/components/Modals/RoleAssignmentModal.vue'
import { usersStore } from '@/stores/users'
import { ref } from 'vue'

const props = defineProps({
  data: Object,
  doctype: String,
})

const { getUser } = usersStore()

const showRoleAssignmentModal = ref(false)
const assignees = defineModel()

function handleRoleAssignment(assignmentData) {
  // Update assignees list with the newly assigned user
  const user = getUser(assignmentData.assigned_user)
  const newAssignee = {
    name: assignmentData.assigned_user,
    image: user?.user_image,
    label: user?.full_name || assignmentData.assigned_user, // Fallback to email if full_name not available
  }
  
  // Update assignees to show the assigned user
  assignees.value = [newAssignee]
}
</script>
