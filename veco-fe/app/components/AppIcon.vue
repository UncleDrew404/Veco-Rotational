<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    :width="size"
    :height="size"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
    class="shrink-0"
  >
    <component
      :is="shape[0]"
      v-for="(shape, index) in shapes"
      :key="index"
      v-bind="shape[1]"
    />
  </svg>
</template>

<script setup>
// Paths from Lucide (lucide.dev, ISC license), inlined to avoid an icon dependency.
const ICONS = {
  'alert': [
    ['path', { d: 'm21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3' }],
    ['path', { d: 'M12 9v4' }],
    ['path', { d: 'M12 17h.01' }],
  ],
  'arrow-right': [
    ['path', { d: 'M5 12h14' }],
    ['path', { d: 'm12 5 7 7-7 7' }],
  ],
  'calendar': [
    ['rect', { width: 18, height: 18, x: 3, y: 4, rx: 2 }],
    ['path', { d: 'M16 2v4' }],
    ['path', { d: 'M8 2v4' }],
    ['path', { d: 'M3 10h18' }],
  ],
  'check': [
    ['circle', { cx: 12, cy: 12, r: 10 }],
    ['path', { d: 'm9 12 2 2 4-4' }],
  ],
  'clock': [
    ['circle', { cx: 12, cy: 12, r: 10 }],
    ['path', { d: 'M12 6v6l4 2' }],
  ],
  'external-link': [
    ['path', { d: 'M15 3h6v6' }],
    ['path', { d: 'M10 14 21 3' }],
    ['path', { d: 'M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6' }],
  ],
  'map-pin': [
    ['path', { d: 'M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z' }],
    ['circle', { cx: 12, cy: 10, r: 3 }],
  ],
  'refresh': [
    ['path', { d: 'M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8' }],
    ['path', { d: 'M21 3v5h-5' }],
    ['path', { d: 'M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16' }],
    ['path', { d: 'M8 16H3v5' }],
  ],
  'search': [
    ['circle', { cx: 11, cy: 11, r: 8 }],
    ['path', { d: 'm21 21-4.3-4.3' }],
  ],
  'x': [
    ['path', { d: 'M18 6 6 18' }],
    ['path', { d: 'm6 6 12 12' }],
  ],
  'zap': [
    ['path', { d: 'M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z' }],
  ],
}

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 20 },
})

const shapes = computed(() => ICONS[props.name] || [])
</script>
