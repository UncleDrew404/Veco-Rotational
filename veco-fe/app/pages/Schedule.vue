<template>
  <section>
    <div class="mb-8 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="max-w-3xl text-3xl font-black tracking-tight text-slate-950 sm:text-4xl">
          Interruptions Schedule
        </h1>
      </div>

      <button
        type="button"
        :disabled="isRefreshing"
        class="inline-flex w-fit items-center justify-center rounded-full bg-blue-700 px-5 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-blue-800 disabled:cursor-wait disabled:opacity-60"
        @click="refreshSchedule"
      >
        {{ isRefreshing ? 'Refreshing…' : 'Refresh schedule' }}
      </button>
    </div>

    <div class="mb-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div class="grid gap-5 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
        <div class="grid gap-5 sm:grid-cols-2">
          <label class="grid gap-2 text-sm font-bold text-slate-700">
            Search Interruptions
            <input
              v-model="filters.search"
              type="search"
              placeholder="Search area, purpose, or time"
              class="h-11 rounded-xl border border-slate-300 bg-white px-4 font-normal text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-blue-600 focus:ring-4 focus:ring-blue-100"
            >
          </label>

          <label class="grid gap-2 text-sm font-bold text-slate-700">
            Date
            <input
              v-model="filters.date"
              type="date"
              class="h-11 rounded-xl border border-slate-300 bg-white px-4 font-normal text-slate-950 outline-none transition focus:border-blue-600 focus:ring-4 focus:ring-blue-100"
            >
          </label>
        </div>

        <button
          v-if="hasActiveFilters"
          type="button"
          class="h-11 w-fit rounded-xl border border-slate-300 px-4 text-sm font-bold text-slate-700 transition hover:border-blue-300 hover:bg-blue-50 hover:text-blue-800"
          @click="interruptionsStore.resetFilters"
        >
          Clear filters
        </button>
      </div>

      <fieldset class="mt-5 border-t border-slate-100 pt-5">
        <legend class="sr-only">Interruption type</legend>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="option in categoryOptions"
            :key="option.value"
            type="button"
            class="rounded-full px-4 py-2 text-sm font-bold transition ring-1 ring-inset"
            :class="
              filters.category === option.value
                ? 'bg-blue-700 text-white ring-blue-700'
                : 'bg-slate-50 text-slate-700 ring-slate-200 hover:bg-blue-50 hover:text-blue-800 hover:ring-blue-200'
            "
            :aria-pressed="filters.category === option.value"
            @click="filters.category = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </fieldset>
    </div>

    <div
      v-if="status === 'pending' && items.length === 0"
      class="grid gap-5 md:grid-cols-2 xl:grid-cols-3"
      role="status"
      aria-live="polite"
    >
      <span class="sr-only">Loading VECO’s latest schedule…</span>
      <CardSkeleton v-for="index in 6" :key="index" />
    </div>

    <div
      v-else-if="errorMessage && items.length === 0"
      class="grid gap-1 rounded-2xl border border-red-200 bg-red-50 p-6 text-red-800 shadow-sm"
    >
      <strong>Unable to load the interruption calendar.</strong>
      <span>{{ errorMessage }}</span>
    </div>

    <div
      v-else-if="items.length === 0"
      class="rounded-2xl border border-slate-200 bg-white p-6 text-slate-600 shadow-sm"
    >
      No service interruptions are currently listed.
    </div>

    <div
      v-else-if="filteredItems.length === 0"
      class="rounded-2xl border border-slate-200 bg-white p-6 text-slate-600 shadow-sm"
    >
      <p class="font-bold text-slate-900">No interruptions match these filters.</p>
      <button
        type="button"
        class="mt-3 text-sm font-bold text-blue-700 hover:text-blue-900 hover:underline"
        @click="interruptionsStore.resetFilters"
      >
        Clear filters
      </button>
    </div>

    <template v-else>
      <p class="mb-4 text-sm font-semibold text-slate-600">
        Showing {{ filteredItems.length }} of {{ items.length }} interruptions
      </p>

      <!-- CARDS -->
      <div class="grid gap-5 " aria-label="Filtered interruption schedule">
        <article
          v-for="interruption in filteredItems"
          :key="`${interruption.source_id}-${interruption.date_start}-${interruption.time}-${interruption.areas_affected}`"
          class="flex flex-col gap-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div class="flex items-center justify-between gap-3">
            <span
              class="rounded-full px-2.5 py-1 text-xs font-extrabold uppercase tracking-wide ring-1 ring-inset"
              :class="badgeClass(interruption.status)"
            >
              {{ interruption.status || 'Scheduled' }}
            </span>
            <span class="text-xs font-extrabold uppercase tracking-wider text-blue-700">
              {{ interruption.category }}
            </span>
          </div>

          <div>
            <p class="text-sm font-extrabold text-blue-800">
              {{ interruption.date_label }}
            </p>
            <p class="mt-1 text-base font-extrabold text-slate-700">
              {{ interruption.time }}
            </p>
          </div>

          <h2 class="text-base font-bold leading-7 text-slate-950">
            {{ interruption.purpose }}
          </h2>

          <div class="border-t border-slate-100 pt-4">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Areas affected</span>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              {{ interruption.areas_affected }}
            </p>
          </div>

          <a
            v-if="interruption.map_url"
            :href="interruption.map_url"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-auto w-fit text-sm font-bold text-blue-700 hover:text-blue-900 hover:underline"
          >
            View outage map
          </a>
        </article>
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

const config = useRuntimeConfig()
const interruptionsStore = useInterruptionsStore()
const { items, filteredItems, filters, hasActiveFilters, isRefreshing, errorMessage } =
  storeToRefs(interruptionsStore)

const categoryOptions = [
  { label: 'All interruptions', value: 'all' },
  { label: 'Scheduled', value: 'scheduled' },
  { label: 'Rotational Brownout', value: 'rotational' },
]

const { data, status, error } = await useFetch('/api/v1/interruptions/', {
  baseURL: config.public.apiBase,
  key: 'all-interruptions',
})

if (data.value) {
  interruptionsStore.setResponse(data.value)
}

if (error.value) {
  interruptionsStore.setError(error.value?.data?.message || error.value.message)
}

const statusClasses = {
  ongoing: 'bg-red-100 text-red-700 ring-red-600/20',
  restored: 'bg-emerald-100 text-emerald-700 ring-emerald-600/20',
  upcoming: 'bg-amber-100 text-amber-800 ring-amber-600/20',
}

function badgeClass(value) {
  return statusClasses[value?.toLowerCase()] || 'bg-slate-100 text-slate-700 ring-slate-600/20'
}

async function refreshSchedule() {
  try {
    await interruptionsStore.fetchAll()
  } catch {
    // The store exposes the API error through errorMessage.
  }
}
</script>
