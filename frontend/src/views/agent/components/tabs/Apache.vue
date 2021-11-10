<template>
  <div>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Uptime") }}
          </div>

          <h2 class="text-center" v-html="uptime" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Load") }}
          </div>

          <h2 class="text-center" v-html="load1" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Processes") }}
          </div>

          <h2 class="text-center" v-html="processes" />
        </el-card>
      </el-col>
      <el-col :md="4">
        <el-card v-loading="is_loading_stats" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t("Max Request per Second") }}
          </div>

          <h2 class="text-center" v-html="reqpersec" />
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t('Workers') }}
          </div>

          <time-chart ref="graph_apache_BusyWorkers" :options="{}" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t('Scoreboard') }}
          </div>

          <time-chart ref="graph_apache_scboard_closing" :options="{}" :date-range="dateRange" />
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t('Requests per second') }}
          </div>

          <time-chart ref="graph_apache_ReqPerSec" :options="{}" :date-range="dateRange" />
        </el-card>
      </el-col>
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t('CPU System and User') }}
          </div>

          <time-chart ref="graph_apache_CPUSystem" :options="{}" :date-range="dateRange" />
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10" style="margin: 10px 0;">
      <el-col :md="12">
        <el-card v-loading="is_loading_time" class="no-radius" shadow="hover" :body-style="{padding: 0}">
          <div slot="header">
            {{ $t('Load') }}
          </div>

          <time-chart ref="graph_apache_Load1" :options="{}" :date-range="dateRange" />
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
import GaugeChart from "@/components/charts/GaugeChart.vue"

export default defineComponent({
  components: { GaugeChart, TimeChart },
  mixins: [dashMixin, statsMixin, renderMixin],

  props: {
    agent_id: String,
    required: true
  },

  data: (vm) => ({
    is_loading_max: true,
    is_loading_time: true,
    is_loading_stats: true,

    uptime: "",
    load1: 0,
    processes: 0,
    reqpersec: 0,

    last: {
      apache: {
        fields: ["Uptime", "CPULoad", "Processes"]
      }
    },

    max: {
      apache: {
        fields: ["ReqPerSec"]
      }
    },

    time: [{
      measurement: "apache",
      fields: ["BusyWorkers", "IdleWorkers"]
    }, {
      measurement: "apache",
      fields: ["scboard_closing", "scboard_dnslookup", "scboard_finishing", "scboard_idle_cleanup", "scboard_keepalive", "scboard_logging", "scboard_open", "scboard_reading", "scboard_sending", "scboard_starting", "scboard_waiting"]
    }, {
      measurement: "apache",
      fields: ["ReqPerSec"]
    }, {
      measurement: "apache",
      fields: ["CPUSystem", "CPUUser", "CPUChildrenSystem", "CPUChildrenUser"]
    }, {
      measurement: "apache",
      fields: ["Load1", "Load15", "Load5"]
    }]
  }),

  methods: {
    updateData(graph_type, data) {
      if (graph_type === "last") {
        this.is_loading_stats = false
        this.uptime = this.renderUPtime(data["apache.Uptime"])
        this.load1 = parseFloat(data["apache.CPULoad"])
        this.processes = data["apache.Processes"]
      } else if (graph_type === "max") {
        this.is_loading_max = false
        this.reqpersec = parseFloat(data["apache.ReqPerSec"])
      } else if (graph_type === "time") {
        this.is_loading_time = false
        for (const element of this.time) {
          const series = this.formatTimeSeries(element, data, element.convert)
          this.$refs[`graph_${element.measurement}_${element.fields[0]}`].updateSeries(series)
          if (element.colors) { this.$refs[`graph_${element.measurement}_${element.fields[0]}`].updateColors(element.colors) }
        }
      }

      this.resize()
    }
  }
})
</script>
