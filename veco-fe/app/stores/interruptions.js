export const useInterruptionsStore = defineStore('interruptions', {
  state: () => ({
    items: [],
    meta: null,
    isRefreshing: false,
    errorMessage: '',
    filters: {
      search: '',
      category: 'all',
      date: '',
    },
  }),

  getters: {
    filteredItems(state) {
      const search = state.filters.search.trim().toLowerCase()
      const selectedCategory = state.filters.category
      const selectedDate = state.filters.date

      return state.items.filter((interruption) => {
        const category = interruption.category?.toLowerCase() || ''
        const matchesCategory =
          selectedCategory === 'all' ||
          (selectedCategory === 'scheduled' && category.includes('scheduled')) ||
          (selectedCategory === 'rotational' &&
            (category.includes('rotational') || category.includes('brownout')))

        const matchesDate =
          !selectedDate ||
          (interruption.date_start <= selectedDate && interruption.date_end >= selectedDate)

        const searchableText = [
          interruption.date_label,
          interruption.time,
          interruption.purpose,
          interruption.areas_affected,
          interruption.category,
          interruption.status,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()

        return matchesCategory && matchesDate && (!search || searchableText.includes(search))
      })
    },

    hasActiveFilters(state) {
      return Boolean(
        state.filters.search || state.filters.category !== 'all' || state.filters.date,
      )
    },
  },

  actions: {
    setResponse(response) {
      this.items = Array.isArray(response?.data) ? response.data : []
      this.meta = response?.meta ?? null
      this.errorMessage = ''
    },

    setError(message) {
      this.errorMessage = message || 'Unable to load the interruption calendar.'
    },

    resetFilters() {
      this.filters.search = ''
      this.filters.category = 'all'
      this.filters.date = ''
    },

    async fetchAll() {
      const config = useRuntimeConfig()
      this.isRefreshing = true
      this.errorMessage = ''

      try {
        const response = await $fetch('/api/v1/interruptions/', {
          baseURL: config.public.apiBase,
        })
        this.setResponse(response)
        return response
      } catch (error) {
        this.setError(error?.data?.message || error?.message)
        throw error
      } finally {
        this.isRefreshing = false
      }
    },
  },
})
