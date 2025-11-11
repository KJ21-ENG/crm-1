<template>
  <div ref="pickerRef" class="custom-datetime-picker relative">
    <div
      class="relative flex h-7 w-full items-center justify-between gap-2 rounded bg-surface-gray-2 px-2 py-1 transition-colors hover:bg-surface-gray-3 border border-transparent focus:border-outline-gray-4 focus:outline-none focus:ring-2 focus:ring-outline-gray-3 text-base rounded h-7 py-1.5 px-2 border border-gray-100 bg-surface-gray-2 placeholder-ink-gray-4 hover:border-outline-gray-modals hover:bg-surface-gray-3 focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors w-full"
      :class="inputClass"
      @click="togglePicker"
      :style="{ cursor: 'pointer' }"
    >
      <div class="flex items-center justify-between w-full">
        <span class="datetime-display">
          {{ displayValue || placeholder }}
        </span>
        <div class="calendar-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M8 2V5M16 2V5M3.5 9.09H20.5M21 8.5V17C21 20 19.5 22 16 22H8C4.5 22 3 20 3 17V8.5C3 5 4.5 3 8 3H16C19.5 3 21 5 21 8.5Z"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-miterlimit="10"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
      </div>
    </div>

    <Teleport :to="teleportTarget" :disabled="resolvedDisableTeleport">
      <div v-if="isOpen" class="datetime-picker-overlay" @click="closePicker">
        <div
          ref="popupRef"
          class="datetime-picker-popup"
          :style="pickerPosition"
          @click.stop
          @mousedown.stop
          @touchstart.stop
        >
          <div class="picker-header">
            <button @click="previousMonth" class="nav-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
            <div class="month-year-display" :class="yearQuickSelect ? 'quick-select' : ''">
              <template v-if="yearQuickSelect">
                <select v-model.number="monthIndex" class="month-select">
                  <option v-for="(m, i) in monthNames" :key="i" :value="i">{{ m }}</option>
                </select>
                <select v-model.number="yearValue" class="year-select">
                  <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
                </select>
              </template>
              <template v-else>
                <span class="month">{{ currentMonthName }}</span>
                <span class="year">{{ currentYear }}</span>
              </template>
            </div>
            <button @click="nextMonth" class="nav-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
          </div>

          <div class="calendar-grid">
            <div class="days-header">
              <div v-for="day in daysOfWeek" :key="day" class="day-header">{{ day }}</div>
            </div>

            <div class="calendar-dates">
              <div
                v-for="date in calendarDates"
                :key="date.key"
                class="calendar-date"
                :class="{
                  'other-month': !date.isCurrentMonth,
                  'selected': !isRangeMode && date.isSelected,
                  'range-start': isRangeMode && date.isRangeStart,
                  'range-end': isRangeMode && date.isRangeEnd,
                  'in-range': isRangeMode && date.isInRange,
                  'today': date.isToday,
                  'clickable': date.isCurrentMonth
                }"
                @click="date.isCurrentMonth && selectDate(date.date)"
              >
                {{ date.day }}
              </div>
            </div>
          </div>

          <div v-if="showTimeComputed" class="time-picker">
            <template v-if="isRangeMode">
              <div class="time-section">
                <div class="time-label">Start Time</div>
                <div class="time-inputs">
                  <div class="time-input-group">
                    <label>Hour</label>
                    <select v-model="rangeStartHour" class="time-select">
                      <option v-for="hour in hours" :key="`start-hour-${hour}`" :value="hour">{{ hour.toString().padStart(2, '0') }}</option>
                    </select>
                  </div>
                  <div class="time-separator">:</div>
                  <div class="time-input-group">
                    <label>Minute</label>
                    <select v-model="rangeStartMinute" class="time-select">
                      <option v-for="minute in minutes" :key="`start-minute-${minute}`" :value="minute">{{ minute.toString().padStart(2, '0') }}</option>
                    </select>
                  </div>
                  <div class="time-input-group">
                    <label>Period</label>
                    <select v-model="rangeStartPeriod" class="time-select">
                      <option value="AM">AM</option>
                      <option value="PM">PM</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="time-section">
                <div class="time-label">End Time</div>
                <div class="time-inputs">
                  <div class="time-input-group">
                    <label>Hour</label>
                    <select v-model="rangeEndHour" class="time-select">
                      <option v-for="hour in hours" :key="`end-hour-${hour}`" :value="hour">{{ hour.toString().padStart(2, '0') }}</option>
                    </select>
                  </div>
                  <div class="time-separator">:</div>
                  <div class="time-input-group">
                    <label>Minute</label>
                    <select v-model="rangeEndMinute" class="time-select">
                      <option v-for="minute in minutes" :key="`end-minute-${minute}`" :value="minute">{{ minute.toString().padStart(2, '0') }}</option>
                    </select>
                  </div>
                  <div class="time-input-group">
                    <label>Period</label>
                    <select v-model="rangeEndPeriod" class="time-select">
                      <option value="AM">AM</option>
                      <option value="PM">PM</option>
                    </select>
                  </div>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="time-section">
                <div class="time-label">Time</div>
                <div class="time-inputs">
                  <div class="time-input-group">
                    <label>Hour</label>
                    <select v-model="selectedHour" class="time-select">
                      <option v-for="hour in hours" :key="hour" :value="hour">{{ hour.toString().padStart(2, '0') }}</option>
                    </select>
                  </div>
                  <div class="time-separator">:</div>
                  <div class="time-input-group">
                    <label>Minute</label>
                    <select v-model="selectedMinute" class="time-select">
                      <option v-for="minute in minutes" :key="minute" :value="minute">{{ minute.toString().padStart(2, '0') }}</option>
                    </select>
                  </div>
                  <div class="time-input-group">
                    <label>Period</label>
                    <select v-model="selectedPeriod" class="time-select">
                      <option value="AM">AM</option>
                      <option value="PM">PM</option>
                    </select>
                  </div>
                </div>
              </div>
            </template>
          </div>

          <div class="picker-actions">
            <button @click="clearSelection" class="action-btn clear-btn">Clear</button>
            <button @click="setToday" class="action-btn today-btn">Today</button>
            <button @click="applySelection" class="action-btn apply-btn">Apply</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Array, Object],
    default: null,
  },
  placeholder: {
    type: String,
    default: 'Select date and time',
  },
  inputClass: {
    type: [String, Array, Object],
    default: () => 'border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900',
  },
  mode: {
    type: String,
    default: 'datetime', // datetime | date | daterange | datetimerange
  },
  showTime: {
    type: Boolean,
    default: undefined,
  },
  disableTeleport: {
    type: Boolean,
    default: false,
  },
  teleportTarget: {
    type: String,
    default: 'body',
  },
  preventAutoFill: {
    type: Boolean,
    default: false,
  },
  autoDefault: {
    type: Boolean,
    default: true,
  },
  yearQuickSelect: {
    type: Boolean,
    default: false,
  },
  rangeValueType: {
    type: String,
    default: 'array', // array | object
    validator: (val) => ['array', 'object'].includes(val),
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

const pickerRef = ref(null)
const popupRef = ref(null)

const isOpen = ref(false)
const isValueApplied = ref(false)
const hasUserSelection = ref(false)
const isInsideDialog = ref(false)

const currentDate = ref(startOfMonth(new Date()))
const selectedDate = ref(null)
const rangeStart = ref(null)
const rangeEnd = ref(null)

const selectedHour = ref(12)
const selectedMinute = ref(0)
const selectedPeriod = ref('AM')
const rangeStartHour = ref(12)
const rangeStartMinute = ref(0)
const rangeStartPeriod = ref('AM')
const rangeEndHour = ref(12)
const rangeEndMinute = ref(0)
const rangeEndPeriod = ref('AM')

const pickerPosition = ref({ top: '0px', left: '0px' })

const daysOfWeek = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
const monthNames = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
]

const monthIndex = ref(new Date().getMonth())
const yearValue = ref(new Date().getFullYear())

const yearOptions = computed(() => {
  const end = new Date().getFullYear() + 10
  const start = 1900
  const arr = []
  for (let y = end; y >= start; y--) arr.push(y)
  return arr
})

const isRangeMode = computed(() => ['daterange', 'datetimerange'].includes(props.mode))
const showTimeComputed = computed(() => {
  if (typeof props.showTime === 'boolean') {
    return props.showTime
  }
  return props.mode === 'datetime' || props.mode === 'datetimerange'
})

const resolvedDisableTeleport = computed(() => props.disableTeleport || isInsideDialog.value)

const displayValue = computed(() => {
  if (!isValueApplied.value) {
    if (!props.modelValue) return ''
  }

  if (isRangeMode.value) {
    if (!rangeStart.value || !rangeEnd.value) return ''
    const startDisplay = formatDisplay(rangeStart.value, showTimeComputed.value, rangeStartHour.value, rangeStartMinute.value, rangeStartPeriod.value)
    const endDisplay = formatDisplay(rangeEnd.value, showTimeComputed.value, rangeEndHour.value, rangeEndMinute.value, rangeEndPeriod.value)
    return `${startDisplay} - ${endDisplay}`
  }

  if (!selectedDate.value) return ''
  return formatDisplay(selectedDate.value, showTimeComputed.value, selectedHour.value, selectedMinute.value, selectedPeriod.value)
})

const currentMonthName = computed(() => currentDate.value.toLocaleDateString('en-US', { month: 'long' }))
const currentYear = computed(() => currentDate.value.getFullYear())

const hours = computed(() => Array.from({ length: 12 }, (_, i) => i + 1))
const minutes = computed(() => Array.from({ length: 60 }, (_, i) => i))

const calendarDates = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()

  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const firstDayOfWeek = firstDay.getDay()
  const today = new Date()
  const todayYear = today.getFullYear()
  const todayMonth = today.getMonth()
  const todayDay = today.getDate()

  const dates = []

  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(year, month, -i)
    dates.push(createCalendarDate(date, todayYear, todayMonth, todayDay, false))
  }

  for (let day = 1; day <= lastDay.getDate(); day++) {
    const date = new Date(year, month, day)
    dates.push(createCalendarDate(date, todayYear, todayMonth, todayDay, true))
  }

  const remainingDays = 42 - dates.length
  for (let day = 1; day <= remainingDays; day++) {
    const date = new Date(year, month + 1, day)
    dates.push(createCalendarDate(date, todayYear, todayMonth, todayDay, false, 'next'))
  }

  return dates
})

function createCalendarDate(date, todayYear, todayMonth, todayDay, isCurrentMonth, prefix = 'prev') {
  const keyPrefix = isCurrentMonth ? 'current' : prefix
  const dateYear = date.getFullYear()
  const dateMonth = date.getMonth()
  const dateDay = date.getDate()

  const isSelected = !isRangeMode.value && selectedDate.value && isSameDate(date, selectedDate.value)
  const isRangeStart = isRangeMode.value && rangeStart.value && isSameDate(date, rangeStart.value)
  const isRangeEnd = isRangeMode.value && rangeEnd.value && isSameDate(date, rangeEnd.value)
  const isInRange = isRangeMode.value && rangeStart.value && rangeEnd.value &&
    date >= rangeStart.value && date <= rangeEnd.value

  return {
    date,
    day: dateDay,
    isCurrentMonth,
    isSelected,
    isRangeStart,
    isRangeEnd,
    isInRange,
    isToday: dateYear === todayYear && dateMonth === todayMonth && dateDay === todayDay,
    key: `${keyPrefix}-${date.getTime()}`,
  }
}

function togglePicker() {
  updateDialogContext()
  if (isOpen.value) {
    closePicker()
    return
  }
  isOpen.value = true
  if (!hasUserSelection.value) {
    initializeCurrent()
  }
  calculatePosition()
  document.body.classList.add('picker-open')
}

function closePicker() {
  isOpen.value = false
  document.body.classList.remove('picker-open')
}

function previousMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
}

function nextMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
}

function selectDate(date) {
  const cleanDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())

  if (isRangeMode.value) {
    if (!rangeStart.value || (rangeStart.value && rangeEnd.value)) {
      rangeStart.value = cleanDate
      rangeEnd.value = null
    } else if (cleanDate < rangeStart.value) {
      rangeEnd.value = rangeStart.value
      rangeStart.value = cleanDate
    } else {
      rangeEnd.value = cleanDate
    }
    hasUserSelection.value = !!(rangeStart.value && rangeEnd.value)
  } else {
    selectedDate.value = cleanDate
    hasUserSelection.value = true
  }
}

function clearSelection() {
  selectedDate.value = null
  rangeStart.value = null
  rangeEnd.value = null
  hasUserSelection.value = false
  isValueApplied.value = false
}

function setToday() {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  currentDate.value = startOfMonth(today)
  if (isRangeMode.value) {
    rangeStart.value = today
    rangeEnd.value = today
    setTimeFromDate(today, rangeStartHour, rangeStartMinute, rangeStartPeriod)
    setTimeFromDate(today, rangeEndHour, rangeEndMinute, rangeEndPeriod)
    hasUserSelection.value = true
  } else {
    selectedDate.value = today
    setTimeFromDate(now, selectedHour, selectedMinute, selectedPeriod)
    hasUserSelection.value = true
  }
}

function applySelection() {
  if (isRangeMode.value) {
    if (!rangeStart.value || !rangeEnd.value) {
      emit('update:modelValue', props.rangeValueType === 'object' ? { start: null, end: null } : [null, null])
      emit('change', props.rangeValueType === 'object' ? { start: null, end: null } : [null, null])
      closePicker()
      return
    }
    const startValue = formatValue(rangeStart.value, showTimeComputed.value, rangeStartHour.value, rangeStartMinute.value, rangeStartPeriod.value)
    const endValue = formatValue(rangeEnd.value, showTimeComputed.value, rangeEndHour.value, rangeEndMinute.value, rangeEndPeriod.value)
    const payload = props.rangeValueType === 'object'
      ? { start: startValue, end: endValue }
      : [startValue, endValue]
    isValueApplied.value = true
    emit('update:modelValue', payload)
    emit('change', payload)
    closePicker()
    return
  }

  if (!hasUserSelection.value || !selectedDate.value) {
    emit('update:modelValue', '')
    emit('change', '')
    closePicker()
    return
  }

  const singleValue = formatValue(selectedDate.value, showTimeComputed.value, selectedHour.value, selectedMinute.value, selectedPeriod.value)
  isValueApplied.value = true
  emit('update:modelValue', singleValue)
  emit('change', singleValue)
  closePicker()
}

function updateDialogContext() {
  const pickerElement = pickerRef.value
  if (!pickerElement) return
  isInsideDialog.value = Boolean(pickerElement.closest('.dialog-content'))
}

function calculatePosition() {
  nextTick(() => {
    const inputElement = pickerRef.value
    if (!inputElement) return
    const rect = inputElement.getBoundingClientRect()
    const disableTeleport = resolvedDisableTeleport.value

    // Determine the effective containing rectangle for positioning.
    // When teleported (default), use the viewport. When not teleported
    // (disableTeleport=true), many modal implementations apply CSS transforms
    // and overflow on ancestors, creating a new containing block. In that case,
    // we compute bounds from the nearest ancestor that creates a containing
    // block or clips overflow and then position within those bounds.
    const getContainingRect = () => {
      if (!disableTeleport) {
        return {
          top: 0,
          left: 0,
          right: window.innerWidth,
          bottom: window.innerHeight,
          width: window.innerWidth,
          height: window.innerHeight,
        }
      }
      let node = inputElement.parentElement
      while (node && node !== document.body) {
        const style = window.getComputedStyle(node)
        const createsContainingBlock =
          (style.transform && style.transform !== 'none') ||
          (style.perspective && style.perspective !== 'none') ||
          (style.filter && style.filter !== 'none') ||
          (style.willChange && /transform|perspective|filter/.test(style.willChange))
        const overflowClips = /auto|scroll|hidden|clip/.test(
          `${style.overflow} ${style.overflowX} ${style.overflowY}`,
        )
        if (createsContainingBlock || overflowClips) {
          return node.getBoundingClientRect()
        }
        node = node.parentElement
      }
      return {
        top: 0,
        left: 0,
        right: window.innerWidth,
        bottom: window.innerHeight,
        width: window.innerWidth,
        height: window.innerHeight,
      }
    }

    const bounds = getContainingRect()
    
    // Auto-calculate picker dimensions based on content and available space
    const basePickerWidth = 320
    const basePickerHeight = 520 // Base height for calendar + time + actions

    const popupEl = popupRef.value
    let previousMaxHeight = ''
    let previousOverflowY = ''
    if (popupEl) {
      previousMaxHeight = popupEl.style.maxHeight
      previousOverflowY = popupEl.style.overflowY
      // Remove prior constraints so the measurement reflects the natural size.
      popupEl.style.maxHeight = ''
      popupEl.style.overflowY = ''
    }

    // Measure actual popup size if available, otherwise use base
    const measuredWidth = popupEl?.offsetWidth || basePickerWidth
    const measuredHeight = popupEl?.offsetHeight || basePickerHeight

    if (popupEl) {
      popupEl.style.maxHeight = previousMaxHeight
      popupEl.style.overflowY = previousOverflowY
    }
    
    // Calculate available space within container bounds (with margins)
    const margin = 16
    const availableWidth = Math.max(260, bounds.width - margin * 2)
    
    // Auto-adjust width while keeping natural height for full content visibility
    const pickerWidth = Math.min(measuredWidth, availableWidth)
    let pickerHeight = measuredHeight

    if (popupEl && pickerWidth !== measuredWidth) {
      const previousWidth = popupEl.style.width
      popupEl.style.width = `${pickerWidth}px`
      // Re-measure because reducing width can change the layout height
      pickerHeight = popupEl.offsetHeight || pickerHeight
      popupEl.style.width = previousWidth
    }

    // Start by aligning to the input field
    let top = rect.bottom + 4
    let left = rect.left

    // Prevent overflow on the bottom/right within container bounds
    const minLeft = bounds.left + margin
    const minTop = bounds.top + margin
    const rightLimit = bounds.left + bounds.width - margin
    const bottomLimit = bounds.top + bounds.height - margin

    if (top + pickerHeight > bottomLimit) {
      const flippedTop = rect.top - pickerHeight - 4
      if (flippedTop >= minTop) {
        top = flippedTop
      } else {
        top = bottomLimit - pickerHeight
      }
    }
    if (left + pickerWidth > rightLimit) {
      left = rightLimit - pickerWidth
    }

    // Prevent overflow on the top/left within container bounds
    if (left < minLeft) left = minLeft
    if (top < minTop) top = minTop

    // If not teleported, convert viewport coords to container-local coords
    // because position: fixed under a transformed ancestor uses that ancestor
    // as the containing block.
    const finalLeft = disableTeleport ? left - bounds.left : left
    const finalTop = disableTeleport ? top - bounds.top : top

    pickerPosition.value = {
      top: `${finalTop}px`,
      left: `${finalLeft}px`,
      width: `${pickerWidth}px`,
      maxHeight: 'auto',
      overflowY: 'visible',
    }
  })
}

function initializeCurrent() {
  const now = new Date()
  currentDate.value = startOfMonth(now)
  monthIndex.value = now.getMonth()
  yearValue.value = now.getFullYear()

  if (isRangeMode.value) {
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    rangeStart.value = today
    rangeEnd.value = today
    setTimeFromDate(now, rangeStartHour, rangeStartMinute, rangeStartPeriod)
    setTimeFromDate(now, rangeEndHour, rangeEndMinute, rangeEndPeriod)
    hasUserSelection.value = true
  } else {
    selectedDate.value = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    setTimeFromDate(now, selectedHour, selectedMinute, selectedPeriod)
    hasUserSelection.value = true
  }
}

function setTimeFromDate(date, hourRef, minuteRef, periodRef) {
  const formatter = new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: 'numeric',
    hour12: true,
  })
  const timeParts = formatter.format(date).match(/(\d+):(\d+)\s(AM|PM)/i)
  if (timeParts) {
    hourRef.value = parseInt(timeParts[1])
    minuteRef.value = parseInt(timeParts[2])
    periodRef.value = timeParts[3].toUpperCase()
  } else {
    hourRef.value = date.getHours() % 12 || 12
    minuteRef.value = date.getMinutes()
    periodRef.value = date.getHours() >= 12 ? 'PM' : 'AM'
  }
}

function parseIncomingValue(value) {
  if (!value) return { start: null, end: null }

  if (isRangeMode.value) {
    let start
    let end
    if (Array.isArray(value)) {
      ;[start, end] = value
    } else if (typeof value === 'object') {
      start = value.start
      end = value.end
    } else if (typeof value === 'string' && value.includes(',')) {
      ;[start, end] = value.split(',')
    }
    return {
      start: start ? parseDateValue(start) : null,
      end: end ? parseDateValue(end) : null,
    }
  }

  return { start: parseDateValue(value), end: null }
}

function parseDateValue(val) {
  if (!val) return null
  if (val instanceof Date) return new Date(val.getTime())
  if (typeof val === 'string') {
    const [datePart, timePart] = val.trim().split(/[T ]/)
    if (!datePart) return null
    const [y, m, d] = datePart.split('-').map((n) => parseInt(n, 10))
    if (!y || !m || !d) return null
    let hour = 0
    let minute = 0
    let second = 0
    if (timePart) {
      const [h, min, sec = '0'] = timePart.split(':')
      hour = parseInt(h, 10) || 0
      minute = parseInt(min, 10) || 0
      second = parseInt(sec, 10) || 0
    }
    return new Date(y, m - 1, d, hour, minute, second)
  }
  return null
}

function formatDisplay(date, includeTime, hour, minute, period) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const year = date.getFullYear()
  if (!includeTime) {
    return `${month}/${day}/${year}`
  }
  const displayHour = hour % 12 || 12
  const displayMinute = String(minute).padStart(2, '0')
  return `${month}/${day}/${year} ${displayHour.toString().padStart(2, '0')}:${displayMinute} ${period}`
}

function formatValue(date, includeTime, hour, minute, period) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  if (!includeTime) {
    return `${year}-${month}-${day}`
  }
  let h = hour % 12
  if (period === 'PM') {
    h += 12
  }
  if (period === 'AM' && h === 12) {
    h = 0
  }
  const hour24 = String(h).padStart(2, '0')
  const minuteStr = String(minute).padStart(2, '0')
  return `${year}-${month}-${day} ${hour24}:${minuteStr}:00`
}

function isSameDate(a, b) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

function startOfMonth(date) {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

function handleResize() {
  if (isOpen.value) {
    calculatePosition()
  }
}

const handleClickOutside = (event) => {
  if (!isOpen.value) return
  const popupEl = popupRef.value
  const pickerEl = pickerRef.value
  const path = typeof event.composedPath === 'function' ? event.composedPath() : []
  if (popupEl && (popupEl.contains(event.target) || path.includes(popupEl))) return
  if (pickerEl && (pickerEl.contains(event.target) || path.includes(pickerEl))) return
  closePicker()
}

watch(() => props.modelValue, (val) => {
  const parsed = parseIncomingValue(val)
  if (isRangeMode.value) {
    if (parsed.start) {
      rangeStart.value = new Date(parsed.start.getFullYear(), parsed.start.getMonth(), parsed.start.getDate())
      setTimeFromDate(parsed.start, rangeStartHour, rangeStartMinute, rangeStartPeriod)
    } else {
      rangeStart.value = null
    }
    if (parsed.end) {
      rangeEnd.value = new Date(parsed.end.getFullYear(), parsed.end.getMonth(), parsed.end.getDate())
      setTimeFromDate(parsed.end, rangeEndHour, rangeEndMinute, rangeEndPeriod)
    } else {
      rangeEnd.value = null
    }
    if (parsed.start && parsed.end) {
      currentDate.value = startOfMonth(parsed.start)
      hasUserSelection.value = true
      isValueApplied.value = true
    }
  } else if (parsed.start) {
    selectedDate.value = new Date(parsed.start.getFullYear(), parsed.start.getMonth(), parsed.start.getDate())
    setTimeFromDate(parsed.start, selectedHour, selectedMinute, selectedPeriod)
    currentDate.value = startOfMonth(parsed.start)
    hasUserSelection.value = true
    isValueApplied.value = true
  } else {
    hasUserSelection.value = false
    isValueApplied.value = false
  }
}, { immediate: true })

watch([monthIndex, yearValue], ([m, y]) => {
  if (typeof m === 'number' && typeof y === 'number') {
    currentDate.value = new Date(y, m, 1)
  }
})

watch(currentDate, (d) => {
  monthIndex.value = d.getMonth()
  yearValue.value = d.getFullYear()
})

watch([selectedHour, selectedMinute, selectedPeriod], () => {
  if (!isRangeMode.value && selectedDate.value) {
    hasUserSelection.value = true
  }
})

watch([rangeStartHour, rangeStartMinute, rangeStartPeriod, rangeEndHour, rangeEndMinute, rangeEndPeriod], () => {
  if (isRangeMode.value && rangeStart.value && rangeEnd.value) {
    hasUserSelection.value = true
  }
})

onMounted(() => {
  window.addEventListener('resize', handleResize)
  document.addEventListener('click', handleClickOutside)

  if (!props.modelValue && props.autoDefault && !props.preventAutoFill) {
    initializeCurrent()
    applySelection()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('click', handleClickOutside)
  document.body.classList.remove('picker-open')
})
</script>

<style scoped>
.custom-datetime-picker {
  position: relative;
  display: inline-block;
}

.datetime-display {
  flex: 1;
  color: inherit;
  font-size: 14px;
}

.calendar-icon {
  color: #6b7280;
  margin-left: 8px;
}

.datetime-picker-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: transparent;
}

.datetime-picker-popup {
  /*
   * Use fixed positioning when teleported to body; fall back to absolute
   * positioning when rendered inside a transformed/overflow-hidden modal
   * (disableTeleport=true) to ensure the popup is clipped and aligned
   * within the dialog instead of the viewport.
   */
  position: fixed !important;
  z-index: 99999 !important;
  background: #ffffff !important;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 16px;
  padding-bottom: 20px;
  width: 320px;
  /* Auto-adjust height based on content and available space */
  overflow: visible;
}

/* When the picker is inside a transformed container (common for modals),
   browsers treat fixed elements as fixed to that container. However, some
   UI kits still compute coordinates relative to that container. The class
   below can be toggled if ever needed, but we compute coordinates already.
*/

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.month-select,
.year-select {
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 4px 6px;
  margin: 0 4px;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s ease-in-out;
}

.nav-btn:hover {
  background: #f3f4f6;
  color: #000000;
}

.month-year-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-weight: 600;
}

.month-year-display.quick-select {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.month {
  font-size: 16px;
  color: #000000;
}

.year {
  font-size: 14px;
  color: #6b7280;
}

.calendar-grid {
  margin-bottom: 16px;
}

.days-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.day-header {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
}

.calendar-dates {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-date {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  color: #000000;
}

.calendar-date.other-month {
  color: #d1d5db;
  cursor: default;
}

.calendar-date.clickable:hover {
  background: #f3f4f6;
  color: #000000 !important; /* Ensure readable text on hover */
}

.calendar-date.today {
  background: #e5e7eb;
  color: #000000;
  font-weight: 600;
}

.calendar-date.selected,
.calendar-date.range-start,
.calendar-date.range-end {
  background: #000000;
  color: #ffffff;
  font-weight: 600;
}

/* Preserve contrast when hovering selected endpoints */
.calendar-date.selected.clickable:hover,
.calendar-date.range-start.clickable:hover,
.calendar-date.range-end.clickable:hover {
  background: #000000 !important;
  color: #ffffff !important;
}

/* Preserve contrast for today on hover */
.calendar-date.today.clickable:hover {
  background: #e5e7eb !important;
  color: #000000 !important;
}

.calendar-date.in-range {
  background: rgba(0, 0, 0, 0.1);
  color: #000000;
}

.calendar-date.range-start {
  border-top-left-radius: 9999px;
  border-bottom-left-radius: 9999px;
}

.calendar-date.range-end {
  border-top-right-radius: 9999px;
  border-bottom-right-radius: 9999px;
}

.time-picker {
  border-top: 1px solid #e5e7eb;
  padding-top: 16px;
  margin-bottom: 16px;
}

.time-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.time-label {
  font-size: 14px;
  font-weight: 600;
  color: #000000;
}

.time-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.time-input-group label {
  font-size: 12px;
  color: #6b7280;
}

.time-select {
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #ffffff;
  font-size: 14px;
  color: #000000;
  cursor: pointer;
  min-width: 60px;
}

.time-select:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.time-separator {
  font-size: 18px;
  font-weight: 600;
  color: #6b7280;
  margin-top: 20px;
}

.picker-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.clear-btn {
  background: transparent;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.clear-btn:hover {
  background: #f9fafb;
  color: #000000;
}

.today-btn {
  background: transparent;
  color: #000000;
  border: 1px solid #000000;
}

.today-btn:hover {
  background: #000000;
  color: #ffffff;
}

.apply-btn {
  background: #000000;
  color: #ffffff !important;
  flex: 1;
}

.apply-btn:hover {
  background: #374151;
}

:global(body.picker-open) {
  overflow: hidden;
}

.datetime-picker-popup {
  color: #000000 !important;
}

.calendar-date {
  color: #000000 !important;
}

.calendar-date.other-month {
  color: #d1d5db !important;
}

.calendar-date.selected {
  color: #ffffff !important;
}

.calendar-date.today {
  color: #000000 !important;
  background: #e5e7eb !important;
  font-weight: 600 !important;
}

.time-select {
  color: #000000 !important;
  background: #ffffff !important;
}

.action-btn {
  color: inherit !important;
}

.clear-btn {
  color: #6b7280 !important;
}

.clear-btn:hover {
  color: #000000 !important;
}

.today-btn {
  color: #000000 !important;
}

.today-btn:hover {
  color: #ffffff !important;
}

.apply-btn {
  color: #ffffff !important;
}
</style>
