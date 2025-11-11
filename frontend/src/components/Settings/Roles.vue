<template>
  <div class="flex h-full flex-col gap-6 p-8 text-ink-gray-8">
    <!-- Header -->
    <div class="flex justify-between px-2 pt-2">
      <div class="flex flex-col gap-1 w-9/12">
        <h2 class="flex gap-2 text-xl font-semibold leading-none h-5">
          {{ __('Roles') }}
        </h2>
        <p class="text-p-base text-ink-gray-6">
          {{ __('Create and manage system roles, desk access, and permissions') }}
        </p>
      </div>
      <div class="flex items-center gap-2 justify-end">
        <TextInput
          v-model.trim="newRoleName"
          :placeholder="__('New role name')"
          class="w-72"
          :debounce="150"
        >
          <template #prefix>
            <FeatherIcon name="user-plus" class="h-4 w-4 text-ink-gray-6" />
          </template>
        </TextInput>
        <Button
          variant="solid"
          :disabled="!canCreate || !newRoleName"
          :loading="creating"
          @click="addRole"
        >
          <template #prefix>
            <FeatherIcon name="plus" class="h-4 w-4" />
          </template>
          {{ __('Add') }}
        </Button>
      </div>
    </div>

    <!-- Search and filters -->
    <div class="flex items-center justify-between mb-2 px-2">
      <TextInput
        v-model="search"
        :placeholder="__('Search roles')"
        class="w-1/3"
        :debounce="200"
      >
        <template #prefix>
          <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-6" />
        </template>
      </TextInput>
      <div class="flex items-center gap-4">
        <FormControl
          type="select"
          v-model="filter"
          :options="[
            { label: __('All'), value: 'all' },
            { label: __('Custom'), value: 'custom' },
            { label: __('Standard'), value: 'standard' },
            { label: __('Enabled'), value: 'enabled' },
            { label: __('Disabled'), value: 'disabled' },
          ]"
        />
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="roles.loading" class="flex mt-20 w-full">
      <Button :loading="roles.loading" variant="ghost" class="w-full" size="2xl" />
    </div>

    <!-- Empty State -->
    <div v-else-if="!filteredRoles.length" class="flex justify-between w-full h-full">
      <div class="text-ink-gray-4 border border-dashed rounded w-full flex items-center justify-center">
        {{ __('No roles found') }}
      </div>
    </div>

    <!-- Roles List with bulk actions and rename -->
    <div v-else class="flex-1 overflow-y-auto px-2">
      <div class="flex items-center justify-between py-2 px-3">
        <div class="flex items-center gap-3">
          <input type="checkbox" :checked="allSelected" @change="toggleSelectAll($event)" />
          <span class="text-sm text-ink-gray-6">{{ __('Select') }}</span>
          <Dropdown :options="bulkOptions" :button="{ label: __('Bulk Actions'), iconLeft: 'tool' }" />
        </div>
        <div class="text-xs text-ink-gray-6">{{ filteredRoles.length }} {{ __('roles') }}</div>
      </div>

      <div class="grid grid-cols-12 py-2 px-3 text-xs font-medium text-ink-gray-6">
        <div class="col-span-1">&nbsp;</div>
        <div class="col-span-4">{{ __('Role') }}</div>
        <div class="col-span-2">{{ __('Desk Access') }}</div>
        <div class="col-span-2">{{ __('Two Factor') }}</div>
        <div class="col-span-2">{{ __('Disabled') }}</div>
        <div class="col-span-1 text-right">{{ __('Actions') }}</div>
      </div>

      <ul class="divide-y divide-outline-gray-modals">
        <li v-for="r in filteredRoles" :key="r.name" class="grid grid-cols-12 items-center py-2 px-3">
          <div class="col-span-1">
            <input type="checkbox" :checked="!!selected[r.name]" @change="(e) => selectRole(r, e)" />
          </div>
          <div class="col-span-4 flex items-center gap-2">
            <div>
              <div class="text-base text-ink-gray-8">{{ r.name }}</div>
              <div class="text-xs text-ink-gray-6">{{ r.home_page || '' }}</div>
            </div>
            <Badge v-if="r.is_custom" :label="__('Custom')" variant="subtle" theme="blue" />
          </div>
          <div class="col-span-2">
            <label class="inline-flex items-center gap-2 cursor-pointer">
              <input type="checkbox" :checked="!!r.desk_access" @change="toggle(r, 'desk_access', $event.target.checked ? 1 : 0)" />
              <span class="text-sm text-ink-gray-7">{{ r.desk_access ? __('On') : __('Off') }}</span>
            </label>
          </div>
          <div class="col-span-2">
            <label class="inline-flex items-center gap-2 cursor-pointer">
              <input type="checkbox" :checked="!!r.two_factor_auth" @change="toggle(r, 'two_factor_auth', $event.target.checked ? 1 : 0)" />
              <span class="text-sm text-ink-gray-7">{{ r.two_factor_auth ? __('On') : __('Off') }}</span>
            </label>
          </div>
          <div class="col-span-2">
            <label class="inline-flex items-center gap-2 cursor-pointer">
              <input type="checkbox" :checked="!!r.disabled" @change="toggle(r, 'disabled', $event.target.checked ? 1 : 0)" />
              <span class="text-sm text-ink-gray-7">{{ r.disabled ? __('Yes') : __('No') }}</span>
            </label>
          </div>
          <div class="col-span-1 flex justify-end gap-2">
            <Button variant="ghost" icon-left="edit-2" @click="openRenameModal(r)" />
            <Tooltip :text="__('Manage module permissions')">
              <div>
                <Button variant="ghost" icon="lock" @click="openPermsModal(r)" />
              </div>
            </Tooltip>
            <Tooltip :text="r.is_custom ? __('Delete Role') : __('Only custom roles can be deleted')">
              <div>
                <Button
                  variant="ghost"
                  icon="trash-2"
                  :disabled="!r.is_custom || deleting[r.name]"
                  :loading="deleting[r.name]"
                  @click="deleteRole(r)"
                />
              </div>
            </Tooltip>
          </div>
        </li>
      </ul>

      <!-- Rename Modal -->
      <Dialog v-model="showRename" :options="{ size: 'sm' }">
        <template #body>
          <div class="p-4">
            <h3 class="text-lg font-semibold">{{ __('Rename Role') }}</h3>
            <FormControl v-model="renameValue" :label="__('New name')" />
            <div class="mt-4 flex justify-end gap-2">
              <Button variant="subtle" @click="showRename = false">{{ __('Cancel') }}</Button>
              <Button variant="solid" :loading="renaming" @click="submitRename">{{ __('Rename') }}</Button>
            </div>
          </div>
        </template>
      </Dialog>

      <!-- Permissions Modal -->
      <Dialog v-model="showPerms" :options="{ size: 'lg' }">
        <template #body>
          <div class="p-4">
            <h3 class="text-lg font-semibold mb-3">{{ __('Module Permissions for {0}', [permsTarget?.name || '']) }}</h3>
            <div class="grid grid-cols-2 gap-3">
              <div v-for="m in modules" :key="m" class="flex items-center justify-between border rounded p-2">
                <div class="text-sm text-ink-gray-8">{{ m }}</div>
                <FormControl type="select" class="w-48" v-model="permsByModule[m]" :options="permOptions" />
              </div>
            </div>
            <div class="mt-4 flex justify-end gap-2">
              <Button variant="subtle" @click="showPerms = false">{{ __('Cancel') }}</Button>
              <Button variant="solid" :loading="savingPerms" @click="savePerms">{{ __('Save') }}</Button>
            </div>
          </div>
        </template>
      </Dialog>
    </div>

    <ErrorMessage class="mt-2" v-if="error" :message="__(error)" />
  </div>
  
</template>

<script setup>
import { ref, computed } from 'vue'
import { createListResource, createResource, call, toast, TextInput, Button, Badge, Tooltip, FeatherIcon, FormControl, ErrorMessage, Dialog, Dropdown } from 'frappe-ui'
import { usersStore } from '@/stores/users'
import { APP_MODULES } from '@/stores/permissions'

const { isAdmin } = usersStore()

const newRoleName = ref('')
const creating = ref(false)
const error = ref('')
const search = ref('')
const filter = ref('enabled')
const deleting = ref({})

const canCreate = computed(() => isAdmin())

const roles = createListResource({
  doctype: 'Role',
  fields: ['name', 'desk_access', 'disabled', 'two_factor_auth', 'is_custom', 'home_page', 'restrict_to_domain'],
  orderBy: 'modified desc',
  pageLength: 1000, // Set high limit to fetch all roles
  cache: 'roles-list',
  initialData: [],
  auto: true,
})

// bulk select state
const selected = ref({})
const allSelected = computed(() => {
  const keys = Object.keys(selected.value)
  if (!filteredRoles.value.length) return false
  return filteredRoles.value.every(r => selected.value[r.name])
})

function selectRole(role, event) {
  selected.value = { ...selected.value, [role.name]: !!event.target.checked }
}

function toggleSelectAll(e) {
  const checked = e.target.checked
  const map = {}
  for (const r of filteredRoles.value) map[r.name] = checked
  selected.value = map
}

const bulkOptions = [
  { label: __('Enable'), onClick: () => bulkSet('disabled', 0) },
  { label: __('Disable'), onClick: () => bulkSet('disabled', 1) },
  { label: __('Delete'), onClick: () => bulkDelete() },
]

async function bulkSet(field, value) {
  const names = Object.keys(selected.value).filter(n => selected.value[n])
  if (!names.length) return toast.error(__('Select roles first'))
  try {
    for (const name of names) {
      await call('frappe.client.set_value', { doctype: 'Role', name, fieldname: field, value })
    }
    toast.success(__('Updated roles'))
    roles.reload()
  } catch (e) {
    toast.error(e?.messages?.[0] || __('Bulk update failed'))
  }
}

async function bulkDelete() {
  const names = Object.keys(selected.value).filter(n => selected.value[n])
  if (!names.length) return toast.error(__('Select roles first'))
  try {
    for (const name of names) {
      // attempt delete; ignore non-custom
      await call('frappe.client.delete', { doctype: 'Role', name })
    }
    toast.success(__('Deleted selected roles'))
    roles.reload()
  } catch (e) {
    toast.error(e?.messages?.[0] || __('Bulk delete failed'))
  }
}

// rename modal state
const showRename = ref(false)
const renameTarget = ref(null)
const renameValue = ref('')
const renaming = ref(false)

function openRenameModal(role) {
  renameTarget.value = role
  renameValue.value = role.name
  showRename.value = true
}

async function submitRename() {
  if (!renameValue.value || !renameTarget.value) return
  renaming.value = true
  try {
    await call('frappe.client.rename_doc', { doctype: 'Role', old_name: renameTarget.value.name, new_name: renameValue.value })
    toast.success(__('Role renamed'))
    roles.reload()
    showRename.value = false
  } catch (e) {
    toast.error(e?.messages?.[0] || __('Rename failed'))
  } finally {
    renaming.value = false
  }
}

const filteredRoles = computed(() => {
  let data = roles.data || []
  if (search.value) {
    const q = search.value.toLowerCase()
    data = data.filter((r) => r.name.toLowerCase().includes(q))
  }
  if (filter.value === 'custom') {
    data = data.filter((r) => !!r.is_custom)
  } else if (filter.value === 'standard') {
    data = data.filter((r) => !r.is_custom)
  } else if (filter.value === 'enabled') {
    data = data.filter((r) => !r.disabled)
  } else if (filter.value === 'disabled') {
    data = data.filter((r) => !!r.disabled)
  }
  // sort by name asc for stable UI
  return [...data].sort((a, b) => a.name.localeCompare(b.name))
})

async function addRole() {
  if (!newRoleName.value) return
  error.value = ''
  creating.value = true
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'Role',
        role_name: newRoleName.value,
        desk_access: 1,
        is_custom: 1,
      },
    })
    toast.success(__('Role {0} created', [newRoleName.value]))
    newRoleName.value = ''
    roles.reload()
  } catch (e) {
    error.value = e?.messages?.[0] || e?.message || __('Failed to create role')
    toast.error(error.value)
  } finally {
    creating.value = false
  }
}

async function toggle(role, field, value) {
  try {
    await call('frappe.client.set_value', {
      doctype: 'Role',
      name: role.name,
      fieldname: field,
      value,
    })
    // Optimistic update
    role[field] = value
  } catch (e) {
    toast.error(e?.messages?.[0] || e?.message || __('Failed to update role'))
    roles.reload()
  }
}

async function deleteRole(role) {
  if (!role.is_custom) return
  deleting.value = { ...deleting.value, [role.name]: true }
  try {
    await call('frappe.client.delete', { doctype: 'Role', name: role.name })
    toast.success(__('Role {0} deleted', [role.name]))
    roles.reload()
  } catch (e) {
    toast.error(e?.messages?.[0] || e?.message || __('Failed to delete role'))
  } finally {
    deleting.value = { ...deleting.value, [role.name]: false }
  }
}

// Permissions modal state and logic
const showPerms = ref(false)
const permsTarget = ref(null)
const savingPerms = ref(false)
const modules = APP_MODULES
const permOptions = [
  { label: __('None'), value: 'None' },
  { label: __('Read'), value: 'Read' },
  { label: __('Read & Write'), value: 'Read & Write' },
]
const permsByModule = ref({})

function openPermsModal(role) {
  permsTarget.value = role
  permsByModule.value = {}
  showPerms.value = true
  // Load current values
  createResource({
    url: 'crm.api.permissions.get_role_module_permissions',
    params: { role: role.name },
    auto: true,
    onSuccess(data) {
      const map = {}
      for (const row of data || []) map[row.module] = row.permission || 'Read & Write'
      // Ensure all modules present
      for (const m of modules) if (!map[m]) map[m] = 'Read & Write'
      permsByModule.value = map
    },
    onError(e) {
      toast.error(e?.messages?.[0] || __('Failed to load permissions'))
    }
  })
}

async function savePerms() {
  if (!permsTarget.value) return
  savingPerms.value = true
  try {
    const payload = modules.map(m => ({ module: m, permission: permsByModule.value[m] || 'Read & Write' }))
    await call('crm.api.permissions.set_role_module_permissions', { role: permsTarget.value.name, permissions: payload })
    toast.success(__('Permissions saved'))
    showPerms.value = false
  } catch (e) {
    toast.error(e?.messages?.[0] || __('Failed to save permissions'))
  } finally {
    savingPerms.value = false
  }
}
</script>

