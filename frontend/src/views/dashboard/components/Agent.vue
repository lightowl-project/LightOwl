<template>
  <div
    ref="card"
    :style="renderAgentStyle()"
    class="card-agent"
  >
    <div v-if="agent" style="">
      {{ agent.ip_address }} - {{ agent.hostname }}

      <el-badge style="float: right" is-dot :type="badgeType" class="item">
        {{ $t('Last seen') }}: {{ renderLastSeen(agent.last_seen) }}
      </el-badge>
    </div>

    <el-row v-if="agent" :gutter="0" class="mt-1">
      <table class="table-agent">
        <tbody>
          <tr>
            <td style="width: 8%">{{ $t('CPU') }}</td>
            <td>
              <el-progress :stroke-width="15" stroke-linecap="square" :color="customColors" :percentage="agent_data.cpu" />
            </td>
          </tr>
          <tr>
            <td style="width: 8%">{{ $t('RAM') }}</td>
            <td>
              <el-progress :stroke-width="15" stroke-linecap="square" :color="customColors" :percentage="agent_data.mem" />
            </td>
          </tr>
          <tr>
            <td style="width: 8%">{{ $t('Load') }}</td>
            <td>
              <b><el-tag type="info" effect="dark">{{ agent_data.load }}</el-tag></b>
            </td>
          </tr>
        </tbody>
      </table>
    </el-row>
    <el-row :gutter="10" class="mt-1">
      <alert-info :alerts="alerts" :agent_id="agent_id" />
    </el-row>
  </div>
</template>

<script>
import moment from "moment"
import request from "@/utils/request"
import AlertInfo from "./AlertInfo.vue"
import renderMixin from "@/mixins/renderMixin"
import { defineComponent } from "@vue/composition-api"

export default defineComponent({
  mixins: [renderMixin],

  components: {
    AlertInfo
  },

  props: {
    agent_id: {
      type: String,
      required: true
    }
  },

  computed: {
    sizeAlerts() {
      if (this.alerts.length) {
        return 10
      }

      return 0
    },

    sizeCpuRamLoad() {
      if (this.alerts.length) {
        return 14
      }

      return 24
    }
  },

  data: () => ({
    alerts: [],
    agent: null,
    interval: null,
    badgeType: "success",
    agent_data: {
      cpu: 0,
      mem: 0,
      load: 0
    },
    customColors: [
      { color: "#5cb87a", percentage: 40 },
      { color: "#e6a23c", percentage: 60 },
      { color: "#f56c6c", percentage: 80 },
      { color: "#f56c6c", percentage: 100 }
    ]
  }),

  beforeMount() {
    this.getAgent()
  },

  mounted() {
    window.onresize = () => {
      this.$forceUpdate()
    }
  },

  beforeDestroy() {
    if (this.interval) { clearInterval(this.interval) }
  },

  methods: {
    renderLastSeen(date) {
      const last_seen = moment.utc(date)
      let diff = moment.utc().diff(last_seen, "minutes")
      if (diff < 60) return `${diff} minutes ago`

      diff = moment.utc().diff(last_seen, "hours")
      if (diff < 24) return `${diff} hours ago`

      diff = moment.utc().diff(last_seen, "days")
      return `${diff} days ago`
    },

    renderAgentStyle() {
      const style = {
        height: "100%",
        "background-color": "#304156",
        color: "#fff",
        padding: "0px"
      }

      // if (this.agent) {
      //   const last_seen = moment.utc(this.agent.last_seen)
      //   const now = moment.utc()

      //   if (now.diff(last_seen, "minutes") > 5) {
      //     style["background-color"] = "#F49B51"
      //     style["color"] = "#fff"
      //   }
      // }

      return style
    },

    renderHeight(graph_type) {
      const element = this.$refs.card
      const cardHeight = element.clientHeight
      if (graph_type === "load") return cardHeight - 20
      else return cardHeight
    },

    getAgent() {
      request.get(`/api/v1/agents/${this.agent_id}`, { params: { alerts: true }}).then((response) => {
        this.agent = response.data
        this.alerts = response.data.alerts
        this.interval = setInterval(() => {
          this.fetchAgentData()
        }, 10000)
        this.fetchAgentData()
        this.fetchStats()
      })
    },

    async fetchAgentData() {
      const response_agent = await request.get(`/api/v1/agents/${this.agent_id}`, { params: { alerts: true }})
      this.agent.last_seen = response_agent.data.last_seen
      this.alerts = response_agent.data.alerts

      const last_seen = moment.utc(this.agent.last_seen)
      const now = moment.utc()

      if (now.diff(last_seen, "minutes") > 5) {
        this.badgeType = "warning"
      } else {
        this.badgeType = "success"
      }
    },

    async fetchStats() {
      const data_to_fetch = {
        "cpu": "usage_idle",
        "mem": "used_percent",
        "system": "load1"
      }

      const params = []
      for (const [k, v] of Object.entries(data_to_fetch)) {
        params.push({
          agent_id: this.agent_id,
          measurement: k,
          field: v,
          agg: "last",
          interval: "1m",
          graph_type: "last"
        })
      }

      let cpu_usage, mem_usage, load

      const response = await request.post("/api/v1/dashboard/query", params)

      try {
        cpu_usage = 100 - parseInt(response.data[`${this.agent_id}.cpu.usage_idle`].series[0].values[0][1])
      } catch (err) {
        cpu_usage = 0
      }

      try {
        mem_usage = parseInt(response.data[`${this.agent_id}.mem.used_percent`].series[0].values[0][1])
      } catch (err) {
        mem_usage = 0
      }

      try {
        load = parseInt(response.data[`${this.agent_id}.system.load1`].series[0].values[0][1])
      } catch (err) {
        load = 0
      }

      this.agent_data = {
        cpu: cpu_usage,
        mem: mem_usage,
        load: load
      }
    }
  }
})
</script>

<style>
.card-agent {
  padding: 10px !important;
  box-shadow: 0 2px 12px 0 rgb(0 0 0 / 10%);
}

.table-agent{
  width: 100%;
}

.table-agent tbody{
  line-height: 30px;
}

.el-progress__text{
  color: #fff !important;
}
</style>
