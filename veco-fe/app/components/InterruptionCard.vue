<template>
  <article
    class="flex h-full flex-col gap-4 rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-6"
    :class="{ 'border-l-4 border-l-red-600': isOngoing }"
  >
    <div class="flex flex-wrap items-center justify-between gap-2">
      <StatusBadge :status="interruption.status" />
      <span
        v-if="interruption.category"
        class="text-xs font-bold uppercase tracking-wide text-stone-600"
      >
        {{ interruption.category }}
      </span>
    </div>

    <div class="grid gap-1">
      <p v-if="showDate" class="text-sm font-semibold text-amber-800">
        {{ dateLabel }}
      </p>
      <p class="flex items-center gap-2 text-lg font-bold text-stone-950">
        <AppIcon name="clock" class="text-amber-700" />
        <span><span class="sr-only">Time: </span>{{ interruption.time }}</span>
      </p>
    </div>

    <h3 class="text-base font-semibold leading-7 text-stone-800">
      <HighlightedText :text="interruption.purpose" :query="highlight" />
    </h3>

    <div class="border-t border-stone-100 pt-4">
      <p class="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-stone-600">
        <AppIcon name="map-pin" :size="16" />
        Areas affected
      </p>
      <p class="mt-2 text-sm leading-6 text-stone-700">
        <HighlightedText :text="interruption.areas_affected" :query="highlight" />
      </p>
    </div>

    <a
      v-if="interruption.map_url"
      :href="interruption.map_url"
      target="_blank"
      rel="noopener noreferrer"
      class="mt-auto inline-flex min-h-11 items-center gap-1.5 self-start rounded-lg text-sm font-bold text-amber-800 underline-offset-4 transition-colors duration-200 hover:text-amber-950 hover:underline"
    >
      View outage map
      <AppIcon name="external-link" :size="16" />
      <span class="sr-only">(opens in a new tab)</span>
    </a>
  </article>
</template>

<script setup>
const props = defineProps({
  interruption: { type: Object, required: true },
  highlight: { type: String, default: '' },
  showDate: { type: Boolean, default: false },
})

const isOngoing = computed(() => statusTone(props.interruption.status) === 'ongoing')
const dateLabel = computed(
  () => formatDateKey(props.interruption.date_start) || props.interruption.date_label,
)
</script>
