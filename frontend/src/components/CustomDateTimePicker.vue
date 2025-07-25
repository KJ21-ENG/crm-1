<template>
  <div class="custom-datetime-picker">
    <input
      type="date"
      v-model="date"
      :class="inputClass"
      @change="emitChange"
    />
    <input
      type="time"
      v-model="time"
      :class="inputClass"
      step="60"
      @change="emitChange"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: String,
  placeholder: String,
  inputClass: {
    type: String,
    default: 'border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-gray-500 bg-white text-gray-900',
  },
});
const emit = defineEmits(['update:modelValue', 'change']);

const date = ref('');
const time = ref('');

// Helper function to format date as YYYY-MM-DD
function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// Helper function to format time as HH:MM
function formatTime(date) {
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      const d = new Date(val);
      date.value = formatDate(d);
      time.value = formatTime(d);
    } else {
      date.value = '';
      time.value = '';
    }
  },
  { immediate: true }
);

function emitChange() {
  if (date.value && time.value) {
    const dt = new Date(`${date.value}T${time.value}`);
    emit('update:modelValue', dt.toISOString());
    emit('change', dt.toISOString());
  } else {
    emit('update:modelValue', '');
    emit('change', '');
  }
}
</script>

<style scoped>
.custom-datetime-picker {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

input[type='date'],
input[type='time'] {
  font-size: 0.875rem;
  border-radius: 0.375rem;
  border: 1px solid #d1d5db;
  padding: 0.5rem 0.75rem;
  background: #ffffff;
  color: #374151;
  transition: all 0.15s ease-in-out;
  min-width: 120px;
}

input[type='date']:hover,
input[type='time']:hover {
  border-color: #9ca3af;
}

input[type='date']:focus,
input[type='time']:focus {
  outline: none;
  border-color: #6b7280;
  box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.1);
}

input[type='date']::placeholder,
input[type='time']::placeholder {
  color: #9ca3af;
}

/* Custom styling for date/time inputs to match frappe theme */
input[type='date']::-webkit-calendar-picker-indicator,
input[type='time']::-webkit-calendar-picker-indicator {
  filter: invert(0.5);
  cursor: pointer;
}

input[type='date']::-webkit-calendar-picker-indicator:hover,
input[type='time']::-webkit-calendar-picker-indicator:hover {
  filter: invert(0.3);
}
</style> 