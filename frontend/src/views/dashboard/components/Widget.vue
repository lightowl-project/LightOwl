<template>
  <el-card
    v-if="agent"
    class="box-card wrapper"
    shadow="always"
    :body-style="{
      position: 'absolute',
      padding: 0,
      top: '40px',
      bottom: 0,
      right: 0,
      left: 0,
    }"
  >
    <div slot="header">
      <i :class="renderOSIcon(agent.os)" />
      {{ agent.ip_address }} - {{ agent.hostname }}
      <span v-if="editMode" class="widget-button">
        <el-popconfirm
          :title="$t('Are you sure to delete this ?')"
          @confirm="$emit('deleteWidget', index)"
        >
          <el-button
            slot="reference"
            plain
            type="danger"
            size="mini"
            style="float: right; padding: 5px; margin-left: 5px"
          >
            <i class="fa fa-trash" />
          </el-button>
        </el-popconfirm>
        <el-button
          type="primary"
          size="mini"
          plain
          style="float: right; padding: 5px"
          @click="$emit('editWidget', widgetId)"
        >
          <i class="fa fa-edit" />
        </el-button>
      </span>
    </div>
    <graph
      :is="mapping_chart[graph_type]"
      ref="graph"
      height="100%"
      class="wrapper"
      :title="title"
      :options="options"
      @zoom="zoom"
    />
  </el-card>
</template>

<script>
import moment from "moment"
import request from "@/utils/request"
import statsMixin from "@/mixins/statsMixin"
import renderMixin from "@/mixins/renderMixin"
import TextChart from "@/components/charts/Text.vue"
import PieChart from "@/components/charts/PieChart.vue"
import TimeChart from "@/components/charts/TimeChart.vue"
import GaugeChart from "@/components/charts/GaugeChart.vue"

export default {
  components: { TimeChart, PieChart, TextChart, GaugeChart },
  mixins: [renderMixin, statsMixin],
  props: {
    widgetId: {
      type: String,
      required: true
    },
    index: {
      type: Number,
      required: true
    },
    interval: {
      type: String,
      required: true
    },
    refresh: {
      type: Number,
      default: 10000
    },
    dateRange: {
      type: Object,
      required: true
    },
    selectedDate: {
      type: String,
      required: true
    },
    editMode: {
      type: Boolean,
      default: false
    }
  },

  data: () => ({
    is_loading: true,
    mapping_chart: {
      time: "TimeChart",
      pie: "PieChart",
      text: "TextChart",
      gauge: "GaugeChart"
    },
    title: "",
    options: {},
    agent: null,
    agent_id: null,
    measurement: null,
    field: null,
    graph_type: ""
  }),

  watch: {
    interval() {
      this.fetchData()
    },

    refresh() {
      clearInterval(this.interval_refresh)
      this.setInterval()
    },

    dateRange() {
      this.fetchData()
    },

    selectedDate() {
      this.fetchData()
    }
  },

  beforeMount() {
    this.init()
  },

  mounted() {
    this.setInterval()
  },

  beforeDestroy() {
    clearInterval(this.interval_refresh)
  },

  methods: {
    zoom(params) {
      this.$emit("zoom", params)
    },
    init() {
      this.is_loading = true

      request
        .get(`/api/v1/dashboard/widget/${this.widgetId}`)
        .then((response) => {
          this.graph_type = response.data.graph_type
          this.agent_id = response.data.agent

          this.getAgent()

          this.measurement = response.data.measurement
          this.field = response.data.field
          this.options = response.data.options
          this.options.responsive = true
          this.options.maintainAspectRatio = false

          switch (this.graph_type) {
            case "gauge":
              this.datacollection = 0
              break
            case "text":
              this.datacollection = 0
              break
            default:
              this.datacollection = { labels: [], datasets: [] }
              break
          }

          this.fetchData()
        })
    },

    getAgent() {
      request.get(`/api/v1/agents/${this.agent_id}`).then((response) => {
        this.agent = response.data
      })
    },

    setInterval() {
      this.interval_refresh = setInterval(() => {
        this.fetchData()
      }, this.refresh)
    },

    fetchData() {
      this.is_loading = true
      let interval = this.interval

      let startDate = moment.utc(this.dateRange.startDate)
      let endDate = moment.utc(this.dateRange.endDate)
      if (this.selectedDate !== "custom") {
        const dates = this.getRelativeDate(this.selectedDate)
        startDate = dates.startDate
        endDate = dates.endDate
      }

      if (interval === "auto") {
        interval = this.calculateInterval({
          startDate: startDate,
          endDate: endDate
        })
      }

      const params = {
        agent_id: this.agent_id,
        measurement: this.measurement,
        field: this.field,
        date_start: startDate.format("YYYY-MM-DD HH:mm:ss"),
        date_end: endDate.format("YYYY-MM-DD HH:mm:ss"),
        graph_type: this.graph_type,
        interval: interval,
        options: this.options
      }

      request.post("/api/v1/dashboard/query", params).then((response) => {
        const data = this.formatDatasets(this.graph_type, response.data)

        this.$refs.graph.updateOptions()
        this.$refs.graph.updateSeries([{ name: "data", data: data }])
        this.is_loading = false
      })
    }
  }
}
</script>

<style scoped>
.wrapper {
  position: relative;
  height: 100%;
  width: 100%;
}
.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both;
}

.widget-button {
  position: absolute;
  z-index: 1;
  top: 5px;
  right: 5px;
}
</style>
