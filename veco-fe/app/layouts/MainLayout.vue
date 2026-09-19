<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <NavigationHeader>
      <NuxtLink to="/" class="flex items-center gap-3 font-semibold text-slate-950">
        <img
          :src="rotationalLogo"
          alt="VECO Outage Watch"
          width="44"
          height="44"
          class="size-11 object-contain"
        >
      </NuxtLink>

      <div class="flex items-center gap-2 text-sm font-medium">
        <NuxtLink to="/schedule" class="rounded-lg px-3 py-2 text-gray-600 hover:bg-blue-50">
          Schedule
        </NuxtLink>
      </div>
    </NavigationHeader>

    <main class="px-4 py-6 sm:px-6 lg:px-6 lg:py-8">
      <slot />
    </main>
  </div>
</template>

<script setup>
import rotationalLogo from '~/assets/images/rotational-logo.png'

</script>
