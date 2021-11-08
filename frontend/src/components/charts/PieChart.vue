<template>
  <apexchart
    ref="graph"
    :type="options.piechart.type"
    :width="200"
    :height="200"
    :options="chartOptions"
    :series="series"
  />
</template>

<script>
import VueApexCharts from "vue-apexcharts"
import statsMixin from "@/mixins/statsMixin"

export default {
  components: {
    apexchart: VueApexCharts
  },
  mixins: [statsMixin],
  props: {
    title: {
      type: String,
      required: true
    },
    height: {
      type: String,
      default: "400"
    },
    queries: {
      type: Array,
      required: true
    },
    labels: {
      type: Array,
      required: true
    },
    options: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    chartOptions: {},
    dataCollection: {},
    series: [],
    loaded: false
  }),

  beforeMount() {
    this.chartOptions = this.buildOptions()
    this.loaded = true
  },

  methods: {
    updateSeries(series) {
      this.$refs.graph.updateSeries(series)
    },

    updateOptions() {
      this.$refs.graph.updateOptions(this.buildOptions())
    },

    buildOptions() {
      const finalOptions = {
        labels: this.labels,
        title: {
          text: this.title,
          align: "left"
        },
        colors: [],
        responsive: [
          {
            breakpoint: 480,
            options: {
              legend: {
                show: this.options.legend.display,
                position: this.options.legend.position
              }
            }
          }
        ]
      }

      for (const query of this.queries) {
        finalOptions.colors.push(query.color)
      }

      return finalOptions
    }
  }
}
</script>
