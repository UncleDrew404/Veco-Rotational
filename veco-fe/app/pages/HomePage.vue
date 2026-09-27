<template>
  <div class="grid gap-5">
    <section
      aria-labelledby="home-title"
      class="relative overflow-hidden bg-stone-900 px-6 py-10 text-white shadow-sm sm:px-10 sm:py-14"
    >
      <div class="relative max-w-2xl">
        <p class="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-sm font-semibold text-amber-300 ring-1 ring-inset ring-white/15">
          <AppIcon name="zap" :size="16" />
          VECO service area
        </p>
        <h1 id="home-title" class="mt-5 text-3xl font-extrabold tracking-tight text-balance sm:text-5xl">
          Know about power interruptions before they reach your street.
        </h1>
        <p class="mt-4 text-base leading-7 text-stone-300 sm:text-lg">
          Scheduled maintenance and rotational brownouts from VECO in one place.
          Search for your barangay or pick a date to see if you're affected.
        </p>
        <div class="mt-8 flex flex-wrap gap-3">
          <NuxtLink
            :to="{ path: '/schedule', query: { date: todayKey } }"
            class="inline-flex min-h-11 items-center gap-2 rounded-full bg-amber-400 px-5 text-sm font-bold text-stone-950 transition-colors duration-200 hover:bg-amber-300 focus-visible:outline-amber-300"
          >
            Today's schedule
            <AppIcon name="arrow-right" :size="16" />
          </NuxtLink>
        </div>
      </div>
      <img
        :src="rotationalLogo"
        alt=""
        width="288"
        height="288"
        class="pointer-events-none absolute -bottom-16 -right-16 hidden size-72 opacity-15 md:block"
      >
    </section>

    <!-- CARD STAT -->
    <section aria-labelledby="overview-title" class="px-4 sm:px-6 lg:px-8 ">
      <h2 id="overview-title" class="sr-only">Overview</h2>

      <div v-if="isInitialLoading" class="grid gap-4 sm:grid-cols-3" role="status">
        <span class="sr-only">Loading VECO's latest schedule…</span>
        <div
          v-for="index in 3"
          :key="index"
          aria-hidden="true"
          class="h-32 animate-pulse rounded-2xl border border-stone-200 bg-white"
        />
      </div>

      <div
        v-else-if="errorMessage && !items.length"
        role="alert"
        class="flex flex-col items-start gap-4 rounded-2xl border border-red-200 bg-red-50 p-6 text-red-900 sm:flex-row sm:items-center sm:justify-between"
      >
        <div class="flex items-start gap-3">
          <AppIcon name="alert" :size="24" class="mt-0.5 text-red-700" />
          <div>
            <p class="font-bold">We couldn't load the interruption schedule.</p>
            <p class="mt-1 text-sm text-red-800">{{ errorMessage }} Check your connection and try again.</p>
          </div>
        </div>
        <button
          type="button"
          :disabled="isRefreshing"
          class="inline-flex min-h-11 shrink-0 items-center gap-2 rounded-full bg-red-700 px-5 text-sm font-bold text-white transition-colors duration-200 hover:bg-red-800 disabled:cursor-wait disabled:opacity-70"
          @click="retry"
        >
          <AppIcon name="refresh" :size="16" :class="{ 'animate-spin': isRefreshing }" />
          {{ isRefreshing ? 'Retrying…' : 'Try again' }}
        </button>
      </div>

      <ul v-else class="grid gap-4 sm:grid-cols-3">
        <li v-for="stat in stats" :key="stat.label">
          <NuxtLink
            :to="stat.to"
            class="group flex h-full flex-col rounded-2xl border border-stone-200 bg-white p-5 shadow-sm"
          >
            <span class="text-sm font-semibold text-stone-600">{{ stat.label }}</span>
            <span class="mt-2 text-4xl font-extrabold tabular-nums text-stone-950">{{ stat.value }}</span>
            <span class="mt-1 flex items-center justify-between gap-2 text-sm text-stone-600">
              {{ stat.caption }}
              <AppIcon
                name="arrow-right"
                :size="16"
                class="text-stone-400 transition-colors duration-200 group-hover:text-amber-800"
              />
            </span>
          </NuxtLink>
        </li>
      </ul>
    </section>

    <section v-if="isInitialLoading" aria-hidden="true" class="grid gap-4 lg:grid-cols-2">
      <CardSkeleton v-for="index in 2" :key="index" />
    </section>

    <section v-else-if="items.length" aria-labelledby="spotlight-title" class="px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
      <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 id="spotlight-title" class="text-xl font-bold text-stone-950">{{ spotlight.title }}</h2>
          <p class="mt-1 text-sm text-stone-600">{{ spotlight.subtitle }}</p>
        </div>
        <NuxtLink
          v-if="spotlight.items.length"
          :to="spotlight.to"
          class="inline-flex min-h-11 items-center gap-1.5 rounded-lg text-sm font-bold text-amber-800 underline-offset-4 hover:text-amber-950 hover:underline"
        >
          {{ spotlight.items.length > SPOTLIGHT_LIMIT ? `See all ${spotlight.items.length}` : 'Open in schedule' }}
          <AppIcon name="arrow-right" :size="16" />
        </NuxtLink>
      </div>

      <ul v-if="spotlight.items.length" class="grid gap-4 lg:grid-cols-2">
        <li v-for="interruption in spotlight.items.slice(0, SPOTLIGHT_LIMIT)" :key="interruptionKey(interruption)">
          <InterruptionCard :interruption="interruption" :show-date="!spotlight.isToday" />
        </li>
      </ul>

      <div
        v-else
        class="flex justify-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-900"
      >
        <AppIcon name="check" :size="24" class="mt-0.5 text-emerald-700" />
        <p>No upcoming interruptions are listed. We'll show them here as soon as VECO posts them.</p>
      </div>
    </section>

    <section
      v-else-if="!errorMessage"
      class="flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-emerald-900"
    >
      <AppIcon name="check" :size="24" class="mt-0.5 text-emerald-700" />
      <p>No service interruptions are currently listed.</p>
    </section>
  </div>
</template>

<script setup>
import rotationalLogo from '~/assets/images/rotational-logo.png'

definePageMeta({
  layout: 'main-layout',
  path: '/',
})

const SPOTLIGHT_LIMIT = 4

const interruptionsStore = useInterruptionsStore()
const { items, isRefreshing, errorMessage } = storeToRefs(interruptionsStore)

const { status } = await useAsyncData(
  'all-interruptions',
  () => interruptionsStore.fetchAll(),
)

const todayKey = manilaDateKey()
const tomorrowKey = shiftDateKey(todayKey, 1)

const isInitialLoading = computed(() => status.value === 'pending' && items.value.length === 0)
const todayItems = computed(() => items.value.filter((item) => occursOn(item, todayKey)))
const tomorrowItems = computed(() => items.value.filter((item) => occursOn(item, tomorrowKey)))

const stats = computed(() => {
  const dayCount = new Set(items.value.map((item) => item.date_start)).size

  return [
    {
      label: 'Today',
      value: todayItems.value.length,
      caption: formatDateKey(todayKey, { weekday: false }),
      to: { path: '/schedule', query: { date: todayKey } },
    },
    {
      label: 'Tomorrow',
      value: tomorrowItems.value.length,
      caption: formatDateKey(tomorrowKey, { weekday: false }),
      to: { path: '/schedule', query: { date: tomorrowKey } },
    },
    {
      label: 'All listed',
      value: items.value.length,
      caption: `Across ${dayCount} ${dayCount === 1 ? 'day' : 'days'}`,
      to: '/schedule',
    },
  ]
})

const spotlight = computed(() => {
  if (todayItems.value.length) {
    return {
      isToday: true,
      title: 'Happening today',
      subtitle: formatDateKey(todayKey),
      items: todayItems.value,
      to: { path: '/schedule', query: { date: todayKey } },
    }
  }

  const [nextGroup] = groupByDate(items.value.filter((item) => item.date_start > todayKey))
  if (nextGroup) {
    return {
      isToday: false,
      title: 'Next scheduled interruptions',
      subtitle: `Nothing is listed for today. The next ones are on ${nextGroup.label}.`,
      items: nextGroup.items,
      to: { path: '/schedule', query: { date: nextGroup.date } },
    }
  }

  return {
    isToday: false,
    title: 'No upcoming interruptions',
    subtitle: 'Nothing is listed for today or the days ahead.',
    items: [],
    to: '/schedule',
  }
})

async function retry() {
  try {
    await interruptionsStore.fetchAll()
  } catch {
    // The store exposes the API error through errorMessage.
  }
}
</script>
