<template>
  <div class="flex min-h-screen flex-col bg-stone-50 text-stone-900">
    <a
      href="#main-content"
      class="sr-only rounded-lg bg-white px-4 py-3 font-semibold text-stone-950 shadow-lg focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60]"
    >
      Skip to main content
    </a>

    <NavigationHeader>
      <NuxtLink to="/" class="flex min-h-11 items-center gap-3 rounded-lg">
        <img
          :src="rotationalLogo"
          alt=""
          width="40"
          height="40"
          class="size-10 object-contain"
        >
        <span class="leading-tight">
          <span class="block text-base font-extrabold tracking-tight text-stone-950">VECO Outage Watch</span>
          <span class="hidden text-xs font-medium text-stone-600 sm:block">Power interruption schedules</span>
        </span>
      </NuxtLink>

      <ul class="flex items-center gap-1 text-sm font-semibold">
        <li v-for="link in navLinks" :key="link.to">
          <NuxtLink
            :to="link.to"
            class="inline-flex min-h-11 items-center rounded-lg px-3 transition-colors duration-200 sm:px-4"
            :class="
              isActive(link.to)
                ? 'bg-amber-50 text-amber-900 ring-1 ring-inset ring-amber-200'
                : 'text-stone-600 hover:bg-stone-100 hover:text-stone-950'
            "
          >
            {{ link.label }}
          </NuxtLink>
        </li>
      </ul>
    </NavigationHeader>

    <!-- MAIN -->
    <main
      id="main-content"
      tabindex="-1"
      class=" flex-1 focus:outline-none"
    >
      <slot />
    </main>

    <footer class="border-t border-stone-200 bg-white">
      <div class="flex justify-center px-4 py-6 text-sm leading-6 text-stone-600 sm:px-6 lg:px-8">
        Schedules come from VECO's public interruption calendar and may change without notice.
        Times are in Philippine Standard Time.
      </div>
    </footer>
  </div>
</template>

<script setup>
import rotationalLogo from '~/assets/images/rotational-logo.png'

const route = useRoute()

const navLinks = [
  { label: 'Home', to: '/' },
  { label: 'Schedule', to: '/schedule' },
]

function isActive(path) {
  return route.path === path
}
</script>
