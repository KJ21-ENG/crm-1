import { formatDate, timeAgo } from '@/utils'
import { getMeta } from '@/stores/meta'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Call Log')

function parseDurationToSeconds(val, fallback = 0) {
  if (val == null) return fallback
  if (typeof val === 'number' && !isNaN(val)) return val
  if (typeof val !== 'string') return fallback

  // Try HH:MM:SS or MM:SS
  if (val.includes(':')) {
    const parts = val.split(':').map((p) => parseInt(p, 10) || 0)
    if (parts.length === 3) {
      const [h, m, s] = parts
      return h * 3600 + m * 60 + s
    }
    if (parts.length === 2) {
      const [m, s] = parts
      return m * 60 + s
    }
  }

  // Try simple number inside string
  const num = parseFloat(val)
  return isNaN(num) ? fallback : num
}

export function getCallLogDetail(row, log, columns = []) {
  let incoming = log.type === 'Incoming'

  if (row === 'duration') {
    return {
      label: log._duration,
      icon: 'clock',
    }
  } else if (row === 'caller') {
    return {
      label: log._caller?.label,
      image: log._caller?.image,
    }
  } else if (row === 'employee') {
    // Show employee display name + avatar instead of raw id/email
    return {
      // Prefer explicit _employee.label, then employee_display, then fallback to employee
      label: log._employee?.label || log.employee_display || log.employee,
      image: log._employee?.image || null,
      // include underlying id so filters use the stored value (not the display label)
      name: log.employee,
    }
  } else if (row === 'receiver') {
    return {
      label: log._receiver?.label,
      image: log._receiver?.image,
    }
  } else if (row === 'type') {
    return {
      label: log.type,
      icon: incoming ? 'phone-incoming' : 'phone-outgoing',
    }
  } else if (row === 'status') {
    // Derive status label with strong precedence to duration
    const rawStatus = log.status
    const type = log.type // 'Incoming' | 'Outgoing'
    const dur = parseDurationToSeconds(log.duration, 0)

    // PRIMARY RULE: Any call with talk time (>0s) is Completed
    if (dur > 0) {
      return { label: 'Completed', color: 'green', name: 'Completed' }
    }

    // Map known provider statuses when duration is 0
    if (rawStatus === 'No Answer') {
      return {
        label: type === 'Outgoing' ? 'Did Not Pick' : 'Missed Call',
        color: 'red',
        // Underlying DB value used for filtering
        name: 'No Answer',
      }
    }

    if (rawStatus === 'Completed' || !rawStatus) {
      return {
        label: type === 'Outgoing' ? 'Did Not Pick' : 'Missed Call',
        color: 'red',
        name: 'No Answer',
      }
    }

    // Fallback to predefined maps for others (Busy/Failed/etc.)
    return {
      label: statusLabelMap[rawStatus] || rawStatus,
      color: statusColorMap[rawStatus] || 'gray',
      name: rawStatus,
    }
  } else if (['modified', 'creation', 'start_time'].includes(row)) {
    return {
      label: formatDate(log[row]),
      timeAgo: __(timeAgo(log[row])),
    }
  }

  let fieldType = columns?.find((col) => (col.key || col.value) == row)?.type

  if (fieldType && ['Date', 'Datetime'].includes(fieldType) && !['modified', 'creation', 'start_time'].includes(row)) {
    return formatDate(log[row], '', true, fieldType == 'Datetime')
  }

  if (fieldType && fieldType == 'Currency') {
    return getFormattedCurrency(row, log)
  }

  if (fieldType && fieldType == 'Float') {
    return getFormattedFloat(row, log)
  }

  if (fieldType && fieldType == 'Percent') {
    return getFormattedPercent(row, log)
  }

  return log[row]
}

export const statusLabelMap = {
  Completed: 'Completed',
  Initiated: 'Initiated',
  Busy: 'Declined',
  Failed: 'Failed',
  Queued: 'Queued',
  Canceled: 'Canceled',
  Ringing: 'Ringing',
  'No Answer': 'Missed Call',
  'In Progress': 'In Progress',
}

export const statusColorMap = {
  Completed: 'green',
  Busy: 'orange',
  Failed: 'red',
  Initiated: 'gray',
  Queued: 'gray',
  Canceled: 'gray',
  Ringing: 'gray',
  'No Answer': 'red',
  'In Progress': 'blue',
}
