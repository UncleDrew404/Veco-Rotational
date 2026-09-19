<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
import rotationalLogo from '~/assets/images/rotational-logo.png'

useHead({
  link: [
    {
      rel: 'icon',
      type: 'image/png',
      href: rotationalLogo,
    },
  ],
})
</script>
