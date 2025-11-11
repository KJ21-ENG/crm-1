<template>
  <div class="p-6 w-full">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold text-ink-gray-9">{{ __('Backup Status') }}</h2>
      <div class="text-sm text-ink-gray-6 flex items-center gap-2">
        <Button size="sm" :loading="manualBackup.loading" @click="triggerManualBackup" class="flex items-center gap-1">
          <FeatherIcon name="save" class="w-4 h-4" />
          <span>{{ __('Backup Now') }}</span>
        </Button>
        <Button :loading="loading" size="sm" @click="refresh" class="flex items-center">
          <FeatherIcon name="refresh-ccw" class="w-4 h-4 mr-1" />
          {{ __('Refresh') }}
        </Button>
        <div class="font-medium">{{ data?.site || currentHost }}</div>
      </div>
    </div>

    <!-- Warning banner when today's backup missing -->
    <div v-if="!loading && !error && data && !data.today_backup_exists" class="mb-4">
      <Alert variant="warning">
        <div class="flex items-center">
          <FeatherIcon name="alert-triangle" class="w-5 h-5 mr-2" />
          {{ __('No backup found for today. Please take a backup.') }}
        </div>
      </Alert>
    </div>

    <!-- Error state -->
    <div v-if="error" class="mb-4">
      <Alert variant="error">
        <div class="flex items-center">
          <FeatherIcon name="alert-circle" class="w-5 h-5 mr-2" />
          {{ error }}
        </div>
      </Alert>
    </div>

    <!-- Controls -->
    <!-- Controls (directory hidden as requested) -->
    <div class="mb-3"></div>

    <!-- Files table -->
    <div class="rounded border border-gray-200 overflow-hidden">
      <div class="grid grid-cols-12 bg-gray-50 text-xs font-medium text-ink-gray-7 px-3 py-2">
        <div class="col-span-5">{{ __('File') }}</div>
        <div class="col-span-2">{{ __('Type') }}</div>
        <div class="col-span-2">{{ __('Size') }}</div>
        <div class="col-span-2">{{ __('Modified') }}</div>
        <div class="col-span-1">{{ __('Action') }}</div>
      </div>

      <div v-if="loading" class="p-6 text-center text-ink-gray-6 text-sm">
        {{ __('Loading backups...') }}
      </div>

      <div v-else-if="!data?.files?.length" class="p-6 text-center text-ink-gray-6 text-sm">
        {{ __('No backup files found') }}
      </div>

      <div v-else class="divide-y">
        <div
          v-for="file in data.files"
          :key="file.name + file.modified"
          class="grid grid-cols-12 items-center px-3 py-2 text-sm"
        >
          <div class="col-span-5 truncate" :title="file.name">{{ file.name }}</div>
          <div class="col-span-2 uppercase tracking-wide text-xs text-ink-gray-6">{{ formatType(file.type) }}</div>
          <div class="col-span-2 tabular-nums text-ink-gray-7">{{ prettySize(file.size) }}</div>
          <div class="col-span-2 text-ink-gray-7">{{ formatDate(file.modified) }}</div>
          <div class="col-span-1 flex justify-center">
            <Button size="sm" type="button" @click="download(file.name)" class="flex items-center">
              <FeatherIcon name="download" class="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createResource, Alert, Button, FeatherIcon, toast } from 'frappe-ui'
import { computed } from 'vue'

const currentHost = window?.location?.host || 'crm.localhost'

const api = createResource({
  url: 'crm.api.settings.get_backup_status',
  auto: true,
})

const manualBackup = createResource({
  url: 'crm.api.settings.create_manual_backup',
  auto: false,
  makeParams() {
    return {
      include_files: 0,
    }
  },
  onSuccess(res) {
    toast.success(__('Backup created successfully'))
    api.reload()
    const filename = res?.database_backup?.name
    if (filename) {
      download(filename)
    }
  },
  onError(err) {
    const message = err?.messages?.[0] || err?.message || __('Backup failed')
    toast.error(message)
  },
})

const loading = computed(() => api.loading)
const data = computed(() => api.data)
const error = computed(() => api.error?.message || api.error)

function refresh() {
  api.reload()
}

async function triggerManualBackup() {
  if (manualBackup.loading) return
  await manualBackup.submit()
}

function prettySize(bytes) {
  if (!bytes && bytes !== 0) return '-'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = Number(bytes)
  let unit = 0
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024
    unit += 1
  }
  return `${size.toFixed(size >= 10 || unit === 0 ? 0 : 1)} ${units[unit]}`
}

function formatDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  const hh = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  const sec = String(d.getSeconds()).padStart(2, '0')
  return `${dd}/${mm}/${yyyy}, ${hh}:${min}:${sec}`
}

function formatType(t) {
  if (!t) return '-'
  const m = {
    database: __('DB'),
    private_files: __('Private'),
    public_files: __('Public'),
    site_config: __('Config'),
    archive: __('Archive'),
  }
  return m[t] || t
}

async function download(filename) {
  if (!filename) return
  // open download link using Frappe API endpoint
  const url = `/api/method/crm.api.settings.download_backup?filename=${encodeURIComponent(filename)}`
  // create anchor and click to trigger download
  const a = document.createElement('a')
  a.href = url
  a.target = '_blank'
  a.rel = 'noopener'
  document.body.appendChild(a)
  a.click()
  a.remove()
}
</script>

<style scoped>
</style>
