<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold uppercase tracking-wide ring-1 ring-inset"
    :class="TONE_CLASSES[tone]"
  >
    <span
      class="size-1.5 rounded-full bg-current"
      :class="{ 'animate-pulse': tone === 'ongoing' }"
      aria-hidden="true"
    />
    {{ label }}
  </span>
</template>

<script setup>
const props = defineProps({
  status: { type: String, default: '' },
})

const TONE_CLASSES = {
  ongoing: 'bg-red-50 text-red-800 ring-red-600/25',
  upcoming: 'bg-sky-50 text-sky-800 ring-sky-600/25',
  done: 'bg-emerald-50 text-emerald-800 ring-emerald-600/25',
  cancelled: 'bg-stone-100 text-stone-700 ring-stone-500/25',
  neutral: 'bg-amber-50 text-amber-900 ring-amber-600/25',
}

const tone = computed(() => statusTone(props.status))
const label = computed(() => props.status?.trim() || 'Scheduled')
</script>
