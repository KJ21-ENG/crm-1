<template>
  <div class="custom-datetime-picker">
    <input
      type="datetime-local"
      v-model="datetimeValue"
      :class="inputClass"
      @change="emitChange"
      :placeholder="placeholder"
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

const datetimeValue = ref('');

// Helper function to format date as YYYY-MM-DDTHH:MM
function formatDateTimeLocal(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      const d = new Date(val);
      datetimeValue.value = formatDateTimeLocal(d);
    } else {
      datetimeValue.value = '';
    }
  },
  { immediate: true }
);

function emitChange() {
  if (datetimeValue.value) {
    try {
      // Create date from the datetime-local input value
      const dt = new Date(datetimeValue.value);

      // Validate the date
      if (isNaN(dt.getTime())) {
        console.warn('Invalid date from input:', datetimeValue.value);
        emit('update:modelValue', '');
        emit('change', '');
        return;
      }

      // Format as MySQL datetime string
      const mysqlString = dt.getFullYear() + '-' +
        String(dt.getMonth() + 1).padStart(2, '0') + '-' +
        String(dt.getDate()).padStart(2, '0') + ' ' +
        String(dt.getHours()).padStart(2, '0') + ':' +
        String(dt.getMinutes()).padStart(2, '0') + ':' +
        String(dt.getSeconds()).padStart(2, '0');

      emit('update:modelValue', mysqlString);
      emit('change', mysqlString);
    } catch (error) {
      console.error('Error processing date value:', error);
      emit('update:modelValue', '');
      emit('change', '');
    }
  } else {
    emit('update:modelValue', '');
    emit('change', '');
  }
}
</script>

<style scoped>
.custom-datetime-picker {
  display: flex;
  align-items: center;
}

input[type='datetime-local'] {
  font-size: 0.875rem;
  border-radius: 0.375rem;
  border: 1px solid #d1d5db;
  padding: 0.5rem 0.75rem;
  background: #ffffff;
  color: #374151;
  transition: all 0.15s ease-in-out;
  min-width: 200px;
}

input[type='datetime-local']:hover {
  border-color: #9ca3af;
}

input[type='datetime-local']:focus {
  outline: none;
  border-color: #6b7280;
  box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.1);
}

input[type='datetime-local']::placeholder {
  color: #9ca3af;
}

/* Custom styling for datetime-local input to match frappe theme */
input[type='datetime-local']::-webkit-calendar-picker-indicator {
  filter: invert(0.5);
  cursor: pointer;
}

input[type='datetime-local']::-webkit-calendar-picker-indicator:hover {
  filter: invert(0.3);
}

/* Firefox specific styling */
input[type='datetime-local']::-moz-calendar-picker-indicator {
  filter: invert(0.5);
  cursor: pointer;
}

input[type='datetime-local']::-moz-calendar-picker-indicator:hover {
  filter: invert(0.3);
}
</style> 