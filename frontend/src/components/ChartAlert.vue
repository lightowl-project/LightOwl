<template>
  <div>
    <el-skeleton style="width: 100%" :loading="is_loading" animated>
      <template slot="template">
        <el-skeleton-item
          variant="image"
          style="width: 100%; height: 240px;"
        />
      </template>
    </el-skeleton>
    <apexchart
      v-if="!is_loading"
      ref="graph"
      type="area"
      :height="200"
      :options="chartOptions"
      :series="series"
    />
  </div>
</template>

<script>
import moment from "moment"
import request from "@/utils/request"
import statsMixin from "@/mixins/statsMixin"
import VueApexCharts from "vue-apexcharts"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  components: { apexchart: VueApexCharts },
  mixins: [statsMixin],

  props: {
    alert_id: {
      type: String,
      required: true
    }
  },

  data: () => ({
    is_loading: false,
    chartOptions: {
      legend: { show: false },
      dataLabels: {
        enabled: false
      },
      colors: ["#F49B51"],
      chart: { toolbar: { show: false }},
      xaxis: {
        type: "datetime",
        labels: {
          formatter: (value) => {
            moment.locale()
            return moment.utc(value).local().format("lll")
          }
        }
      }
    },
    series: []
  }),

  mounted() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.is_loading = true
      request.get(`/api/v1/alerts/${this.alert_id}/graph`).then((response) => {
        const data = this.formatValues(response.data.data)

        this.is_loading = false
        this.$nextTick(() => {
          this.$refs.graph.updateSeries([
            { name: response.data.field, data: data }
          ])
        })
      })
    }
  }
})
</script>
