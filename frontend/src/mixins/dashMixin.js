const dashMixin = {
  props: {
    dateRange: {
      type: Object,
      required: true
    }
  },
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
