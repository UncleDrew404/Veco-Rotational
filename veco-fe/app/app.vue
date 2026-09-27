<template>
  <NuxtLoadingIndicator color="#d97706" :height="3" />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
import rotationalLogo from '~/assets/images/rotational-logo.png'

useHead({
  htmlAttrs: { lang: 'en' },
  titleTemplate: (title) => (title ? `${title} · VECO Outage Watch` : 'VECO Outage Watch'),
  meta: [
    {
      name: 'description',
      content: 'Scheduled power interruptions and rotational brownouts in the VECO service area.',
    },
    { name: 'theme-color', content: '#1c1917' },
  ],
  link: [
    {
      rel: 'icon',
      type: 'image/png',
      href: rotationalLogo,
    },
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
    {
      rel: 'stylesheet',
      href: 'https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700;800&display=swap',
    },
  ],
})
</script>
