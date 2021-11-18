<template>
  <div>
    <el-row :gutter="10" style="margin: 10px 0">
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Requests per second") }}
          </div>
          <time-chart ref="graph_haproxy_req_rate" :options="optionsFormatNumbers" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Messages") }}
          </div>
          <time-chart ref="graph_haproxy_http_response.1xx" :options="optionsFormatNumbers" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Average response time") }}
          </div>
          <time-chart ref="graph_haproxy_rtime" :options="optionsFormatNumbers" :date-range="dateRange" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import statsMixin from "@/mixins/statsMixin"
import dashMixin from "@/mixins/dashMixin"
import renderMixin from "@/mixins/renderMixin"
import { defineComponent } from "@vue/composition-api"
import TimeChart from "@/components/charts/TimeChart.vue"

export default defineComponent({
  components: { TimeChart },
  mixins: [dashMixin, statsMixin, renderMixin],

  props: {
    agent_id: {
      type: String,
      required: true
    }
  },

  data: (vm) => ({
    is_loading_stats: true,
    is_loading_max: true,
    is_loading_time: true,

    last: {},
    max: {},
    time: [{
      measurement: "haproxy",
      fields: ["req_rate"]
    }, {
      measurement: "haproxy",
      fields: ["http_response.1xx", "http_response.2xx", "http_response.3xx", "http_response.4xx", "http_response.5xx"]
    }, {
      measurement: "haproxy",
      fields: ["rtime"]
    }]
  }),

  methods: {
    updateData(graph_type, data) {
      if (graph_type === "last") {
        this.is_loading_stats = false
      } else if (graph_type === "max") {
        this.is_loading_max = false
      } else if (graph_type === "time") {
        this.is_loading_time = false
        for (const element of this.time) {
          const series = this.formatTimeSeries(element, data)
          console.log(series)
          this.$refs[`graph_${element.measurement}_${element.fields[0]}`].updateSeries(series)
          if (element.colors) { this.$refs[`graph_${element.measurement}_${element.fields[0]}`].updateColors(element.colors) }
        }
      }
    }
  }
})
</script>
