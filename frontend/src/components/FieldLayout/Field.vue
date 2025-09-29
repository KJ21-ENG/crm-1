<template>
  <div v-if="field.visible && shouldRenderField(field)" class="field w-full">
    <div v-if="field.fieldtype != 'Check' && field.label" class="mb-2 text-sm text-ink-gray-5 truncate" style="min-height:20px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
      {{ __(field.label) }}
      <span
        v-if="
          field.reqd ||
          (field.mandatory_depends_on && field.mandatory_via_depends_on) ||
          field.fieldname === 'ticket_subject' ||
          field.fieldname === 'ticket_subjects'
        "
        class="text-ink-red-2"
        >*</span
      >
    </div>
    <FormControl
      v-if="
        field.read_only &&
        !['Int', 'Float', 'Currency', 'Percent', 'Check'].includes(
          field.fieldtype,
        )
      "
      type="text"
      :placeholder="getPlaceholder(field)"
      v-model="data[field.fieldname]"
      :disabled="true"
      :description="field.description"
    />
    <Grid
      v-else-if="field.fieldtype === 'Table'"
      v-model="data[field.fieldname]"
      v-model:parent="data"
      :doctype="field.options"
      :parentDoctype="doctype"
      :parentFieldname="field.fieldname"
    />
    <FormControl
      v-else-if="field.fieldtype === 'Select'"
      type="select"
      class="form-control"
      :class="field.prefix ? 'prefix' : ''"
      :options="field.options"
      v-model="data[field.fieldname]"
      @change="(e) => fieldChange(e.target.value, field)"
      :placeholder="getPlaceholder(field)"
      :description="field.description"
    >
      <template v-if="field.prefix" #prefix>
        <IndicatorIcon :class="field.prefix" />
      </template>
    </FormControl>
    <div v-else-if="field.fieldtype == 'Check'" class="flex items-center gap-2">
      <FormControl
        class="form-control"
        type="checkbox"
        v-model="data[field.fieldname]"
        @change="(e) => fieldChange(e.target.checked, field)"
        :disabled="Boolean(field.read_only)"
        :description="field.description"
      />
      <label
        class="text-sm text-ink-gray-5"
        @click="
          () => {
            if (!Boolean(field.read_only)) {
              data[field.fieldname] = !data[field.fieldname]
            }
          }
        "
      >
        {{ __(field.label) }}
        <span class="text-ink-red-3" v-if="field.mandatory">*</span>
      </label>
    </div>
    <div
      class="flex gap-1"
      v-else-if="['Link', 'Dynamic Link'].includes(field.fieldtype)"
    >
      <!-- Special handling for ticket subject field -->
      <TicketSubjectInput
        v-if="field.fieldname === 'ticket_subject' && field.options === 'CRM Ticket Subject'"
        class="form-control flex-1 truncate"
        :value="data[field.fieldname]"
        :doctype="field.options"
        :filters="field.filters"
        @change="(v) => fieldChange(v, field)"
        :placeholder="getPlaceholder(field)"
      />
      <!-- Special handling for account type: allow inline creation like ticket subject -->
      <AccountTypeInput
        v-else-if="field.fieldname === 'account_type' && field.options === 'CRM Account Type'"
        class="form-control flex-1 truncate"
        :value="data[field.fieldname]"
        :doctype="field.options"
        :filters="field.filters"
        @change="(v) => fieldChange(v, field)"
        :placeholder="getPlaceholder(field)"
      />
      <Link
        v-else
        class="form-control flex-1 truncate"
        :value="data[field.fieldname]"
        :doctype="
          field.fieldtype == 'Link' ? field.options : data[field.options]
        "
        :filters="field.filters"
        @change="(v) => fieldChange(v, field)"
        :placeholder="getPlaceholder(field)"
        :onCreate="field.create"
      />
      <Button
        v-if="data[field.fieldname] && field.edit"
        class="shrink-0"
        :label="__('Edit')"
        @click="field.edit(data[field.fieldname])"
      >
        <template #prefix>
          <EditIcon class="h-4 w-4" />
        </template>
      </Button>
    </div>

    <TableMultiselectInput
      v-else-if="field.fieldtype === 'Table MultiSelect'"
      v-model="data[field.fieldname]"
      :doctype="field.options"
      :placeholder="getPlaceholder(field)"
      @change="(v) => fieldChange(v, field)"
    />

    <Link
      v-else-if="field.fieldtype === 'User'"
      class="form-control"
      :value="data[field.fieldname] && getUser(data[field.fieldname]).full_name"
      :doctype="field.options"
      :filters="field.filters"
      @change="(v) => fieldChange(v, field)"
      :placeholder="getPlaceholder(field)"
      :hideMe="true"
    >
      <template #prefix>
        <UserAvatar
          v-if="data[field.fieldname]"
          class="mr-2"
          :user="data[field.fieldname]"
          size="sm"
        />
      </template>
      <template #item-prefix="{ option }">
        <UserAvatar class="mr-2" :user="option.value" size="sm" />
      </template>
      <template #item-label="{ option }">
        <Tooltip :text="option.value">
          <div class="cursor-pointer">
            {{ getUser(option.value).full_name }}
          </div>
        </Tooltip>
      </template>
    </Link>
    <div v-else-if="field.fieldtype === 'Datetime'" class="relative">
      <div @click="focusDateTimeInput" class="absolute inset-0 cursor-pointer z-10"></div>
      <CustomDateTimePicker
        ref="dateTimeInputRef"
        :model-value="data[field.fieldname]"
        :placeholder="getPlaceholder(field)"
        :input-class="'border-none'"
        @update:modelValue="(v) => fieldChange(v, field)"
      />
    </div>
    <div v-else-if="field.fieldtype === 'Date'" class="relative">
      <CustomDateTimePicker
        :model-value="data[field.fieldname]"
        :placeholder="getPlaceholder(field)"
        :input-class="'border-none'"
        :mode="'date'"
        :show-time="false"
        :auto-default="false"
        :year-quick-select="true"
        @update:modelValue="(v) => fieldChange(v, field)"
      />
    </div>
    <FormControl
      v-else-if="
        ['Small Text', 'Text', 'Long Text', 'Code'].includes(field.fieldtype)
      "
      type="textarea"
      :value="data[field.fieldname]"
      :placeholder="getPlaceholder(field)"
      :description="field.description"
      @change="fieldChange($event.target.value, field)"
    />
    <Password
      v-else-if="field.fieldtype === 'Password'"
      :value="data[field.fieldname]"
      :placeholder="getPlaceholder(field)"
      :description="field.description"
      @change="fieldChange($event.target.value, field)"
    />
    <FormattedInput
      v-else-if="field.fieldtype === 'Int'"
      type="text"
      :placeholder="getPlaceholder(field)"
      :value="data[field.fieldname] || '0'"
      :disabled="Boolean(field.read_only)"
      :description="field.description"
      @change="fieldChange($event.target.value, field)"
    />
    <FormattedInput
      v-else-if="field.fieldtype === 'Percent'"
      type="text"
      :value="getFormattedPercent(field.fieldname, data)"
      :placeholder="getPlaceholder(field)"
      :disabled="Boolean(field.read_only)"
      :description="field.description"
      @change="fieldChange(flt($event.target.value), field)"
    />
    <FormattedInput
      v-else-if="field.fieldtype === 'Float'"
      type="text"
      :value="getFormattedFloat(field.fieldname, data)"
      :placeholder="getPlaceholder(field)"
      :disabled="Boolean(field.read_only)"
      :description="field.description"
      @change="fieldChange(flt($event.target.value), field)"
    />
    <FormattedInput
      v-else-if="field.fieldtype === 'Currency'"
      type="text"
      :value="getFormattedCurrency(field.fieldname, data, parentDoc)"
      :placeholder="getPlaceholder(field)"
      :disabled="Boolean(field.read_only)"
      :description="field.description"
      @change="fieldChange(flt($event.target.value), field)"
    />
    <Button
      v-else-if="field.fieldtype === 'Button'"
      :variant="field.buttonVariant || 'outline'"
      :size="field.buttonSize || 'sm'"
      :label="field.buttonLabel || field.label"
      :icon="field.buttonIcon"
      :disabled="Boolean(field.read_only)"
      @click="field.onClick && field.onClick()"
      class="mt-1"
    />
    <!-- <FormControl
      v-else
      type="text"
      :placeholder="getPlaceholder(field)"
      :value="getDataValue(data[field.fieldname], field)"
      :disabled="Boolean(field.read_only)"
      :description="field.description"
      @change="fieldChange($event.target.value, field)"
    /> -->
    <div v-else class="flex items-center gap-2 w-full">
      <FormControl
        class="flex-1"
        type="text"
        :placeholder="getPlaceholder(field)"
        :value="getDataValue(data[field.fieldname], field)"
        :disabled="Boolean(field.read_only)"
        :description="field.description"
        @change="fieldChange($event.target.value, field)"
      />

      <!-- Only show Swap for mobile_no -->
      <Tooltip text="Swap Mobile with Alternate">
        <Button
          v-if="field.fieldname === 'mobile_no'"
          size="sm"
          variant="outline"
          @click="$emit('swap')"
        >
          <FeatherIcon name="repeat" class="h-2 w-2" />
        </Button>
      </Tooltip>
    </div>

  </div>
</template>
<script setup>
import Password from '@/components/Controls/Password.vue'
import FormattedInput from '@/components/Controls/FormattedInput.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import TableMultiselectInput from '@/components/Controls/TableMultiselectInput.vue'
import Link from '@/components/Controls/Link.vue'
import TicketSubjectInput from '@/components/Controls/TicketSubjectInput.vue'
import AccountTypeInput from '@/components/Controls/AccountTypeInput.vue'
import Grid from '@/components/Controls/Grid.vue'
import { createDocument } from '@/composables/document'
import { getFormat, evaluateDependsOnValue } from '@/utils'
import { flt } from '@/utils/numberFormat.js'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { useDocument } from '@/data/document'
import { Tooltip, DatePicker } from 'frappe-ui'
import { ref, computed, provide, inject, nextTick } from 'vue'
import CustomDateTimePicker from '../CustomDateTimePicker.vue'

const props = defineProps({
  field: Object,
})

const data = inject('data')
const doctype = inject('doctype')
const preview = inject('preview')
const isGridRow = inject('isGridRow')

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta(doctype)

const { users, getUser } = usersStore()

let triggerOnChange
let parentDoc

if (!isGridRow) {
  const {
    triggerOnChange: trigger,
    triggerOnRowAdd,
    triggerOnRowRemove,
  } = useDocument(doctype, data.value.name)
  triggerOnChange = trigger

  provide('triggerOnChange', triggerOnChange)
  provide('triggerOnRowAdd', triggerOnRowAdd)
  provide('triggerOnRowRemove', triggerOnRowRemove)
} else {
  triggerOnChange = inject('triggerOnChange', () => {})
  parentDoc = inject('parentDoc')
}

const field = computed(() => {
  let field = props.field
  if (field.fieldtype == 'Select' && typeof field.options === 'string') {
    field.options = field.options.split('\n').map((option) => {
      return { label: option, value: option }
    })

    if (field.options[0].value !== '') {
      field.options.unshift({ label: '', value: '' })
    }
  }

  if (field.fieldtype === 'Link' && field.options === 'User') {
    field.fieldtype = 'User'
    field.link_filters = JSON.stringify({
      ...(field.link_filters ? JSON.parse(field.link_filters) : {}),
      name: ['in', users.data.crmUsers?.map((user) => user.name)],
    })
  }

  if (field.fieldtype === 'Link' && field.options !== 'User') {
    if (!field.create) {
      field.create = (value, close) => {
        const callback = (d) => {
          if (d) fieldChange(d.name, field)
        }
        createDocument(field.options, value, close, callback)
      }
    }
  }

  let _field = {
    ...field,
    filters: field.link_filters && JSON.parse(field.link_filters),
    placeholder: field.placeholder || field.label,
    display_via_depends_on: evaluateDependsOnValue(
      field.depends_on,
      data.value,
    ),
    mandatory_via_depends_on: evaluateDependsOnValue(
      field.mandatory_depends_on,
      data.value,
    ),
  }

  _field.visible = isFieldVisible(_field)
  return _field
})

function isFieldVisible(field) {
  if (preview.value) return true
  // Always respect depends_on/hidden, but do not hide read-only fields when empty
  return (!field.depends_on || field.display_via_depends_on) && !field.hidden
}

const shouldRenderField = (field) => {
  // Don't render fields without labels or with empty labels
  if (!field.label || field.label.trim() === '') {
    return false
  }
  
  // Don't render hidden fields
  if (field.hidden) {
    return false
  }
  
  // Section breaks and column breaks should not render as input fields
  if (['Section Break', 'Column Break', 'Tab Break'].includes(field.fieldtype)) {
    return false
  }
  
  return true
}

const getPlaceholder = (field) => {
  if (field.placeholder) {
    return __(field.placeholder)
  }
  
  // Only show placeholder if field has a proper label
  if (!field.label || field.label.trim() === '') {
    console.warn('Field without proper label detected:', field)
    return ''
  }
  
  if (['Select', 'Link'].includes(field.fieldtype)) {
    return __('Select {0}', [__(field.label)])
  } else {
    return __('Enter {0}', [__(field.label)])
  }
}

function fieldChange(value, df) {
  if (isGridRow) {
    triggerOnChange(df.fieldname, value, data.value)
  } else {
    triggerOnChange(df.fieldname, value)
  }
}

function getDataValue(value, field) {
  if (field.fieldtype === 'Duration') {
    return value || 0
  }
  return value
}

const dateTimeInputRef = ref(null)
function focusDateTimeInput() {
  nextTick(() => {
    if (dateTimeInputRef.value && dateTimeInputRef.value.$el) {
      const input = dateTimeInputRef.value.$el.querySelector('input')
      if (input) input.focus()
    }
  })
}
</script>
<style scoped>
:deep(.form-control.prefix select) {
  padding-left: 2rem;
}
</style>
