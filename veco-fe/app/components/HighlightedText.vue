<template>
  <template v-for="(part, index) in parts" :key="index">
    <mark v-if="part.match" class="rounded-sm bg-amber-200 px-0.5 text-stone-950">{{ part.text }}</mark>
    <template v-else>{{ part.text }}</template>
  </template>
</template>

<script setup>
const props = defineProps({
  text: { type: String, default: '' },
  query: { type: String, default: '' },
})

const parts = computed(() => highlightParts(props.text, props.query))
</script>
