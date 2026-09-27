<template>
  <section aria-labelledby="schedule-title" class=" px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
    <header class="mb-6 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 id="schedule-title" class="mt-1 text-3xl font-extrabold tracking-tight text-stone-950 sm:text-4xl">
          Interruptions Schedule
        </h1>
        <p class="mt-2 max-w-2xl text-base leading-7 text-stone-600">
          Scheduled maintenance and rotational brownouts. Search for your barangay or street,
          or pick a date to check whether your area is affected.
        </p>
      </div>

      <div class="flex shrink-0 flex-col gap-2 sm:items-end">
        <button
          type="button"
          :disabled="isRefreshing"
          :aria-busy="isRefreshing"
          class="inline-flex min-h-11 w-fit items-center justify-center gap-2 rounded-full bg-stone-900 px-5 text-sm font-bold text-white shadow-sm transition-colors duration-200 hover:bg-stone-700 disabled:cursor-wait disabled:opacity-70"
          @click="refreshSchedule"
        >
          <AppIcon name="refresh" :size="16" :class="{ 'animate-spin': isRefreshing }" />
          {{ isRefreshing ? 'Refreshing…' : 'Refresh schedule' }}
        </button>
        <p v-if="updatedLabel" class="text-xs text-stone-600">
          Last updated {{ updatedLabel }}
        </p>
      </div>
    </header>

    <div
      v-if="errorMessage && items.length"
      role="alert"
      class="mb-6 flex flex-col gap-3 rounded-2xl border border-amber-300 bg-amber-50 p-4 text-amber-950 sm:flex-row sm:items-center sm:justify-between"
    >
      <p class="flex items-start gap-2 text-sm">
        <AppIcon name="alert" class="mt-0.5 text-amber-700" />
        <span>
          <strong class="font-bold">Couldn't refresh the schedule.</strong>
          Showing the last loaded results.
        </span>
      </p>
      <button
        type="button"
        :disabled="isRefreshing"
        class="inline-flex min-h-11 w-fit shrink-0 items-center rounded-full px-4 text-sm font-bold text-amber-950 ring-1 ring-inset ring-amber-400 transition-colors duration-200 hover:bg-amber-100 disabled:cursor-wait disabled:opacity-70"
        @click="refreshSchedule"
      >
        Try again
      </button>
    </div>

    <form
      role="search"
      aria-label="Filter interruptions"
      class="mb-6 rounded-2xl border border-stone-200 bg-white p-4 shadow-sm sm:p-5"
      @submit.prevent
    >
      <div class="grid gap-4 md:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
        <div class="grid gap-2">
          <label for="interruption-search" class="text-sm font-bold text-stone-800">Search</label>
          <div class="relative">
            <AppIcon
              name="search"
              class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-500"
            />
            <input
              id="interruption-search"
              ref="searchInput"
              v-model="filters.search"
              type="search"
              autocomplete="off"
              enterkeyhint="search"
              placeholder="Barangay, street, or purpose"
              class="h-12 w-full rounded-xl border border-stone-300 bg-white pl-11 pr-12 text-base text-stone-950 outline-none transition-colors duration-200 placeholder:text-stone-500 focus:border-amber-700 focus:ring-4 focus:ring-amber-200 [&::-webkit-search-cancel-button]:hidden"
            >
            <button
              v-if="filters.search"
              type="button"
              aria-label="Clear search"
              class="absolute right-1 top-1/2 inline-flex size-10 -translate-y-1/2 items-center justify-center rounded-lg text-stone-500 transition-colors duration-200 hover:bg-stone-100 hover:text-stone-900"
              @click="clearSearch"
            >
              <AppIcon name="x" :size="16" />
            </button>
          </div>
        </div>

        <div class="grid gap-2">
          <div class="flex items-center justify-between gap-2">
            <label for="interruption-date" class="text-sm font-bold text-stone-800">Date</label>
            <button
              v-if="filters.date !== todayKey"
              type="button"
              class="-my-3 inline-flex min-h-11 items-center px-1 text-sm font-semibold text-amber-800 underline-offset-4 hover:text-amber-950 hover:underline"
              @click="filters.date = todayKey"
            >
              Jump to today
            </button>
          </div>
          <input
            id="interruption-date"
            v-model="filters.date"
            type="date"
            class="h-12 w-full rounded-xl border border-stone-300 bg-white px-4 text-base text-stone-950 outline-none transition-colors duration-200 focus:border-amber-700 focus:ring-4 focus:ring-amber-200"
          >
        </div>
      </div>

      <fieldset class="mt-4 border-t border-stone-100 pt-4">
        <legend class="sr-only">Interruption type</legend>
        <div class="flex flex-wrap items-center gap-2">
          <span class="mr-1 text-sm font-bold text-stone-800" aria-hidden="true">Type</span>
          <button
            v-for="option in categoryOptions"
            :key="option.value"
            type="button"
            class="inline-flex min-h-11 items-center gap-2 rounded-full px-4 text-sm font-semibold ring-1 ring-inset transition-colors duration-200"
            :class="
              filters.category === option.value
                ? 'bg-stone-900 text-white ring-stone-900'
                : 'bg-white text-stone-700 ring-stone-300 hover:bg-stone-100 hover:text-stone-950'
            "
            :aria-pressed="filters.category === option.value"
            @click="filters.category = option.value"
          >
            {{ option.label }}
            <span
              v-if="items.length"
              class="rounded-full px-2 py-0.5 text-xs font-bold tabular-nums"
              :class="filters.category === option.value ? 'bg-white/15 text-white' : 'bg-stone-100 text-stone-700'"
            >
              {{ categoryCounts[option.value] }}
            </span>
          </button>

          <button
            v-if="hasActiveFilters"
            type="button"
            class="inline-flex min-h-11 items-center gap-1.5 rounded-full px-4 text-sm font-semibold text-stone-700 transition-colors duration-200 hover:bg-stone-100 hover:text-stone-950 sm:ml-auto"
            @click="interruptionsStore.resetFilters"
          >
            <AppIcon name="x" :size="16" />
            Clear filters
          </button>
        </div>
      </fieldset>
    </form>

    <p class="sr-only" aria-live="polite">{{ liveSummary }}</p>

    <div
      v-if="isInitialLoading"
      class="grid gap-4 lg:grid-cols-2"
      role="status"
    >
      <span class="sr-only">Loading VECO's latest schedule…</span>
      <CardSkeleton v-for="index in 4" :key="index" />
    </div>

    <div
      v-else-if="errorMessage && !items.length"
      role="alert"
      class="flex flex-col items-start gap-4 rounded-2xl border border-red-200 bg-red-50 p-6 text-red-900"
    >
      <div class="flex items-start gap-3">
        <AppIcon name="alert" :size="24" class="mt-0.5 text-red-700" />
        <div>
          <h2 class="font-bold">We couldn't load the interruption schedule.</h2>
          <p class="mt-1 text-sm text-red-800">{{ errorMessage }} Check your connection and try again.</p>
        </div>
      </div>
      <button
        type="button"
        :disabled="isRefreshing"
        class="inline-flex min-h-11 items-center gap-2 rounded-full bg-red-700 px-5 text-sm font-bold text-white transition-colors duration-200 hover:bg-red-800 disabled:cursor-wait disabled:opacity-70"
        @click="refreshSchedule"
      >
        <AppIcon name="refresh" :size="16" :class="{ 'animate-spin': isRefreshing }" />
        {{ isRefreshing ? 'Retrying…' : 'Try again' }}
      </button>
    </div>

    <div
      v-else-if="!items.length"
      class="flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-900"
    >
      <AppIcon name="check" :size="24" class="mt-0.5 text-emerald-700" />
      <div>
        <h2 class="font-bold">No service interruptions are listed right now.</h2>
        <p class="mt-1 text-sm text-emerald-800">VECO hasn't posted any scheduled interruptions. Check back later.</p>
      </div>
    </div>

    <template v-else>
      <p class="mb-4 text-sm text-stone-600">
        Showing <span class="font-bold text-stone-900">{{ filteredItems.length }}</span>
        of {{ items.length }} interruptions<template v-if="groupedItems.length > 1">
          across {{ groupedItems.length }} days</template>
      </p>

      <div
        v-if="!filteredItems.length"
        class="rounded-2xl border border-dashed border-stone-300 bg-white px-6 py-10 text-center"
      >
        <AppIcon name="search" :size="32" class="mx-auto text-stone-400" />
        <h2 class="mt-3 font-bold text-stone-900">No interruptions match your filters</h2>
        <p class="mt-1 text-sm text-stone-600">
          Try a different spelling, another date, or a broader type.
        </p>
        <button
          type="button"
          class="mt-4 inline-flex min-h-11 items-center rounded-full bg-stone-900 px-5 text-sm font-bold text-white transition-colors duration-200 hover:bg-stone-700"
          @click="interruptionsStore.resetFilters"
        >
          Clear filters
        </button>
      </div>

      <div v-else class="grid gap-8">
        <template v-for="section in daySections" :key="section.key">
          <div
            v-if="section.divider"
            class="flex items-center gap-3 pt-2 text-sm font-bold uppercase tracking-wide text-stone-600"
          >
            <span class="h-px flex-1 bg-stone-200" aria-hidden="true" />
            {{ section.divider }}
            <span class="h-px flex-1 bg-stone-200" aria-hidden="true" />
          </div>

          <section
            v-for="group in section.groups"
            :key="group.date"
            :aria-labelledby="`day-${group.date}`"
          >
            <h2
              :id="`day-${group.date}`"
              class="sticky top-16 z-10 -mx-2 mb-3 flex flex-wrap items-center gap-2 bg-stone-50/95 px-2 py-2 text-base font-bold text-stone-900 backdrop-blur"
            >
              <AppIcon name="calendar" class="text-amber-700" />
              {{ group.label }}
              <span
                v-if="group.relative"
                class="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-bold text-amber-900"
              >
                {{ group.relative }}
              </span>
              <span class="ml-auto text-sm font-medium text-stone-600">
                {{ group.items.length }} {{ group.items.length === 1 ? 'interruption' : 'interruptions' }}
              </span>
            </h2>

            <ul class="grid gap-4 lg:grid-cols-2">
              <li v-for="interruption in group.items" :key="interruptionKey(interruption)">
                <InterruptionCard :interruption="interruption" :highlight="filters.search" />
              </li>
            </ul>
          </section>
        </template>
      </div>
    </template>
  </section>
</template>

<script setup>
definePageMeta({
  layout: 'main-layout',
  path: '/schedule',
})

useHead({
  title: 'Interruptions Schedule',
})

const route = useRoute()
const router = useRouter()
const interruptionsStore = useInterruptionsStore()
const {
  items,
  filteredItems,
  filters,
  hasActiveFilters,
  categoryCounts,
  isRefreshing,
  errorMessage,
  lastFetchedAt,
} = storeToRefs(interruptionsStore)

const categoryOptions = [
  { label: 'All interruptions', value: 'all' },
  { label: 'Scheduled', value: 'scheduled' },
  { label: 'Rotational Brownout', value: 'rotational' },
]

const searchInput = ref(null)
const todayKey = manilaDateKey()

// The URL is the source of truth for filters, so filtered views can be shared.
applyRouteQuery(route.query)

const { status } = await useAsyncData(
  'all-interruptions',
  () => interruptionsStore.fetchAll(),
)

const isInitialLoading = computed(() => status.value === 'pending' && items.value.length === 0)
const updatedLabel = computed(() => formatUpdatedAt(lastFetchedAt.value))
const groupedItems = computed(() =>
  groupByDate(filteredItems.value).map((group) => ({
    ...group,
    relative: relativeDayLabel(group.date, todayKey),
  })),
)
// Today and upcoming days come first; past days move under an "Earlier" divider.
const daySections = computed(() => {
  const current = groupedItems.value.filter((group) => group.date >= todayKey)
  const past = groupedItems.value.filter((group) => group.date < todayKey).reverse()

  return [
    { key: 'current', divider: '', groups: current },
    { key: 'past', divider: past.length && current.length ? 'Earlier' : '', groups: past },
  ]
})
const liveSummary = computed(() => {
  if (isInitialLoading.value || !items.value.length) return ''
  return `Showing ${filteredItems.value.length} of ${items.value.length} interruptions.`
})

watch(
  filters,
  (value) => {
    const query = buildQuery(value)
    if (!sameQuery(query, route.query)) router.replace({ query })
  },
  { deep: true },
)

watch(
  () => route.query,
  (query) => {
    if (!sameQuery(buildQuery(filters.value), query)) applyRouteQuery(query)
  },
)

function buildQuery(value) {
  const query = {}
  const search = value.search.trim()
  if (search) query.q = search
  if (value.category !== 'all') query.type = value.category
  if (value.date) query.date = value.date
  return query
}

function sameQuery(first, second) {
  const keys = ['q', 'type', 'date']
  return keys.every((key) => (first[key] || '') === (second[key] || ''))
}

function applyRouteQuery(query) {
  const search = typeof query.q === 'string' ? query.q : ''
  const category = categoryOptions.some((option) => option.value === query.type) ? query.type : 'all'
  const date = isDateKey(query.date) ? query.date : ''

  filters.value.search = search
  filters.value.category = category
  filters.value.date = date
}

function clearSearch() {
  filters.value.search = ''
  searchInput.value?.focus()
}

async function refreshSchedule() {
  try {
    await interruptionsStore.fetchAll()
  } catch {
    // The store exposes the API error through errorMessage.
  }
}
</script>
