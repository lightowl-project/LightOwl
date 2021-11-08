<template>
  <apexchart
    ref="graph"
    v-loading="is_loading"
    :type="type"
    :height="height"
    :options="chartOptions"
    :series="series"
  />
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
    agent_ids: {
      type: Array,
      required: true
    },
    collector: {
      type: Object,
      required: true
    },
    type: {
      type: String,
      default: "area"
    },
    height: {
      type: String,
      default: "200"
    },
    agg: {
      type: String,
      default: "mean"
    }
  },

  data: () => ({
    is_loading: false,
    chartOptions: {
      legend: { show: true },
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
    series: [],
    agents: {}
  }),

  mounted() {
    this.fetchData()
  },
  methods: {
    async fetchAgents(agent_id) {
      const response = await request.get(`/api/v1/agents/${agent_id}`)
      return response.data
    },

    fetchData() {
      const startDate = moment.utc().startOf("day")
      const endDate = moment.utc()

      this.is_loading = true

      const params = []
      for (const agent_id of this.agent_ids) {
        params.push({
          measurement: this.collector.measurement,
          field: this.collector.field,
          agent_id: agent_id,
          agg: this.agg,
          date_start: startDate.format("YYYY-MM-DD HH:mm:ss"),
          date_end: endDate.format("YYYY-MM-DD HH:mm:ss"),
          graph_type: "time",
          interval: "1h"
        })
      }

      request.post("/api/v1/dashboard/query", params).then(async(response) => {
        this.is_loading = false
        const datasets = []

        for (const param of params) {
          const tmp = response.data[`${param.agent_id}.${param.measurement}.${param.field}`].series[0].values
          const data = this.formatValues(tmp)

          const agent = await this.fetchAgents(param.agent_id)
          datasets.push({
            name: agent.ip_address,
            data: data
          })
        }
        this.$refs.graph.updateSeries(datasets)
      })
    }
  }
})
</script>
