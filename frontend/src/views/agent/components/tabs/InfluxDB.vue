<template>
  <div>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Average query duration") }}
          </div>

          <h2 class="text-center" v-html="queryDurationNs" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Active Queries") }}
          </div>

          <h2 class="text-center" v-html="activeQueries" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Number of measurements") }}
          </div>

          <h2 class="text-center" v-html="numMeasurements" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius stats-widget" shadow="always" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Number of series") }}
          </div>

          <h2 class="text-center" v-html="numSeries" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="10" style="margin: 10px 0">
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("HTTP Queries") }}
          </div>
          <time-chart ref="graph_influxdb_httpd_queryReq" :options="optionsFormatNumbers" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("HTTP Errors") }}
          </div>
          <time-chart ref="graph_influxdb_httpd_clientError" :options="optionsFormatNumbers" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius stats-widget" shadow="always" style="margin-bottom: 10px">
          <div slot="header">
            {{ $t("Write points") }}
          </div>
          <time-chart ref="graph_influxdb_httpd_pointsWrittenOK" :options="optionsFormatNumbers" :date-range="dateRange" />
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

    activeQueries: 0,
    queryDurationNs: "",
    numMeasurements: 0,
    numSeries: 0,

    last: {
      influxdb_queryExecutor: {
        fields: ["queryDurationNs", "activeQueries"]
      },
      influxdb_database: {
        fields: ["numMeasurements", "numSeries"]
      }
    },
    max: {},
    time: [{
      measurement: "influxdb_httpd",
      fields: ["queryReq"]
    }, {
      measurement: "influxdb_httpd",
      fields: ["clientError", "serverError"]
    }, {
      measurement: "influxdb_httpd",
      fields: ["pointsWrittenOK", "pointsWrittenFail"]
    }]
  }),

  methods: {
    updateData(graph_type, data) {
      if (graph_type === "last") {
        this.is_loading_stats = false
        this.queryDurationNs = parseFloat(data["influxdb_queryExecutor.queryDurationNs"] / 1000000000).toFixed(2) + "s"
        this.activeQueries = data["influxdb_queryExecutor.activeQueries"]
        this.numMeasurements = data["influxdb_database.numMeasurements"]
        this.numSeries = data["influxdb_database.numSeries"]
      } else if (graph_type === "max") {
        this.is_loading_max = false
      } else if (graph_type === "time") {
        this.is_loading_time = false
        for (const element of this.time) {
          const series = this.formatTimeSeries(element, data)
          this.$refs[`graph_${element.measurement}_${element.fields[0]}`].updateSeries(series)
          if (element.colors) { this.$refs[`graph_${element.measurement}_${element.fields[0]}`].updateColors(element.colors) }
        }
      }
    }
  }
})
</script>
