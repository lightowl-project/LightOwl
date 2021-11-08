<template>
  <div>
    <el-skeleton style="width: 100%" :loading="is_loading" animated>
      <template slot="template">
        <el-skeleton-item
          variant="image"
          :style="renderStyle()"
        />
      </template>
    </el-skeleton>
    <apexchart
      v-if="!is_loading"
      ref="graph"
      type="area"
      :height="height"
      :options="chartOptions"
      :series="series"
    />
  </div>
</template>

<script>
import moment from "moment"
import VueApexCharts from "vue-apexcharts"
import statsMixin from "@/mixins/statsMixin"

export default {
  components: {
    apexchart: VueApexCharts
  },
  mixins: [statsMixin],
  props: {
    height: {
      type: String,
      default: "250"
    },
    options: {
      type: Object,
      required: true
    },
    dateRange: {
      type: Object,
      required: true
    }
  },
  data: (vm) => ({
    is_loading: true,
    chartOptions: {
      legend: { show: true },
      dataLabels: {
        enabled: false
      },
      chart: {
        toolbar: { show: false },
        events: {
          beforeZoom: vm.beforeZoom
        }
      },
      xaxis: {
        type: "datetime",
        labels: {
          formatter: (value) => {
            const format = vm.formatDate(vm.dateRange)
            return moment.utc(value).format(format)
          }
        }
      }
    },
    series: []
  }),

  beforeMount() {
  },

  mounted() {
    this.chartOptions = Object.assign({}, this.chartOptions, this.options)
  },

  methods: {
    renderStyle() {
      return `width: 100%; height: ${this.height}px;`
    },

    updateColors(colors) {
      this.chartOptions.colors = colors
      this.is_loading = false
      this.$nextTick(() => {
        this.$refs.graph.updateOptions(this.chartOptions)
      })
    },

    updateSeries(series) {
      this.is_loading = false
      this.$nextTick(() => {
        this.$refs.graph.updateSeries(series)
      })
    },

    beforeZoom(chart, { xaxis }) {
      this.$emit("zoom", { start: xaxis.min, end: xaxis.max })
      return false
    }
  }
}
</script>
