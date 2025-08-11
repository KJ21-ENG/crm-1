import AsyncStorage from '@react-native-async-storage/async-storage'

const LOG_KEY = 'debugLogBuffer'
const MAX_LOGS = 500

function toLine(tag, message, data) {
  const ts = new Date().toISOString()
  let suffix = ''
  try {
    if (data !== undefined) suffix = ' ' + JSON.stringify(data)
  } catch (_) {
    try { suffix = ' ' + String(data) } catch (_) { suffix = '' }
  }
  return `[${ts}] [${tag}] ${message}${suffix}`
}

async function append(line) {
  try {
    const current = await AsyncStorage.getItem(LOG_KEY)
    let arr = []
    if (current) {
      try { arr = JSON.parse(current) || [] } catch (_) { arr = [] }
    }
    arr.push(line)
    if (arr.length > MAX_LOGS) arr = arr.slice(arr.length - MAX_LOGS)
    await AsyncStorage.setItem(LOG_KEY, JSON.stringify(arr))
  } catch (_) {}
}

export const DebugLogger = {
  async log(tag, message, data) {
    const line = toLine(tag, message, data)
    try { console.log(line) } catch (_) {}
    await append(line)
  },
  async error(tag, message, data) {
    const line = toLine(tag, 'ERROR: ' + message, data)
    try { console.error(line) } catch (_) { try { console.log(line) } catch (_) {} }
    await append(line)
  },
  async getAll() {
    try {
      const current = await AsyncStorage.getItem(LOG_KEY)
      return current ? JSON.parse(current) : []
    } catch (_) { return [] }
  },
  async clear() {
    try { await AsyncStorage.removeItem(LOG_KEY) } catch (_) {}
  }
}

export default DebugLogger


