import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2026-09-18',
  css: ['~/assets/css/main.css'],
  devtools: { enabled: true },
  modules: [
    '@pinia/nuxt',
    '@nuxt/eslint',
  ],
  runtimeConfig: {
    public: {
      apiBase: '',
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
})