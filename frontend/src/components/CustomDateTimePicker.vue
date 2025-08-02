<template>
  <div class="custom-datetime-picker relative">
    <!-- Input field that triggers the picker -->
    <div
      class="datetime-input-field"
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
            <path d="M8 2V5M16 2V5M3.5 9.09H20.5M21 8.5V17C21 20 19.5 22 16 22H8C4.5 22 3 20 3 17V8.5C3 5 4.5 3 8 3H16C19.5 3 21 5 21 8.5Z" stroke="currentColor" stroke-width="1.5" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Custom Date Time Picker Popup -->
    <Teleport to="body">
      <div
        v-if="isOpen"
        class="datetime-picker-overlay"
        @click="closePicker"
      >
        <div
          class="datetime-picker-popup"
          :style="pickerPosition"
          @click.stop
        >
          <!-- Month/Year Navigation -->
          <div class="picker-header">
            <button @click="previousMonth" class="nav-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <div class="month-year-display">
              <span class="month">{{ currentMonthName }}</span>
              <span class="year">{{ currentYear }}</span>
            </div>
            <button @click="nextMonth" class="nav-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>

          <!-- Calendar Grid -->
          <div class="calendar-grid">
            <!-- Days of week header -->
            <div class="days-header">
              <div v-for="day in daysOfWeek" :key="day" class="day-header">{{ day }}</div>
            </div>
            
            <!-- Calendar dates -->
            <div class="calendar-dates">
              <div
                v-for="date in calendarDates"
                :key="date.key"
                class="calendar-date"
                :class="{
                  'other-month': !date.isCurrentMonth,
                  'selected': date.isSelected,
                  'today': date.isToday,
                  'clickable': date.isCurrentMonth
                }"
                @click="date.isCurrentMonth && selectDate(date.date)"
              >
                {{ date.day }}
              </div>
            </div>
          </div>

          <!-- Time Picker -->
          <div class="time-picker">
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
          </div>

          <!-- Action Buttons -->
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
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';

const props = defineProps({
  modelValue: String,
  placeholder: {
    type: String,
    default: 'Select date and time'
  },
  inputClass: {
    type: String,
    default: 'border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900'
  },
});

const emit = defineEmits(['update:modelValue', 'change']);

// Reactive data
const isOpen = ref(false);
const now = new Date();
const currentDate = ref(new Date(now.getFullYear(), now.getMonth(), 1));
const selectedDate = ref(now);
const selectedHour = ref(now.getHours() % 12 || 12);
const selectedMinute = ref(now.getMinutes());
const selectedPeriod = ref(now.getHours() >= 12 ? 'PM' : 'AM');
const pickerPosition = ref({ top: '0px', left: '0px' });

// Constants
const daysOfWeek = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

// Computed properties
const currentMonthName = computed(() => {
  return currentDate.value.toLocaleDateString('en-US', { month: 'long' });
});

const currentYear = computed(() => {
  return currentDate.value.getFullYear();
});

const displayValue = computed(() => {
  if (!selectedDate.value) return '';
  
  const date = new Date(selectedDate.value);
  const formattedDate = date.toLocaleDateString('en-US', {
    month: '2-digit',
    day: '2-digit',
    year: 'numeric'
  });
  
  const hour = selectedPeriod.value === 'PM' && selectedHour.value !== 12 
    ? selectedHour.value + 12 
    : selectedPeriod.value === 'AM' && selectedHour.value === 12 
    ? 0 
    : selectedHour.value;
  
  const formattedTime = `${hour.toString().padStart(2, '0')}:${selectedMinute.value.toString().padStart(2, '0')}`;
  
  return `${formattedDate} ${formattedTime} ${selectedPeriod.value}`;
});

const hours = computed(() => {
  return Array.from({ length: 12 }, (_, i) => i + 1);
});

const minutes = computed(() => {
  return Array.from({ length: 60 }, (_, i) => i);
});

const calendarDates = computed(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth();
  
  // Get first day of month and last day of month
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  
  // Get the day of week for first day (0 = Sunday, 1 = Monday, etc.)
  const firstDayOfWeek = firstDay.getDay();
  
  // Calculate dates to show (including previous month's dates to fill first week)
  const dates = [];
  
  // Add previous month's dates
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(year, month, -i);
    dates.push({
      date: date,
      day: date.getDate(),
      isCurrentMonth: false,
      isSelected: selectedDate.value && date.toDateString() === selectedDate.value.toDateString(),
      isToday: date.toDateString() === new Date().toDateString(),
      key: `prev-${date.getTime()}`
    });
  }
  
  // Add current month's dates
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const date = new Date(year, month, day);
    dates.push({
      date: date,
      day: day,
      isCurrentMonth: true,
      isSelected: selectedDate.value && date.toDateString() === selectedDate.value.toDateString(),
      isToday: date.toDateString() === new Date().toDateString(),
      key: `current-${date.getTime()}`
    });
  }
  
  // Add next month's dates to fill the last week
  const remainingDays = 42 - dates.length; // 6 rows * 7 days = 42
  for (let day = 1; day <= remainingDays; day++) {
    const date = new Date(year, month + 1, day);
    dates.push({
      date: date,
      day: date.getDate(),
      isCurrentMonth: false,
      isSelected: selectedDate.value && date.toDateString() === selectedDate.value.toDateString(),
      isToday: date.toDateString() === new Date().toDateString(),
      key: `next-${date.getTime()}`
    });
  }
  
  return dates;
});

// Methods
function calculatePosition() {
  nextTick(() => {
    const inputElement = document.querySelector('.custom-datetime-picker');
    if (!inputElement) return;
    
    const rect = inputElement.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    const pickerHeight = 450;
    const pickerWidth = 320;
    
    let top = rect.bottom + 4;
    let left = rect.left;
    
    // Check if there's enough space below
    if (rect.bottom + pickerHeight > viewportHeight) {
      top = rect.top - pickerHeight - 4;
    }
    
    // Check if there's enough space to the right
    if (rect.left + pickerWidth > viewportWidth) {
      left = viewportWidth - pickerWidth - 16;
    }
    
    // Ensure minimum left position
    if (left < 16) {
      left = 16;
    }
    
    // Ensure minimum top position
    if (top < 16) {
      top = 16;
    }
    
    pickerPosition.value = {
      top: `${top}px`,
      left: `${left}px`
    };
  });
}

function togglePicker() {
  if (isOpen.value) {
    // If already open, close it
    closePicker();
  } else {
    // If closed, open it and calculate position
    isOpen.value = true;
    calculatePosition();
    document.body.classList.add('picker-open');
  }
}

function closePicker() {
  isOpen.value = false;
  document.body.classList.remove('picker-open');
}

function previousMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1);
}

function nextMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1);
}

function selectDate(date) {
  selectedDate.value = date;
}

function clearSelection() {
  const now = new Date();
  selectedDate.value = now;
  selectedHour.value = now.getHours() % 12 || 12;
  selectedMinute.value = now.getMinutes();
  selectedPeriod.value = now.getHours() >= 12 ? 'PM' : 'AM';
}

function setToday() {
  const today = new Date();
  selectedDate.value = today;
  selectedHour.value = today.getHours() % 12 || 12;
  selectedMinute.value = today.getMinutes();
  selectedPeriod.value = today.getHours() >= 12 ? 'PM' : 'AM';
  currentDate.value = new Date(today.getFullYear(), today.getMonth(), 1);
}

function applySelection() {
  if (!selectedDate.value) {
    emit('update:modelValue', '');
    emit('change', '');
    closePicker();
    return;
  }
  
  // Create the final datetime
  const finalDate = new Date(selectedDate.value);
  let hour = selectedHour.value;
  
  if (selectedPeriod.value === 'PM' && hour !== 12) {
    hour += 12;
  } else if (selectedPeriod.value === 'AM' && hour === 12) {
    hour = 0;
  }
  
  finalDate.setHours(hour, selectedMinute.value, 0, 0);
  
  // Format as ISO datetime string (Frappe standard)
  const isoString = finalDate.toISOString().slice(0, 19).replace('T', ' ');
  
  console.log('DateTimePicker output:', isoString)
  emit('update:modelValue', isoString);
  emit('change', isoString);
  closePicker();
}

// Watch for external changes
watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      const date = new Date(val);
      if (!isNaN(date.getTime())) {
        selectedDate.value = date;
        selectedHour.value = date.getHours() % 12 || 12;
        selectedMinute.value = date.getMinutes();
        selectedPeriod.value = date.getHours() >= 12 ? 'PM' : 'AM';
        currentDate.value = new Date(date.getFullYear(), date.getMonth(), 1);
      }
    } else {
      // Set to current date and time when no value is provided
      const now = new Date();
      selectedDate.value = now;
      selectedHour.value = now.getHours() % 12 || 12;
      selectedMinute.value = now.getMinutes();
      selectedPeriod.value = now.getHours() >= 12 ? 'PM' : 'AM';
      currentDate.value = new Date(now.getFullYear(), now.getMonth(), 1);
      
      // Emit the default value so parent components know about it
      const isoString = now.toISOString().slice(0, 19).replace('T', ' ');
      emit('update:modelValue', isoString);
      console.log('DateTimePicker emitting default value:', isoString);
    }
  },
  { immediate: true }
);

// Handle window resize
function handleResize() {
  if (isOpen.value) {
    calculatePosition();
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  document.body.classList.remove('picker-open');
});
</script>

<style scoped>
.custom-datetime-picker {
  position: relative;
  display: inline-block;
}

.datetime-input-field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 200px;
  transition: all 0.15s ease-in-out;
  background-color: #f9fafb !important;
  border: 1px solid #d1d5db !important;
  border-radius: 6px !important;
  padding: 8px 12px !important;
  color: #374151 !important;
}

.datetime-input-field:hover {
  border-color: #9ca3af !important;
  background-color: #f3f4f6 !important;
}

.datetime-input-field:focus-within {
  outline: none;
  border-color: #000000 !important;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1) !important;
  background-color: #ffffff !important;
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
  position: fixed;
  background: #ffffff !important;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 16px;
  padding-bottom: 20px;
  width: 320px;
  max-height: 450px;
  overflow: hidden;
  z-index: 10000;
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
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
}

.calendar-date.today {
  background: #e5e7eb;
  color: #000000;
  font-weight: 600;
}

.calendar-date.selected {
  background: #000000;
  color: #ffffff;
  font-weight: 600;
}

.calendar-date.selected:hover {
  background: #374151;
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
  color: #ffffff;
  flex: 1;
}

.apply-btn:hover {
  background: #374151;
}

/* Prevent body scroll when picker is open */
:global(body.picker-open) {
  overflow: hidden;
}

/* Override any dark theme styles */
.datetime-picker-popup * {
  color: inherit !important;
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

.time-select {
  color: #000000 !important;
  background: #ffffff !important;
}
</style> 