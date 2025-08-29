import { formatDate, timeAgo } from '@/utils'
import { getMeta } from '@/stores/meta'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Call Log')

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
    // Derive status label with call direction + duration overrides
    const rawStatus = log.status
    const type = log.type // 'Incoming' | 'Outgoing'
    const dur = typeof log.duration === 'number' ? log.duration : parseFloat(log.duration || '0')

    // 1) If provider sent 'No Answer', map by direction
    if (rawStatus === 'No Answer') {
      return {
        label: type === 'Outgoing' ? 'Did Not Pick' : 'Missed Call',
        color: 'red',
      }
    }

    // 2) If status is Completed but duration is 0, fix based on direction
    if ((rawStatus === 'Completed' || !rawStatus) && (isNaN(dur) || dur === 0)) {
      return {
        label: type === 'Outgoing' ? 'Did Not Pick' : 'Missed Call',
        color: 'red',
      }
    }

    // 3) Otherwise fall back to predefined maps
    return {
      label: statusLabelMap[rawStatus] || rawStatus,
      color: statusColorMap[rawStatus] || 'gray',
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
