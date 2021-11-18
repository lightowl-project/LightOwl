const dashMixin = {
  props: {
    dateRange: {
      type: Object,
      required: true
    }
  },

  data: () => ({
    optionsFormatNumbers: {
      yaxis: {
        labels: {
          formatter: (val) => {
            return new Intl.NumberFormat("fr-FR", { notation: "compact" }).format(val)
          }
        }
      }
    }
  }),

  methods: {
    load() {
      this.is_loading_stats = true
      this.is_loading_max = true
      this.is_loading_time = true
    },

    resize() { }
  }
}

export default dashMixin
