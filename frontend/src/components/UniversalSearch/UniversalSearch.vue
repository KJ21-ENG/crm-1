<template>
  <div class="flex items-center order-first">
    <button
      type="button"
      class="group flex items-center gap-2 rounded-lg border border-transparent bg-surface-gray-1 px-3 py-2 text-sm text-ink-gray-5 transition-colors hover:border-ink-gray-3 hover:bg-surface-white hover:text-ink-gray-9 focus:outline-none focus-visible:ring-2 focus-visible:ring-ink-gray-4 focus-visible:ring-offset-2"
      :title="shortcutLabel"
      @click="openSearch"
    >
      <FeatherIcon
        name="search"
        class="h-4 w-4 text-ink-gray-5 transition-colors group-hover:text-ink-gray-7"
      />
      <span class="hidden lg:inline text-sm font-medium text-ink-gray-6 group-hover:text-ink-gray-8">
        {{ __('Search CRM') }}
      </span>
      <KeyboardShortcut class="hidden md:flex" :meta="isMac" :ctrl="!isMac" bg>
        <span>K</span>
      </KeyboardShortcut>
    </button>
    <Dialog v-model="show" :options="dialogOptions">
      <template #body>
        <div class="overflow-hidden rounded-lg bg-surface-white">
          <div class="flex items-center gap-3 border-b bg-surface-gray-1 px-4 py-3">
            <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-4" />
            <TextInput
              ref="searchInput"
              v-model="searchQuery"
              :placeholder="placeholder"
              class="w-full"
              :autofocus="true"
            />
            <button
              v-if="searchQuery"
              type="button"
              class="text-ink-gray-4 transition-colors hover:text-ink-gray-6"
              @click="clearQuery"
            >
              <FeatherIcon name="x" class="h-4 w-4" />
            </button>
            <KeyboardShortcut :meta="isMac" :ctrl="!isMac" bg>
              <span>K</span>
            </KeyboardShortcut>
          </div>
          <div ref="resultsContainer" class="max-h-[70vh] overflow-y-auto bg-surface-white">
            <div
              v-if="!hasQuery"
              class="flex flex-col items-center justify-center gap-2 px-6 py-12 text-center text-ink-gray-5"
            >
              <FeatherIcon name="compass" class="h-10 w-10 text-ink-gray-3" />
              <p class="text-base font-medium text-ink-gray-7">{{ __('Search the entire CRM') }}</p>
              <p class="text-sm text-ink-gray-5">
                {{ __('Look up leads, tickets, customers, tasks, notes, call logs, and support pages from one place.') }}
              </p>
            </div>
            <div
              v-else-if="showMinimumHint"
              class="flex flex-col items-center justify-center gap-2 px-6 py-12 text-center text-ink-gray-5"
            >
              <FeatherIcon name="type" class="h-10 w-10 text-ink-gray-3" />
              <p class="text-base font-medium text-ink-gray-7">{{ __('Keep typing…') }}</p>
              <p class="text-sm text-ink-gray-5">
                {{ __('Enter at least {0} characters or 4 digits to search.', [MIN_CHARS]) }}
              </p>
            </div>
            <div
              v-else-if="searchResource.loading"
              class="flex flex-col items-center justify-center gap-2 px-6 py-12 text-ink-gray-5"
            >
              <Spinner class="h-6 w-6" />
              <p class="text-sm">{{ __('Finding relevant records…') }}</p>
            </div>
            <div
              v-else-if="errorMessage"
              class="flex flex-col items-center justify-center gap-2 px-6 py-12 text-center text-red-500"
            >
              <FeatherIcon name="alert-circle" class="h-10 w-10" />
              <p class="font-medium">{{ __('Something went wrong while searching') }}</p>
              <p class="text-sm text-ink-gray-5">{{ errorMessage }}</p>
            </div>
            <div v-else-if="hasResults" class="space-y-4 py-4">
              <div
                v-for="(section, sectionIndex) in sections"
                :key="section.doctype"
                class="px-4"
              >
                <div class="flex items-center gap-2 px-1 pb-2 text-xs font-semibold uppercase tracking-wide text-ink-gray-4">
                  <FeatherIcon :name="section.icon" class="h-3.5 w-3.5" />
                  <span>{{ section.label }}</span>
                  <span class="text-ink-gray-3">•</span>
                  <span>{{ section.results.length }}</span>
                </div>
                <div class="space-y-2">
                  <button
                    v-for="(result, resultIndex) in section.results"
                    :key="`${result.doctype}-${result.name}`"
                    type="button"
                    class="w-full rounded-lg border border-transparent px-3 py-3 text-left transition-colors"
                    :class="{
                      'bg-surface-gray-2 border-ink-gray-3 shadow-inner': getGlobalIndex(sectionIndex, resultIndex) === activeIndex,
                      'hover:bg-surface-gray-1': getGlobalIndex(sectionIndex, resultIndex) !== activeIndex,
                    }"
                    @mouseenter="setActive(getGlobalIndex(sectionIndex, resultIndex))"
                    @click="activateResult(flatResults[getGlobalIndex(sectionIndex, resultIndex)])"
                    :data-result-index="getGlobalIndex(sectionIndex, resultIndex)"
                  >
                    <div class="flex gap-3">
                      <div class="min-w-0 flex-1 space-y-1">
                        <div class="flex items-center gap-2 text-base font-semibold text-ink-gray-9">
                          <FeatherIcon :name="result.icon || section.icon" class="h-4 w-4 text-ink-gray-5" />
                          <span class="truncate">{{ result.title }}</span>
                          <Badge
                            v-if="result.meta?.status"
                            :label="result.meta.status"
                            variant="subtle"
                            theme="blue"
                          />
                          <Badge
                            v-if="result.meta?.priority"
                            :label="result.meta.priority"
                            variant="subtle"
                            theme="orange"
                          />
                        </div>
                        <div v-if="result.subtitle" class="text-sm text-ink-gray-5">
                          {{ result.subtitle }}
                        </div>
                        <div
                          v-if="metaEntries(result.meta).length"
                          class="flex flex-wrap gap-1 text-xs text-ink-gray-6"
                        >
                          <span
                            v-for="entry in metaEntries(result.meta)"
                            :key="entry.key"
                            class="rounded bg-surface-gray-2 px-2 py-1"
                          >
                            <span class="font-medium text-ink-gray-7">{{ entry.label }}:</span>
                            <span class="ml-1 text-ink-gray-6">{{ entry.value }}</span>
                          </span>
                        </div>
                        <div
                          v-if="matchEntries(result).length"
                          class="flex flex-wrap gap-1 text-xs text-ink-gray-5"
                        >
                          <span
                            v-for="match in matchEntries(result)"
                            :key="match.key"
                            class="rounded border border-ink-gray-2 px-2 py-0.5"
                          >
                            {{ match.label }} · {{ match.value }}
                            <span v-if="match.weight != null" class="ml-1 text-ink-gray-4">
                              ({{ formatNumber(match.weight, 1) }})
                            </span>
                          </span>
                        </div>
                        <div
                          v-if="scoreSummary(result).parts.length"
                          class="text-xs text-ink-gray-4"
                        >
                          {{ __('Score') }} {{ scoreSummary(result).total }}
                          <span class="ml-1">
                            ({{ scoreSummary(result).parts.join(' + ') }})
                          </span>
                        </div>
                      </div>
                      <div class="flex flex-col items-end justify-between text-right text-xs text-ink-gray-4">
                        <span class="uppercase tracking-wide text-[10px]">{{ stripPrefix(result.doctype) }}</span>
                        <div class="flex items-center gap-1">
                          <FeatherIcon
                            v-if="result.external || section.external"
                            name="external-link"
                            class="h-3.5 w-3.5"
                          />
                          <KeyboardShortcut class="hidden sm:flex" :meta="isMac" :ctrl="!isMac" bg>
                            <span>↵</span>
                          </KeyboardShortcut>
                        </div>
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </div>
            <div
              v-else
              class="flex flex-col items-center justify-center gap-2 px-6 py-12 text-center text-ink-gray-5"
            >
              <FeatherIcon name="search" class="h-10 w-10 text-ink-gray-3" />
              <p class="text-base font-medium text-ink-gray-7">
                {{ __('No matches for “{0}”', [searchQuery]) }}
              </p>
              <p class="text-sm text-ink-gray-5">
                {{ __('Try different keywords, an email address, or a phone number.') }}
              </p>
            </div>
          </div>
          <div
            v-if="hasResults"
            class="flex items-center justify-between border-t bg-surface-gray-1 px-4 py-2 text-xs text-ink-gray-5"
          >
            <span>{{ __('Showing {0} results', [flatResults.length]) }}</span>
            <span v-if="metadata.elapsed_ms">{{ metadata.elapsed_ms }} ms</span>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import KeyboardShortcut from '@/components/KeyboardShortcut.vue'
import { createResource, FeatherIcon, TextInput, Spinner, Badge } from 'frappe-ui'
import { useDebounceFn } from '@vueuse/core'
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const MIN_CHARS = 2
const MIN_DIGITS = 4

const router = useRouter()
const isMac = navigator.userAgent.includes('Mac')

const show = ref(false)
const searchQuery = ref('')
const sections = ref([])
const metadata = ref({})
const errorMessage = ref('')
const activeIndex = ref(-1)

const searchInput = ref(null)
const resultsContainer = ref(null)

const dialogOptions = { size: '4xl' }
const shortcutLabel = computed(() => (isMac ? 'Search (⌘K)' : 'Search (Ctrl+K)'))
const placeholder = computed(() => __('Find leads, tickets, customers, tasks…'))

const searchResource = createResource({
  url: 'crm.api.search.universal_search',
  auto: false,
  onSuccess(data) {
    const sectionsWithScores = (data?.sections || []).map((section, index) => {
      const results = (section.results || []).map((result) => ({
        ...result,
        score: typeof result.score === 'number' ? result.score : Number(result.score) || 0,
      }))
      const topScore = results.reduce(
        (max, result) => (result.score > max ? result.score : max),
        Number.NEGATIVE_INFINITY,
      )
      return {
        ...section,
        results,
        _topScore: topScore,
        _order: index,
      }
    })

    sections.value = sectionsWithScores.sort((a, b) => {
      const scoreDiff = (b._topScore ?? Number.NEGATIVE_INFINITY) - (a._topScore ?? Number.NEGATIVE_INFINITY)
      if (Math.abs(scoreDiff) > 0.001) {
        return scoreDiff
      }
      return a._order - b._order
    }).map(({ _topScore, _order, ...section }) => section)
    metadata.value = data?.metadata || {}
    errorMessage.value = ''
  },
  onError(error) {
    errorMessage.value = error?.message || __('Unable to fetch search results right now.')
  },
})

const trimmedQuery = computed(() => searchQuery.value.trim())

function meetsMinimum(query) {
  if (!query) return false
  if (query.includes('@')) {
    return query.length >= 3
  }
  if (query.replace(/\D/g, '').length >= MIN_DIGITS) {
    return true
  }
  return query.length >= MIN_CHARS
}

const hasQuery = computed(() => !!trimmedQuery.value)
const showMinimumHint = computed(
  () => hasQuery.value && !meetsMinimum(trimmedQuery.value),
)

const flatResults = computed(() => {
  const items = []
  sections.value.forEach((section, sectionIndex) => {
    ;(section.results || []).forEach((result, resultIndex) => {
      items.push({
        ...result,
        sectionIndex,
        resultIndex,
        sectionLabel: section.label,
        sectionIcon: section.icon,
        external: result.external ?? section.external ?? false,
      })
    })
  })
  return items
})

const hasResults = computed(() => flatResults.value.length > 0)

const sectionOffsets = computed(() => {
  const offsets = []
  let total = 0
  sections.value.forEach((section) => {
    offsets.push(total)
    total += section.results?.length || 0
  })
  return offsets
})

function getGlobalIndex(sectionIndex, resultIndex) {
  const base = sectionOffsets.value[sectionIndex] || 0
  return base + resultIndex
}

const HTML_TAG_REGEX = /<[^>]+>/g

function sanitizeValue(value) {
  if (value == null) return ''
  return String(value).replace(HTML_TAG_REGEX, ' ').replace(/\s+/g, ' ').trim()
}

function canonicalChipKey(label, value) {
  return `${label}`.toLowerCase().trim() + '|' + sanitizeValue(value).toLowerCase()
}

function metaEntries(meta) {
  if (!meta) return []
  return Object.entries(meta)
    .filter(([, value]) => value)
    .map(([key, value]) => ({ key, label: formatLabel(key), value }))
}

function matchEntries(result) {
  const entries = []
  if (!result?.matches?.length) {
    return entries
  }

  const metaSeen = new Set(metaEntries(result.meta).map((entry) => canonicalChipKey(entry.label, entry.value)))

  result.matches.forEach((match) => {
    const field = match.field === 'content' ? 'snippet' : match.field
    const label = formatLabel(field)
    const value = sanitizeValue(match.field === 'content' ? match.value || result.meta?.snippet : match.value)
    if (!value) return
    const id = canonicalChipKey(label, value)
    if (metaSeen.has(id)) return
    metaSeen.add(id)
    entries.push({
      key: `${match.field}-${id}`,
      label,
      value,
      weight: typeof match.weight === 'number' ? match.weight : Number(match.weight) || undefined,
    })
  })

  return entries
}

function scoreSummary(result) {
  const total = typeof result?.score === 'number' ? result.score : Number(result?.score) || 0
  const details = result?.score_details || {}
  const parts = []
  if (typeof details.matches === 'number') {
    parts.push(`${__('matches')} ${formatNumber(details.matches)}`)
  }
  if (typeof details.match_bonus === 'number') {
    parts.push(`${__('stack bonus')} ${formatNumber(details.match_bonus)}`)
  }
  if (typeof details.recency_bonus === 'number') {
    parts.push(`${__('recency')} ${formatNumber(details.recency_bonus)}`)
  }
  return {
    total: formatNumber(total),
    parts,
  }
}

function formatNumber(value, digits = 2) {
  return Number(value || 0).toFixed(digits)
}

function formatLabel(key) {
  if (!key) return ''
  return key
    .toString()
    .replace(/_/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .split(' ')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function stripPrefix(value) {
  if (!value) return ''
  return value.replace(/^CRM\s+/i, '')
}

const triggerSearch = useDebounceFn(() => {
  if (!show.value) {
    return
  }
  const query = trimmedQuery.value
  if (!query) {
    sections.value = []
    metadata.value = {}
    return
  }
  if (!meetsMinimum(query)) {
    return
  }
  searchResource.submit({ query, limit: 20 })
}, 220)

watch(searchQuery, () => {
  activeIndex.value = -1
  if (show.value) {
    triggerSearch()
  }
})

watch(flatResults, (items) => {
  if (!items.length) {
    activeIndex.value = -1
    return
  }
  if (activeIndex.value === -1 || activeIndex.value >= items.length) {
    activeIndex.value = 0
  }
})

watch(show, (value) => {
  if (value) {
    nextTick(() => searchInput.value?.el?.focus?.())
    if (meetsMinimum(trimmedQuery.value)) {
      triggerSearch()
    }
  } else {
    activeIndex.value = -1
  }
})

function openSearch() {
  show.value = true
}

function closeSearch() {
  show.value = false
}

function clearQuery() {
  searchQuery.value = ''
  sections.value = []
  metadata.value = {}
  activeIndex.value = -1
  nextTick(() => searchInput.value?.el?.focus?.())
}

function setActive(index) {
  activeIndex.value = index
}

function scrollActiveIntoView() {
  if (!resultsContainer.value || activeIndex.value < 0) return
  nextTick(() => {
    if (!resultsContainer.value) return
    const el = resultsContainer.value.querySelector(
      `[data-result-index="${activeIndex.value}"]`,
    )
    el?.scrollIntoView({ block: 'nearest' })
  })
}

watch(activeIndex, () => scrollActiveIntoView())

function moveSelection(direction) {
  const items = flatResults.value
  if (!items.length) {
    activeIndex.value = -1
    return
  }
  if (activeIndex.value === -1) {
    activeIndex.value = direction > 0 ? 0 : items.length - 1
    return
  }
  let next = activeIndex.value + direction
  if (next < 0) next = items.length - 1
  if (next >= items.length) next = 0
  activeIndex.value = next
}

function activateResult(item) {
  if (!item) return
  closeSearch()
  const route = item.route
  if (!route) {
    return
  }
  if (item.external) {
    window.open(route, '_blank', 'noopener')
    return
  }
  router.push(route).catch(() => {})
}

function handleGlobalKey(event) {
  const key = event.key.toLowerCase()
  const target = event.target
  const tagName = target?.tagName
  const isEditable =
    target?.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(tagName)

  if ((event.metaKey || event.ctrlKey) && key === 'k') {
    if (isEditable) {
      return
    }
    event.preventDefault()
    openSearch()
    return
  }

  if (!show.value) {
    return
  }

  if (key === 'escape') {
    event.preventDefault()
    closeSearch()
    return
  }

  if (key === 'arrowdown') {
    event.preventDefault()
    moveSelection(1)
    return
  }

  if (key === 'arrowup') {
    event.preventDefault()
    moveSelection(-1)
    return
  }

  if (key === 'enter') {
    const item = flatResults.value[activeIndex.value]
    if (item) {
      event.preventDefault()
      activateResult(item)
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKey)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKey)
})
</script>
