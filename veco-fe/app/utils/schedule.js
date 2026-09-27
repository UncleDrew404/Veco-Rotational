export const VECO_TIME_ZONE = 'Asia/Manila'

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]
const WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
const DATE_KEY_PATTERN = /^\d{4}-\d{2}-\d{2}$/

const STATUS_TONES = {
  ongoing: 'ongoing',
  active: 'ongoing',
  upcoming: 'upcoming',
  scheduled: 'upcoming',
  restored: 'done',
  completed: 'done',
  done: 'done',
  finished: 'done',
  cancelled: 'cancelled',
  canceled: 'cancelled',
  postponed: 'cancelled',
}

// Labels are built by hand so server-rendered and hydrated text always match.
function manilaParts(date) {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: VECO_TIME_ZONE,
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    hourCycle: 'h23',
  }).formatToParts(date)

  return Object.fromEntries(
    parts.filter((part) => part.type !== 'literal').map((part) => [part.type, Number(part.value)]),
  )
}

function pad(value) {
  return String(value).padStart(2, '0')
}

export function isDateKey(value) {
  return (
    typeof value === 'string' &&
    DATE_KEY_PATTERN.test(value) &&
    !Number.isNaN(Date.parse(`${value}T00:00:00Z`))
  )
}

export function manilaDateKey(date = new Date()) {
  const { year, month, day } = manilaParts(date)
  return `${year}-${pad(month)}-${pad(day)}`
}

export function shiftDateKey(dateKey, days) {
  const date = new Date(`${dateKey}T00:00:00Z`)
  date.setUTCDate(date.getUTCDate() + days)
  return date.toISOString().slice(0, 10)
}

export function formatDateKey(dateKey, { weekday = true } = {}) {
  if (!isDateKey(dateKey)) return ''

  const date = new Date(`${dateKey}T00:00:00Z`)
  const label = `${MONTHS[date.getUTCMonth()]} ${date.getUTCDate()}, ${date.getUTCFullYear()}`
  return weekday ? `${WEEKDAYS[date.getUTCDay()]}, ${label}` : label
}

export function relativeDayLabel(dateKey, todayKey) {
  if (!isDateKey(dateKey) || !isDateKey(todayKey)) return ''
  if (dateKey === todayKey) return 'Today'
  if (dateKey === shiftDateKey(todayKey, 1)) return 'Tomorrow'
  if (dateKey === shiftDateKey(todayKey, -1)) return 'Yesterday'
  return ''
}

export function formatUpdatedAt(isoString) {
  if (!isoString) return ''

  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) return ''

  const { month, day, hour, minute } = manilaParts(date)
  const suffix = hour >= 12 ? 'PM' : 'AM'
  return `${MONTHS[month - 1].slice(0, 3)} ${day}, ${hour % 12 || 12}:${pad(minute)} ${suffix}`
}

export function occursOn(interruption, dateKey) {
  const start = interruption?.date_start
  const end = interruption?.date_end || start
  return Boolean(start) && start <= dateKey && end >= dateKey
}

export function groupByDate(interruptions) {
  const groups = new Map()

  for (const interruption of interruptions) {
    const key = interruption.date_start || 'unscheduled'
    if (!groups.has(key)) {
      groups.set(key, {
        date: key,
        label: formatDateKey(key) || interruption.date_label || 'Date to be announced',
        items: [],
      })
    }
    groups.get(key).items.push(interruption)
  }

  return [...groups.values()].sort((first, second) => first.date.localeCompare(second.date))
}

export function statusTone(status) {
  return STATUS_TONES[status?.trim().toLowerCase()] || 'neutral'
}

export function interruptionKey(interruption) {
  return [
    interruption.source_id,
    interruption.date_start,
    interruption.time,
    interruption.areas_affected,
  ].join('-')
}

export function highlightParts(text, query) {
  const value = text || ''
  const needle = query?.trim().toLowerCase()
  if (!needle) return [{ text: value, match: false }]

  const haystack = value.toLowerCase()
  const parts = []
  let index = 0

  while (index < value.length) {
    const found = haystack.indexOf(needle, index)
    if (found === -1) {
      parts.push({ text: value.slice(index), match: false })
      break
    }
    if (found > index) parts.push({ text: value.slice(index, found), match: false })
    parts.push({ text: value.slice(found, found + needle.length), match: true })
    index = found + needle.length
  }

  return parts
}
