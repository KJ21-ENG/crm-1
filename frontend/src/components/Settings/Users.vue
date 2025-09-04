<template>
  <div class="flex h-full flex-col gap-6 p-6 text-ink-gray-8">
    <!-- Header -->
    <div class="flex justify-between px-2 pt-2">
      <div class="flex flex-col gap-1 w-9/12">
        <h2 class="flex gap-2 text-xl font-semibold leading-none h-5">
          {{ __('Users') }}
        </h2>
        <p class="text-p-base text-ink-gray-6">
          {{
            __(
              'Manage CRM users by adding or inviting them, and assign roles to control their access and permissions',
            )
          }}
        </p>
      </div>
      <div class="flex item-center space-x-2 w-3/12 justify-end">
        <Dropdown
          :options="[
            {
              label: __('Add Existing User'),
              onClick: () => (showAddExistingModal = true),
            },
            {
              label: __('Invite New User'),
              onClick: () => (activeSettingsPage = 'Invite User'),
            },
          ]"
          :button="{
            label: __('New'),
            iconLeft: 'plus',
            variant: 'solid',
          }"
          placement="right"
        />
      </div>
    </div>

    <!-- loading state -->
    <div v-if="users.loading" class="flex mt-28 justify-between w-full h-full">
      <Button
        :loading="users.loading"
        variant="ghost"
        class="w-full"
        size="2xl"
      />
    </div>

    <!-- Empty State -->
    <div
      v-if="!users.loading && users.data?.crmUsers?.length == 1"
      class="flex justify-between w-full h-full"
    >
      <div
        class="text-ink-gray-4 border border-dashed rounded w-full flex items-center justify-center"
      >
        {{ __('No users found') }}
      </div>
    </div>

    <!-- Users List -->
    <div
      class="flex flex-col overflow-hidden"
      v-if="!users.loading && users.data?.crmUsers?.length > 1"
    >
      <div
        v-if="users.data?.crmUsers?.length > 10"
        class="flex items-center justify-between mb-4 px-2 pt-0.5"
      >
        <TextInput
          ref="searchRef"
          v-model="search"
          :placeholder="__('Search user')"
          class="w-1/3"
          :debounce="300"
        >
          <template #prefix>
            <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-6" />
          </template>
        </TextInput>
        <FormControl
          type="select"
          v-model="currentRole"
          :options="roleFilterOptions"
        />
      </div>
      <ul class="divide-y divide-outline-gray-modals overflow-y-auto px-2">
        <template v-for="user in usersList" :key="user.name">
          <li class="flex items-center justify-between py-2">
            <div class="flex items-center">
              <Avatar
                :image="user.user_image"
                :label="user.full_name"
                size="xl"
              />
              <div class="flex flex-col gap-1 ml-3">
                <div class="flex items-center text-base text-ink-gray-8 h-4">
                  {{ user.full_name }}
                </div>
                <div class="text-base text-ink-gray-5">
                  {{ user.name }}
                </div>
              </div>
            </div>
            <div class="flex gap-2 items-center flex-row-reverse">
              <Dropdown
                :options="getMoreOptions(user)"
                :button="{
                  icon: 'more-horizontal',
                  onblur: (e) => {
                    e.stopPropagation()
                    confirmRemove = false
                  },
                }"
                placement="right"
              />
              <div v-if="!isAdmin()">
                <Button :label="(roleMap[user.role] || user.role)" :icon-left="
                  user.role === 'System Manager'
                    ? 'shield'
                    : user.role === 'Sales Manager'
                      ? 'briefcase'
                      : user.role === 'Support User'
                        ? 'headphones'
                        : 'user-check'
                " />
              </div>
              <Dropdown
                v-else
                :options="getDropdownOptions(user)"
                :button="{
                  label: (roleMap[user.role] || user.role),
                  iconRight: 'chevron-down',
                  iconLeft:
                    user.role === 'System Manager'
                      ? 'shield'
                      : user.role === 'Sales Manager'
                        ? 'briefcase'
                        : user.role === 'Support Manager'
                          ? 'headphones'
                        : user.role === 'Support User'
                          ? 'headphones'
                        : 'user-check',
                }"
                placement="right"
              />
            </div>
          </li>
        </template>
        <!-- Load More Button -->
        <div
          v-if="!users.loading && users.hasNextPage"
          class="flex justify-center"
        >
          <Button
            class="mt-3.5 p-2"
            @click="() => users.next()"
            :loading="users.loading"
            :label="__('Load More')"
            icon-left="refresh-cw"
          />
        </div>
      </ul>
    </div>
  </div>
  <AddExistingUserModal
    v-if="showAddExistingModal"
    v-model="showAddExistingModal"
  />
</template>

<script setup>
import AddExistingUserModal from '@/components/Modals/AddExistingUserModal.vue'
import { activeSettingsPage } from '@/composables/settings'
import { usersStore } from '@/stores/users'
import { TemplateOption, DropdownOption } from '@/utils'
import { Avatar, TextInput, toast, call, FeatherIcon, Tooltip, createListResource, FormControl } from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'

const { users, isAdmin, isManager } = usersStore()

const showAddExistingModal = ref(false)
const searchRef = ref(null)
const search = ref('')
const currentRole = ref('All')

const enabledRoles = createListResource({
  doctype: 'Role',
  fields: ['name'],
  filters: { disabled: 0 },
  orderBy: 'name asc',
  auto: true,
})

const roleMap = {
  'System Manager': __('Admin'),
  'Sales Manager': __('Sales Manager'),
  'Support Manager': __('Support Manager'),
  'Sales User': __('Sales User'),
  'Support User': __('Support User'),
}

const roleFilterOptions = computed(() => [{ label: __('All'), value: 'All' }].concat((enabledRoles.data || []).map(r => ({ label: __(r.name), value: r.name }))))

const usersList = computed(() => {
  let filteredUsers = users.data?.crmUsers || []

  return filteredUsers
    .filter(
      (user) =>
        user.name?.includes(search.value) ||
        user.full_name?.includes(search.value),
    )
    .filter((user) => {
      if (currentRole.value === 'All') return true
      return user.role === currentRole.value
    })
})

const confirmRemove = ref(false)

function getMoreOptions(user) {
  let options = [
    {
      label: __('Remove'),
      component: (props) =>
        TemplateOption({
          option: __('Remove'),
          icon: 'trash-2',
          active: props.active,
          onClick: (e) => {
            e.preventDefault()
            e.stopPropagation()
            confirmRemove.value = true
          },
        }),
      condition: () => !confirmRemove.value,
    },
    {
      label: __('Confirm Remove'),
      component: (props) =>
        TemplateOption({
          option: __('Confirm Remove'),
          icon: 'trash-2',
          active: props.active,
          theme: 'danger',
          onClick: () => removeUser(user, true),
        }),
      condition: () => confirmRemove.value,
    },
  ]

  return options.filter((option) => option.condition?.() || true)
}

function roleIcon(roleName) {
  if (roleName === 'System Manager') return 'shield'
  if (roleName === 'Sales Manager') return 'briefcase'
  if (roleName === 'Support Manager') return 'headphones'
  if (roleName === 'Sales User') return 'user-check'
  if (roleName === 'Support User') return 'headphones'
  return 'user'
}

function getDropdownOptions(user) {
  const roles = enabledRoles.data || []
  const options = roles.map((r) => {
    const roleName = r.name
    const condition = () => {
      if (roleName === 'System Manager') return isAdmin()
      if (roleName === 'Sales Manager' || roleName === 'Support Manager') return isManager()
      return true
    }

    return {
      label: __(roleName),
      component: (props) =>
        DropdownOption({
          option: __(roleName),
          icon: roleIcon(roleName),
          active: props.active,
          selected: user.role === roleName,
          onClick: () => updateRole(user, roleName),
        }),
      condition,
    }
  })

  return options.filter((opt) => opt.condition?.() || true)
}

function updateRole(user, newRole) {
  if (user.role === newRole) return

  call('crm.api.user.update_user_role', {
    user: user.name,
    new_role: newRole,
  }).then(() => {
    toast.success(
      __('{0} has been granted {1} access', [user.full_name, roleMap[newRole]]),
    )
    users.reload()
  })
}

function removeUser(user) {
  call('crm.api.user.remove_user', {
    user: user.name,
  }).then(() => {
    toast.success(__('User {0} has been removed', [user.full_name]))
    users.reload()
  })
}

onMounted(() => {
  if (searchRef.value) {
    searchRef.value.el.focus()
  }
})
</script>
